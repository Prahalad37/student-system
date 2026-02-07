"""
School management - Settings for school owners, Add School for superuser.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden

from ..models import School, UserProfile
from ..utils import get_current_school
from ..utils.role_guards import require_roles

User = get_user_model()


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
