"""
School management - Settings for school owners, Add School for superuser.
"""
import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.core.serializers.json import DjangoJSONEncoder

from ..models import (
    School,
    UserProfile,
    AcademicYear,
    ClassRoom,
    Member,
    FeeStructure,
    FeeTransaction,
    ROLE_CHOICES,
)
from ..utils import get_current_school
from ..utils.role_guards import require_roles

User = get_user_model()

ONBOARDING_SESSION_KEY = "onboarding_data"


def _normalize_code(raw_code, school_code, fallback_count):
    """Reuse add_school logic for subdomain code."""
    if raw_code:
        return "".join(c for c in raw_code[:30].lower() if c.isalnum() or c == "-")
    if school_code:
        return "".join(c for c in school_code[:30].lower() if c.isalnum() or c == "-")
    return f"school-{fallback_count}"


@require_http_methods(["GET", "POST"])
def onboarding_wizard(request):
    """
    3-step onboarding (no login): Step 1 School details, Step 2 Owner account, Step 3 Review & submit.
    Uses session to persist step data.
    """
    if request.user.is_authenticated:
        return redirect("index")

    data = request.session.get(ONBOARDING_SESSION_KEY, {})
    step = request.GET.get("step", "1")
    if step not in ("1", "2", "3"):
        step = "1"

    # --- Step 1: School details ---
    if step == "1":
        if request.method == "POST":
            name = request.POST.get("name", "").strip()
            address = request.POST.get("address", "").strip()
            school_code = request.POST.get("school_code", "").strip()
            raw_code = request.POST.get("code", "").strip().lower().replace(" ", "-")
            code = _normalize_code(raw_code, school_code, School.objects.count() + 1) or f"school-{School.objects.count() + 1}"

            errors = []
            if not name or not address or not school_code:
                errors.append("Name, address and school code are required.")
            if school_code and School.objects.filter(school_code=school_code).exists():
                errors.append(f"School code '{school_code}' already exists.")
            if code and School.objects.filter(code=code).exists():
                errors.append(f"Subdomain code '{code}' already exists.")

            if errors:
                for err in errors:
                    messages.error(request, err)
                return render(request, "onboarding_wizard.html", {"step": 1, "data": {**data, "name": name, "address": address, "school_code": school_code, "code": raw_code or code}})

            data["name"] = name
            data["address"] = address
            data["school_code"] = school_code
            data["code"] = code
            request.session[ONBOARDING_SESSION_KEY] = data
            return redirect("onboarding?step=2")

        return render(request, "onboarding_wizard.html", {"step": 1, "data": data})

    # --- Step 2: Owner account ---
    if step == "2":
        if not data.get("name"):
            messages.error(request, "Please complete Step 1 first.")
            return redirect("onboarding?step=1")

        if request.method == "POST":
            username = request.POST.get("owner_username", "").strip()
            email = request.POST.get("owner_email", "").strip()
            password = request.POST.get("owner_password", "")
            password2 = request.POST.get("owner_password2", "")

            errors = []
            if not username:
                errors.append("Username is required.")
            if not password:
                errors.append("Password is required.")
            if password and len(password) < 8:
                errors.append("Password must be at least 8 characters.")
            if password != password2:
                errors.append("Passwords do not match.")
            if username and User.objects.filter(username=username).exists():
                errors.append(f"Username '{username}' is already taken.")

            if errors:
                for err in errors:
                    messages.error(request, err)
                return render(request, "onboarding_wizard.html", {"step": 2, "data": {**data, "owner_username": username, "owner_email": email}})

            data["owner_username"] = username
            data["owner_email"] = email or f"{username}@school.local"
            data["owner_password"] = password
            request.session[ONBOARDING_SESSION_KEY] = data
            return redirect("onboarding?step=3")

        return render(request, "onboarding_wizard.html", {"step": 2, "data": data})

    # --- Step 3: Review & submit ---
    if step == "3":
        if not data.get("name") or not data.get("owner_username") or not data.get("owner_password"):
            messages.error(request, "Please complete Steps 1 and 2 first.")
            return redirect("onboarding?step=1")

        if request.method == "POST":
            # Create school
            code = data.get("code") or _normalize_code("", data.get("school_code", ""), School.objects.count() + 1)
            if School.objects.filter(code=code).exists():
                code = f"school-{School.objects.count() + 1}"
            school = School.objects.create(
                name=data["name"],
                address=data["address"],
                school_code=data["school_code"],
                code=code,
            )
            # Create owner user
            user = User.objects.create_user(
                username=data["owner_username"],
                email=data.get("owner_email") or f"{data['owner_username']}@school.local",
                password=data["owner_password"],
            )
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.school = school
            profile.role = "OWNER"
            profile.save()
            # Clear session
            request.session.pop(ONBOARDING_SESSION_KEY, None)
            messages.success(request, f"School '{school.name}' is ready. Please log in with your owner account.")
            return redirect("login")

        return render(request, "onboarding_wizard.html", {"step": 3, "data": data})

    return redirect("onboarding?step=1")


@login_required
@require_roles("OWNER", "ADMIN")
def school_settings(request):
    """School owners/admins - view and edit their school details."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")

    if request.method == "POST":
        school.name = request.POST.get("name", "").strip()
        school.address = request.POST.get("address", "").strip()
        school.school_code = request.POST.get("school_code", "").strip()
        if school.name and school.address and school.school_code:
            school.save()
            messages.success(request, "School details updated.")
        else:
            messages.error(request, "Name, address and school code are required.")
        return redirect("school_settings")

    return render(request, "school_settings.html", {"school": school})


@login_required
def school_list(request):
    """Superuser only - list all schools."""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Superuser access required")

    schools = School.objects.all().order_by("name")
    return render(request, "school_list.html", {"schools": schools})


@login_required
def add_school(request):
    """Superuser only - add a new school."""
    if not request.user.is_superuser:
        return HttpResponseForbidden("Superuser access required")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        address = request.POST.get("address", "").strip()
        school_code = request.POST.get("school_code", "").strip()
        raw_code = request.POST.get("code", "").strip().lower().replace(" ", "-")
        code = raw_code if raw_code else "".join(c for c in school_code[:30].lower() if c.isalnum() or c == "-") or f"school-{School.objects.count() + 1}"

        if not name or not address or not school_code:
            messages.error(request, "Name, address and school code are required.")
            return redirect("add_school")

        if School.objects.filter(school_code=school_code).exists():
            messages.error(request, f"School code '{school_code}' already exists.")
            return redirect("add_school")

        if School.objects.filter(code=code).exists():
            messages.error(request, f"Subdomain code '{code}' already exists.")
            return redirect("add_school")

        school = School.objects.create(
            name=name,
            address=address,
            school_code=school_code,
            code=code,
        )
        messages.success(request, f"School '{school.name}' created. Subdomain: {school.code}.yoursite.com")

        # Optional: create owner user for this school
        owner_username = request.POST.get("owner_username", "").strip()
        owner_email = request.POST.get("owner_email", "").strip()
        owner_password = request.POST.get("owner_password", "").strip()

        if owner_username and owner_password:
            if User.objects.filter(username=owner_username).exists():
                messages.warning(request, f"User '{owner_username}' already exists. Skipped owner creation.")
            else:
                user = User.objects.create_user(
                    username=owner_username,
                    email=owner_email or f"{owner_username}@school.local",
                    password=owner_password,
                )
                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.school = school
                profile.role = "OWNER"
                profile.save()
                messages.success(request, f"Owner account created: {owner_username} / (password as entered)")

        return redirect("school_list")

    return render(request, "school_form.html")


# --- School admin: User management ---


@login_required
@require_roles("OWNER", "ADMIN")
def school_user_list(request):
    """List users for current school."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    profiles = UserProfile.objects.filter(school=school).select_related("user").order_by("user__username")
    return render(request, "school_user_list.html", {"profiles": profiles})


@login_required
@require_roles("OWNER", "ADMIN")
def school_user_add(request):
    """Add a new user to the school with role."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        role = request.POST.get("role", "STAFF").strip()
        if role not in [r[0] for r in ROLE_CHOICES]:
            role = "STAFF"
        if not username:
            messages.error(request, "Username is required.")
            return render(request, "school_user_form.html", {"roles": ROLE_CHOICES, "edit": False})
        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' already exists.")
            return render(request, "school_user_form.html", {"roles": ROLE_CHOICES, "edit": False})
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
            return render(request, "school_user_form.html", {"roles": ROLE_CHOICES, "edit": False})
        user = User.objects.create_user(username=username, email=email or f"{username}@school.local", password=password)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.school = school
        profile.role = role
        profile.save()
        messages.success(request, f"User '{username}' added with role {role}.")
        return redirect("school_user_list")
    return render(request, "school_user_form.html", {"roles": ROLE_CHOICES, "edit": False})


@login_required
@require_roles("OWNER", "ADMIN")
def school_user_edit(request, user_id):
    """Edit user role, is_active, optional password change."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user, school=school)
    if request.method == "POST":
        role = request.POST.get("role", profile.role).strip()
        if role in [r[0] for r in ROLE_CHOICES]:
            profile.role = role
        profile.user.is_active = request.POST.get("is_active") == "1"
        profile.user.email = request.POST.get("email", "").strip() or profile.user.email
        new_password = request.POST.get("password", "").strip()
        if new_password and len(new_password) >= 8:
            profile.user.set_password(new_password)
        profile.user.save()
        profile.save()
        if profile.role == "PARENT":
            guardian_ids = [int(x) for x in request.POST.getlist("guardian_of") if x.isdigit()]
            profile.guardian_of.set(Member.objects.filter(id__in=guardian_ids, school=school))
        messages.success(request, "User updated.")
        return redirect("school_user_list")
    students = Member.objects.filter(school=school).select_related("student_class").order_by("firstname")
    guardian_ids = list(profile.guardian_of.values_list("id", flat=True))
    return render(request, "school_user_form.html", {"profile": profile, "roles": ROLE_CHOICES, "edit": True, "students": students, "guardian_ids": guardian_ids})


@login_required
@require_roles("OWNER", "ADMIN")
@require_POST
def school_user_deactivate(request, user_id):
    """Toggle is_active for a school user."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    user = get_object_or_404(User, id=user_id)
    profile = get_object_or_404(UserProfile, user=user, school=school)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f"User {'deactivated' if not user.is_active else 'activated'}.")
    return redirect("school_user_list")


# --- Academic year ---


@login_required
@require_roles("OWNER", "ADMIN")
def academic_year_list(request):
    """List and add academic years for current school."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    if request.method == "POST" and request.POST.get("action") == "add":
        name = request.POST.get("name", "").strip()
        start_date = request.POST.get("start_date", "").strip()
        end_date = request.POST.get("end_date", "").strip()
        is_active = request.POST.get("is_active") == "1"
        if name and start_date and end_date:
            if is_active:
                AcademicYear.objects.filter(school=school).update(is_active=False)
            AcademicYear.objects.create(school=school, name=name, start_date=start_date, end_date=end_date, is_active=is_active)
            messages.success(request, f"Academic year '{name}' created.")
        else:
            messages.error(request, "Name, start date and end date are required.")
        return redirect("academic_year_list")
    years = AcademicYear.objects.filter(school=school).order_by("-start_date")
    return render(request, "academic_year_list.html", {"years": years})


@login_required
@require_roles("OWNER", "ADMIN")
def academic_year_edit(request, year_id):
    """Edit an academic year."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    ay = get_object_or_404(AcademicYear, id=year_id, school=school)
    if request.method == "POST":
        ay.name = request.POST.get("name", ay.name).strip()
        ay.start_date = request.POST.get("start_date", ay.start_date)
        ay.end_date = request.POST.get("end_date", ay.end_date)
        if request.POST.get("is_active") == "1":
            AcademicYear.objects.filter(school=school).update(is_active=False)
            ay.is_active = True
        else:
            ay.is_active = False
        ay.save()
        messages.success(request, "Academic year updated.")
        return redirect("academic_year_list")
    return render(request, "academic_year_edit.html", {"year": ay})


# --- JSON backup (OWNER only) ---


def _model_to_dict(queryset, fields):
    """Serialize queryset to list of dicts with only given fields."""
    return list(queryset.values(*fields))


@login_required
@require_roles("OWNER")
def school_backup_json(request):
    """Download a JSON backup of key school data (read-only, no passwords)."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    payload = {
        "school": {"id": school.id, "name": school.name, "address": school.address, "school_code": school.school_code, "code": school.code},
        "academic_years": _model_to_dict(AcademicYear.objects.filter(school=school), ["id", "name", "start_date", "end_date", "is_active"]),
        "class_rooms": _model_to_dict(ClassRoom.objects.filter(school=school), ["id", "name", "section"]),
        "members": _model_to_dict(
            Member.objects.filter(school=school),
            ["id", "admission_no", "firstname", "lastname", "father_name", "mobile_number", "email", "student_class_id", "roll_number", "gender", "dob", "joined_date"],
        ),
        "fee_structures": _model_to_dict(FeeStructure.objects.filter(school=school), ["id", "class_room_id", "title", "amount", "due_date"]),
        "fee_transactions": _model_to_dict(
            FeeTransaction.objects.filter(student__school=school),
            ["id", "student_id", "amount_paid", "month_year", "payment_date", "payment_mode", "status"],
        ),
    }
    # Use Django's date serializer
    response = HttpResponse(json.dumps(payload, indent=2, cls=DjangoJSONEncoder), content_type="application/json")
    response["Content-Disposition"] = f'attachment; filename="school_backup_{school.code}.json"'
    return response


# --- Getting started banner ---


@login_required
@require_roles("OWNER", "ADMIN")
@require_POST
def dismiss_getting_started(request):
    """Mark getting started banner as dismissed for current user."""
    school = get_current_school(request)
    if not school:
        raise HttpResponseForbidden("No school context")
    profile = getattr(request.user, "userprofile", None)
    if profile:
        profile.getting_started_dismissed = True
        profile.save(update_fields=["getting_started_dismissed"])
    return redirect("index")
