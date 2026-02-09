from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template
from django.db import transaction
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from xhtml2pdf import pisa
from ..models import (
    Member,
    FeeTransaction,
    ClassRoom,
    FeeStructure,
    Expense,
    AcademicYear,
    FeeInstallment,
    FeePaymentReceipt,
    FeePaymentAllocation,
    FeeDiscount,
    StudentConcession,
    LateFeePolicy,
    FeeRefund,
)
from ..forms import FeeCollectionForm, ExpenseForm
from ..utils import get_current_school
from ..utils.role_guards import require_roles
from ..services.finance import FinanceService

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def fee_home(request):
    school = get_current_school(request)
    transactions = FeeTransaction.objects.filter(student__school=school).select_related('student').order_by('-payment_date', '-id')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    class_filter = request.GET.get('class_id')
    mode_filter = request.GET.get('mode')

    if start_date: transactions = transactions.filter(payment_date__gte=start_date)
    if end_date: transactions = transactions.filter(payment_date__lte=end_date)
    if class_filter: transactions = transactions.filter(student__student_class__id=class_filter)
    if mode_filter: transactions = transactions.filter(payment_mode=mode_filter)

    total_collected = transactions.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    students = Member.objects.filter(school=school).annotate(balance=F('fee_total') - F('fee_paid')).order_by('-balance')
    tx_paginator = Paginator(transactions, 25)
    page_obj = tx_paginator.get_page(request.GET.get('page', 1))

    context = {
        'transactions': page_obj, 'page_obj': page_obj, 'total_collected': total_collected,
        'classes': ClassRoom.objects.filter(school=school), 'students': students
    }
    return render(request, 'fees.html', context)

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def collect_fee(request):
    if request.method == "POST":
        school = get_current_school(request)
        form = FeeCollectionForm(request.POST)
        if form.is_valid():
            student_id = form.cleaned_data['student_id']
            get_object_or_404(Member, id=student_id, school=school)
            FinanceService.collect_fee(
                school_id=school.id,
                student_id=student_id,
                amount=form.cleaned_data['amount'],
                mode=form.cleaned_data['mode'],
                date=form.cleaned_data['date']
            )
        return redirect('fee_home')
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_config(request):
    if request.method == "POST":
        school = get_current_school(request)
        FeeStructure.objects.create(
            school=school,
            class_room=get_object_or_404(ClassRoom, id=request.POST.get('class_id'), school=school),
            title=request.POST.get('title'), amount=request.POST.get('amount')
        )
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def generate_monthly_dues(request):
    if request.method == "POST":
        school = get_current_school(request)
        fees_by_class = (
            FeeStructure.objects.filter(school=school)
            .values('class_room')
            .annotate(total=Sum('amount'))
        )
        for row in fees_by_class:
            if row['total'] and row['class_room']:
                Member.objects.filter(
                    school=school,
                    student_class_id=row['class_room']
                ).update(fee_total=F('fee_total') + row['total'])
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def receipt_pdf(request, id):
    school = get_current_school(request)
    t = get_object_or_404(FeeTransaction, id=id, student__school=school)
    template = get_template('receipt_pdf.html')
    school = t.student.school
    remaining_balance = (t.student.fee_total or 0) - (t.student.fee_paid or 0)
    html = template.render({'t': t, 'school': school, 'remaining_balance': remaining_balance})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def student_receipt_pdf(request, student_id: int):
    school = get_current_school(request)
    student = get_object_or_404(Member, id=student_id, school=school)
    t = FeeTransaction.objects.filter(student=student).order_by('-payment_date', '-id').first()
    if not t:
        return redirect('fee_home')
    return receipt_pdf(request, t.id)

@login_required
@require_roles("OWNER", "ADMIN")
def delete_fee(request, id):
    school = get_current_school(request)
    t = get_object_or_404(FeeTransaction, id=id, student__school=school)
    with transaction.atomic():
        Member.objects.filter(pk=t.student_id).update(
            fee_paid=F('fee_paid') - t.amount_paid
        )
        t.delete()
    return redirect('fee_home')

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF")
def get_fee_amount(request):
    """Return due fee amount for a student (fee_total - fee_paid)."""
    student_id = request.GET.get('student_id')
    if not student_id:
        return JsonResponse({'error': 'student_id required'}, status=400)
    try:
        student_id = int(student_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'invalid student_id'}, status=400)
    school = get_current_school(request)
    student = get_object_or_404(Member, id=student_id, school=school)
    due_amount = (student.fee_total or 0) - (student.fee_paid or 0)
    return JsonResponse({'amount': str(max(due_amount, 0))})

@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def add_expense(request):
    school = get_current_school(request)
    form = ExpenseForm()
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.school = school
            obj.save()
            return redirect('add_expense')
    expenses = Expense.objects.filter(school=school).order_by('-id')
    return render(request, 'add_expense.html', {'expenses': expenses, 'form': form})


# --- Finance v2: Installments ---


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_installments(request):
    """List fee installments by student; ensure quarterly installments exist for active academic year."""
    school = get_current_school(request)
    class_id = request.GET.get('class_id')
    student_id = request.GET.get('student_id')
    today = timezone.now().date()
    students_qs = Member.objects.filter(school=school).select_related('student_class').order_by('student_class__name', 'firstname')
    if class_id:
        students_qs = students_qs.filter(student_class_id=class_id)
    if student_id:
        students_qs = students_qs.filter(id=student_id)
    # Ensure installments exist for each student
    for student in students_qs:
        FinanceService.ensure_quarterly_installments(student, as_of=today)
    installments = FeeInstallment.objects.filter(school=school).select_related('student', 'student__student_class', 'academic_year').order_by('student__firstname', 'due_date')
    if class_id:
        installments = installments.filter(student__student_class_id=class_id)
    if student_id:
        installments = installments.filter(student_id=student_id)
    classes = ClassRoom.objects.filter(school=school)
    return render(request, 'fee_installments.html', {
        'installments': installments,
        'classes': classes,
        'students': students_qs[:500],
    })


# --- Finance v2: Discounts ---


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_discounts(request):
    """List fee discounts; add/edit/delete."""
    school = get_current_school(request)
    discounts = FeeDiscount.objects.filter(school=school).order_by('name')
    return render(request, 'fee_discounts.html', {'discounts': discounts})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_discount_add(request):
    school = get_current_school(request)
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        discount_type = request.POST.get('discount_type', 'Fixed')
        value = request.POST.get('value', '0')
        is_concession = request.POST.get('is_concession') == '1'
        if name and discount_type in ('Percent', 'Fixed'):
            from decimal import Decimal
            FeeDiscount.objects.get_or_create(school=school, name=name, defaults={'discount_type': discount_type, 'value': Decimal(str(value or 0)), 'is_concession': is_concession})
            return redirect('fee_discounts')
    return redirect('fee_discounts')


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_discount_edit(request, pk):
    school = get_current_school(request)
    d = get_object_or_404(FeeDiscount, pk=pk, school=school)
    if request.method == "POST":
        d.name = request.POST.get('name', d.name).strip()
        d.discount_type = request.POST.get('discount_type', d.discount_type)
        d.value = request.POST.get('value', d.value) or 0
        d.is_concession = request.POST.get('is_concession') == '1'
        d.is_active = request.POST.get('is_active') == '1'
        d.save()
        return redirect('fee_discounts')
    return render(request, 'fee_discount_edit.html', {'discount': d})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
@require_POST
def fee_discount_delete(request, pk):
    school = get_current_school(request)
    get_object_or_404(FeeDiscount, pk=pk, school=school).delete()
    return redirect('fee_discounts')


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_concessions(request):
    """List and add student concessions (assign discount to student)."""
    school = get_current_school(request)
    concessions = StudentConcession.objects.filter(school=school).select_related('student', 'discount').order_by('-id')
    if request.method == "POST" and request.POST.get('action') == 'add':
        student_id = request.POST.get('student_id')
        discount_id = request.POST.get('discount_id')
        if student_id and discount_id:
            student = get_object_or_404(Member, id=student_id, school=school)
            discount = get_object_or_404(FeeDiscount, id=discount_id, school=school)
            StudentConcession.objects.get_or_create(school=school, student=student, discount=discount, defaults={'is_active': True})
            return redirect('fee_concessions')
    students = Member.objects.filter(school=school).select_related('student_class').order_by('firstname')
    discounts = FeeDiscount.objects.filter(school=school, is_active=True)
    return render(request, 'fee_concessions.html', {'concessions': concessions, 'students': students, 'discounts': discounts})


# --- Finance v2: Late fee policy ---


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_late_fee_policy(request):
    school = get_current_school(request)
    policy, _ = LateFeePolicy.objects.get_or_create(school=school, defaults={'grace_days': 0, 'per_day_amount': 0, 'cap_amount': 0})
    if request.method == "POST":
        policy.grace_days = int(request.POST.get('grace_days', 0) or 0)
        policy.per_day_amount = request.POST.get('per_day_amount') or 0
        policy.cap_amount = request.POST.get('cap_amount') or 0
        policy.is_active = request.POST.get('is_active') == '1'
        policy.save()
        return redirect('fee_late_fee_policy')
    return render(request, 'fee_late_fee_policy.html', {'policy': policy})


# --- Finance v2: Receipts & Refunds ---


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_receipts(request):
    """List fee payment receipts with option to request refund."""
    school = get_current_school(request)
    receipts = FeePaymentReceipt.objects.filter(school=school).select_related('student', 'student__student_class').order_by('-received_at')[:200]
    return render(request, 'fee_receipts.html', {'receipts': receipts})


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
@require_POST
def fee_refund_request(request, receipt_id):
    school = get_current_school(request)
    receipt = get_object_or_404(FeePaymentReceipt, id=receipt_id, school=school)
    amount = request.POST.get('amount', receipt.amount)
    reason = request.POST.get('reason', '')[:255]
    FeeRefund.objects.create(school=school, receipt=receipt, amount=amount, reason=reason, status='Initiated')
    return redirect('fee_refunds')


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT")
def fee_refunds(request):
    """List refund requests; OWNER/ADMIN can approve/reject."""
    school = get_current_school(request)
    refunds = FeeRefund.objects.filter(school=school).select_related('receipt', 'receipt__student').order_by('-created_at')
    return render(request, 'fee_refunds.html', {'refunds': refunds})


@login_required
@require_roles("OWNER", "ADMIN")
@require_POST
def fee_refund_process(request, refund_id):
    school = get_current_school(request)
    ref = get_object_or_404(FeeRefund, id=refund_id, school=school)
    action = request.POST.get('action')  # Processed | Rejected
    if action in ('Processed', 'Rejected'):
        ref.status = action
        ref.processed_by = request.user
        ref.save()
    return redirect('fee_refunds')