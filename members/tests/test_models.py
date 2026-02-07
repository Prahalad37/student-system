"""Model tests for members app."""
from django.contrib.auth.models import User
from django.test import TestCase

from ..models import School, ClassRoom, Member, Attendance, Notice, Expense


class SchoolModelTest(TestCase):
    """Tests for School model."""

    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            school_code="TEST001",
            code="test",
        )

    def test_school_str(self):
        self.assertEqual(str(self.school), "Test School")

    def test_school_code_unique(self):
        with self.assertRaises(Exception):
            School.objects.create(
                name="Other",
                address="456 St",
                school_code="TEST001",
                code="other",
            )


class MemberModelTest(TestCase):
    """Tests for Member (Student) model."""

    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            school_code="TEST001",
            code="test",
        )

    def test_member_creation(self):
        m = Member.objects.create(
            school=self.school,
            firstname="John",
            lastname="Doe",
            fee_total=1000,
            fee_paid=0,
        )
        self.assertEqual(m.firstname, "John")
        self.assertEqual(m.fee_total - m.fee_paid, 1000)


class AttendanceModelTest(TestCase):
    """Tests for Attendance model."""

    def setUp(self):
        self.school = School.objects.create(
            name="Test School",
            address="123 Test St",
            school_code="TEST001",
            code="test",
        )
        self.student = Member.objects.create(
            school=self.school,
            firstname="Jane",
            lastname="Doe",
        )

    def test_attendance_unique_per_student_date(self):
        from django.db import IntegrityError
        from datetime import date
        d = date(2025, 2, 7)
        Attendance.objects.create(student=self.student, date=d, status="Present")
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(
                student=self.student,
                date=d,
                status="Absent",
            )
