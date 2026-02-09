from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from ..utils import get_current_school
from ..utils.domain import extract_subdomain


def _get_login_redirect_url(user):
    """Redirect STUDENT to portal, others to dashboard (index)."""
    if getattr(user, "is_superuser", False):
        return reverse("index")
    profile = getattr(user, "userprofile", None)
    if profile and profile.role == "STUDENT":
        return "/student/"
    return reverse("index")


@login_required
def user_profile(request):
    profile = getattr(request.user, "userprofile", None)
    school = get_current_school(request)
    role_display = {"OWNER": "Owner", "ADMIN": "Admin", "ACCOUNTANT": "Accountant",
                    "TEACHER": "Teacher", "STAFF": "Staff", "STUDENT": "Student"}.get(
        profile.role if profile else None, profile.role if profile else "—"
    )
    return render(request, "profile.html", {
        "profile": profile,
        "school": school,
        "role_display": role_display,
    })


class TenantLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True

    def dispatch(self, request, *args, **kwargs):
        # When school is None (Render *.onrender.com, fresh deploy), show login so superuser can access admin
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        school = getattr(self.request, "school", None)
        subdomain = extract_subdomain(self.request)
        if school is None:
            if user.is_superuser:
                return super().form_valid(form)
            form.add_error(None, "No school configured yet. Contact admin or add a school at /admin/")
            return self.form_invalid(form)
        if not user.is_superuser:
            profile = getattr(user, "userprofile", None)
            if not profile:
                form.add_error(None, "No user profile. Contact admin.")
                return self.form_invalid(form)
            # Single URL (no subdomain): allow if user has any school. After login middleware sets request.school from profile.
            if subdomain is None:
                if not profile.school_id:
                    form.add_error(None, "Your account is not linked to any school. Contact admin.")
                    return self.form_invalid(form)
            else:
                if profile.school_id != school.id:
                    form.add_error(None, "You do not belong to this school.")
                    return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return _get_login_redirect_url(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["show_demo_logins"] = getattr(settings, "DEBUG", False)
        return context
