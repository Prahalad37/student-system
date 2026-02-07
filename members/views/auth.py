from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render

from ..utils import get_current_school


def _get_login_redirect_url(user):
    """Redirect STUDENT to portal, others to index."""
    if getattr(user, "is_superuser", False):
        return "/"
    profile = getattr(user, "userprofile", None)
    if profile and profile.role == "STUDENT":
        return "/student/"
    return "/"


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
        if school is None:
            if user.is_superuser:
                return super().form_valid(form)
            form.add_error(None, "No school configured yet. Contact admin or add a school at /admin/")
            return self.form_invalid(form)
        if not user.is_superuser:
            profile = getattr(user, "userprofile", None)
            if not profile or profile.school_id != school.id:
                form.add_error(None, "You do not belong to this school.")
                return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return _get_login_redirect_url(self.request.user)
