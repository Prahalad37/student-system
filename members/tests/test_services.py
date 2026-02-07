"""Service layer tests."""
from datetime import date

from django.test import TestCase

from ..models import School, ClassRoom, Member, Book
from ..services.finance import FinanceService


class FinanceServiceTest(TestCase):
    """Tests for FinanceService."""

    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            school_code="TEST001",
            code="test",
        )
        self.student = Member.objects.create(
            school=self.school,
            firstname="Test",
            lastname="Student",
            fee_total=1000,
            fee_paid=0,
        )

    def test_collect_fee_updates_balance(self):
        FinanceService.collect_fee(
            school_id=self.school.id,
            student_id=self.student.id,
            amount=500,
            mode="Cash",
            date=date.today(),
        )
        self.student.refresh_from_db()
        self.assertEqual(float(self.student.fee_paid), 500)

    def test_collect_fee_rejects_zero_amount(self):
        with self.assertRaises(ValueError):
            FinanceService.collect_fee(
                school_id=self.school.id,
                student_id=self.student.id,
                amount=0,
                mode="Cash",
            )
