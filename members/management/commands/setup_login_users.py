"""
Create or reset login credentials for all roles.
Run: python manage.py setup_login_users

Creates a school if none exists, then creates users:
- admin / adminpass123 (superuser - can log in on any school)
- school_admin / admin123 (ADMIN role)
- teacher / teacher123 (TEACHER role)
- staff / staff123 (STAFF role)
- accountant / accountant123 (ACCOUNTANT role)
- owner / owner123 (OWNER role)

All non-superuser accounts are linked to the first school.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Q
from members.models import School, UserProfile, Member

User = get_user_model()

DEFAULT_PASSWORD = {
    "admin": "adminpass123",
    "school_admin": "admin123",
    "teacher": "teacher123",
    "staff": "staff123",
    "accountant": "accountant123",
    "owner": "owner123",
    "student": "student123",
}

USERS_TO_CREATE = [
    ("admin", "admin@example.com", "OWNER", True),   # superuser
    ("school_admin", "admin@school.com", "ADMIN", False),
    ("teacher", "teacher@school.com", "TEACHER", False),
    ("staff", "staff@school.com", "STAFF", False),
    ("accountant", "accountant@school.com", "ACCOUNTANT", False),
    ("owner", "owner@school.com", "OWNER", False),
    ("student", "student@school.com", "STUDENT", False),
]


class Command(BaseCommand):
    help = "Create/reset login credentials for admin, teacher, staff, etc. (all use same login page)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--run-if-empty",
            action="store_true",
            help="Only run when no users exist (e.g. fresh deploy). Use in Render startCommand to auto-create demo users once.",
        )

    def handle(self, *args, **options):
        if options.get("run_if_empty") and User.objects.exists():
            self.stdout.write("Users already exist; skipping (--run-if-empty).")
            return

        # 1. Ensure a school exists (needed for localhost login)
        school = School.objects.first()
        if not school:
            school = School.objects.create(
                name="Demo School",
                address="123 Education Lane",
                school_code="DEMO001",
                code="demo",
            )
            self.stdout.write(self.style.SUCCESS(f"Created school: {school.name}"))

        # 1b. Fix any user profiles pointing to wrong/missing school
        fixed = UserProfile.objects.filter(Q(school__isnull=True) | ~Q(school=school)).update(school=school)
        if fixed:
            self.stdout.write(f"Fixed {fixed} user profile(s) → {school.name}")

        # 2. Create/reset users
        for username, email, role, is_superuser in USERS_TO_CREATE:
            user, created = User.objects.get_or_create(username=username, defaults={"email": email})
            user.email = email
            user.set_password(DEFAULT_PASSWORD[username])
            user.is_superuser = is_superuser
            user.is_staff = is_superuser or (role in ("OWNER", "ADMIN"))
            user.is_active = True
            user.save()

            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.school = school
            profile.role = role
            if role == "STUDENT":
                member = Member.objects.filter(school=school, student_class__isnull=False).first()
                profile.member = member
                if member:
                    self.stdout.write(f"  Linked student to: {member.firstname} {member.lastname} ({member.student_class})")
            profile.save()

            action = "Created" if created else "Reset"
            self.stdout.write(f"  {action}: {username} ({role})")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== Login credentials (all use /accounts/login/) ==="))
        for username, pwd in DEFAULT_PASSWORD.items():
            self.stdout.write(f"  {username} / {pwd}")
