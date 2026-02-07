from __future__ import annotations

from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from datetime import date as date_type
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from ..models import (
    FeeTransaction,
    Member,
    AcademicYear,
    FeeInstallment,
    FeePaymentReceipt,
    FeePaymentAllocation,
    LateFeePolicy,
    StudentConcession,
)


@dataclass(frozen=True)
class PaymentResult:
    legacy_fee_tx: FeeTransaction
    receipt: FeePaymentReceipt


class FinanceService:
    @staticmethod
    def _parse_decimal(value) -> Decimal:
        if isinstance(value, Decimal):
            return value
        try:
            return Decimal(str(value))
        except (InvalidOperation, TypeError, ValueError):
            return Decimal('0')

    @staticmethod
    def _current_academic_year(school_id: int) -> AcademicYear | None:
        return AcademicYear.objects.filter(school_id=school_id, is_active=True).order_by('-start_date').first()

    @staticmethod
    def _quarter_for(d: date_type) -> str:
        m = d.month
        if m in (4, 5, 6):
            return 'Q1'
        if m in (7, 8, 9):
            return 'Q2'
        if m in (10, 11, 12):
            return 'Q3'
        return 'Q4'

    @staticmethod
    def _late_fee_for(installment: FeeInstallment, as_of: date_type) -> Decimal:
        policy = LateFeePolicy.objects.filter(school=installment.school, is_active=True).first()
        if not policy:
            return Decimal('0')
        if as_of <= installment.due_date:
            return Decimal('0')
        overdue_days = (as_of - installment.due_date).days
        if overdue_days <= int(policy.grace_days or 0):
            return Decimal('0')
        billable_days = overdue_days - int(policy.grace_days or 0)
        fee = Decimal(policy.per_day_amount or 0) * Decimal(billable_days)
        cap = Decimal(policy.cap_amount or 0)
        if cap and fee > cap:
            return cap
        return fee

    @staticmethod
    def _discount_for(student: Member) -> Decimal:
        """
        Sum active concessions. Percent concessions are applied on fee_total (legacy basis).
        """
        total = Decimal('0')
        qs = StudentConcession.objects.select_related('discount').filter(
            school=student.school,
            student=student,
            is_active=True,
            discount__is_active=True,
        )
        for sc in qs:
            d = sc.discount
            if d.discount_type == 'Percent':
                total += (Decimal(student.fee_total or 0) * Decimal(d.value or 0)) / Decimal('100')
            else:
                total += Decimal(d.value or 0)
        return total

    @staticmethod
    def ensure_quarterly_installments(student: Member, as_of: date_type | None = None) -> None:
        """
        Creates/updates 4 quarterly installments for the active academic year.
        Principal is derived from legacy Member.fee_total (backward-compatible).
        """
        as_of = as_of or timezone.now().date()
        ay = FinanceService._current_academic_year(student.school_id)
        if not ay:
            return

        annual = Decimal(student.fee_total or 0)
        per_q = (annual / Decimal('4')) if annual else Decimal('0')
        discount_total = FinanceService._discount_for(student)
        discount_per_q = (discount_total / Decimal('4')) if discount_total else Decimal('0')

        due_dates = {
            'Q1': ay.start_date,
            'Q2': date_type(ay.start_date.year, min(ay.start_date.month + 3, 12), ay.start_date.day),
            'Q3': date_type(ay.start_date.year, min(ay.start_date.month + 6, 12), ay.start_date.day),
            'Q4': date_type(ay.start_date.year, min(ay.start_date.month + 9, 12), ay.start_date.day),
        }

        for q in ('Q1', 'Q2', 'Q3', 'Q4'):
            inst, _ = FeeInstallment.objects.get_or_create(
                school=student.school,
                student=student,
                academic_year=ay,
                quarter=q,
                defaults={
                    'due_date': due_dates[q],
                    'principal_amount': per_q,
                    'discount_amount': discount_per_q,
                    'late_fee_amount': Decimal('0'),
                    'paid_amount': Decimal('0'),
                    'status': 'Due',
                },
            )
            inst.late_fee_amount = FinanceService._late_fee_for(inst, as_of)
            inst.discount_amount = discount_per_q
            inst.save(update_fields=['late_fee_amount', 'discount_amount'])

    @staticmethod
    def allocate_receipt(receipt: FeePaymentReceipt, as_of: date_type | None = None) -> None:
        """
        Allocates receipt amount to installments (oldest due first).
        """
        as_of = as_of or timezone.now().date()
        student = receipt.student
        FinanceService.ensure_quarterly_installments(student, as_of=as_of)

        installments = FeeInstallment.objects.filter(
            school=receipt.school,
            student=student,
        ).order_by('due_date', 'id')

        remaining = Decimal(receipt.amount or 0)
        for inst in installments:
            if remaining <= 0:
                break
            inst.late_fee_amount = FinanceService._late_fee_for(inst, as_of)
            inst.save(update_fields=['late_fee_amount'])
            inst_remaining = Decimal(inst.remaining or 0)
            if inst_remaining <= 0:
                continue
            alloc = remaining if remaining <= inst_remaining else inst_remaining
            FeePaymentAllocation.objects.create(receipt=receipt, installment=inst, allocated_amount=alloc)
            inst.paid_amount = F('paid_amount') + alloc
            inst.save(update_fields=['paid_amount'])
            remaining -= alloc

        # Update installment statuses
        for inst in installments:
            inst.refresh_from_db()
            if inst.paid_amount >= inst.net_due and inst.net_due > 0:
                inst.status = 'Paid'
            elif inst.paid_amount > 0:
                inst.status = 'Partial'
            else:
                inst.status = 'Due'
            inst.save(update_fields=['status'])

    @staticmethod
    def collect_fee(*, school_id: int, student_id: int, amount, mode: str, date: str = None) -> FeeTransaction:
        """
        Collects a fee safely using atomic transactions and F() expressions.
        Prevents race conditions where two admins updating fees simultaneously 
        would overwrite each other's changes.
        """
        if not date:
            date = timezone.now().date()
        amount_dec = FinanceService._parse_decimal(amount)
        if amount_dec <= 0:
            raise ValueError("Amount must be > 0")

        # 1. Start a Database Transaction (All or Nothing)
        with transaction.atomic():
            # Lock the student row so no one else can edit it while we are
            student = Member.objects.select_for_update().get(id=student_id, school_id=school_id)

            # 2. Create the Transaction Record
            fee_tx = FeeTransaction.objects.create(
                student=student,
                amount_paid=amount_dec,
                payment_mode=mode,
                payment_date=date,
                month_year="Current",
                status="Paid"
            )

            # 3. Update Balance using F() Expression (The Magic Fix)
            # Instead of saying "New Balance = 500", we say "New Balance = Old Balance + 500"
            # This happens inside the database, not in Python memory.
            student.fee_paid = F('fee_paid') + amount_dec
            student.save()
            
            # Reload to get the actual decimal value back for display if needed
            student.refresh_from_db()

            # ✅ Finance Engine v2: dual-write receipt + allocations
            receipt = FeePaymentReceipt.objects.create(
                school=student.school,
                student=student,
                amount=amount_dec,
                mode=('UPI' if mode in {'Online', 'Online/UPI', 'UPI'} else mode) if mode in {'Cash', 'UPI', 'Bank', 'Cheque', 'Gateway', 'Online', 'Online/UPI'} else 'Cash',
                status='Success',
                created_by=None,
                legacy_fee_transaction=fee_tx,
            )
            FinanceService.allocate_receipt(receipt, as_of=date if isinstance(date, date_type) else timezone.now().date())

            return fee_tx
