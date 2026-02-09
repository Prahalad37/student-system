from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse
from datetime import date

from ..models import Member, Notice, FeeTransaction, LibraryTransaction, StudentTransport
from ..forms import AddNoticeForm
from ..utils import get_current_school
from ..utils.role_guards import require_roles
from ..utils.roles import get_user_role


def landing(request):
    """Landing page for anonymous visitors. Logged-in users are redirected to dashboard."""
    if request.user.is_authenticated:
        return redirect("index")
    return render(request, "landing.html")


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF", "STUDENT", "PARENT")
def index(request):
    school = getattr(request, "school", None)
    if school is None:
        return redirect("/admin/")
    if get_user_role(request) == "STUDENT":
        return redirect("student_portal")
    if get_user_role(request) == "PARENT":
        return redirect("parent_dashboard")
    total_students = Member.objects.filter(school=school).count()
    new_admissions = Member.objects.filter(
        school=school,
        joined_date__month=date.today().month,
    ).count()
    revenue_stats = Member.objects.filter(school=school).aggregate(
        total_expected=Sum("fee_total"),
        total_collected=Sum("fee_paid"),
    )
    total_revenue = revenue_stats["total_collected"] or 0
    pending_dues = (revenue_stats["total_expected"] or 0) - total_revenue
    recent_transactions = (
        FeeTransaction.objects.filter(student__school=school)
        .select_related("student", "student__student_class")
        .order_by("-payment_date", "-id")[:5]
    )

    # Added Phase 1 Analytics
    male_count = Member.objects.filter(school=school, gender="Male").count()
    female_count = Member.objects.filter(school=school, gender="Female").count()
    recent_admissions = Member.objects.filter(school=school).order_by("-joined_date", "-id")[:5]

    profile = getattr(request.user, "userprofile", None)
    show_getting_started = (
        profile
        and getattr(profile, "getting_started_dismissed", False) is False
        and get_user_role(request) in ("OWNER", "ADMIN")
    )
    getting_started_items = [
        {"url_name": "school_settings", "label": "School settings"},
        {"url_name": "academic_year_list", "label": "Add academic year"},
        {"url_name": "school_user_list", "label": "Manage users"},
        {"url_name": "all_students", "label": "Add students"},
    ]

    context = {
        "school": school,
        "total_students": total_students,
        "new_admissions": new_admissions,
        "total_revenue": total_revenue,
        "pending_dues": pending_dues,
        "recent_transactions": recent_transactions,
        "male_count": male_count,
        "female_count": female_count,
        "recent_admissions": recent_admissions,
        "students_on_bus": StudentTransport.objects.filter(school=school).count(),
        "books_issued": LibraryTransaction.objects.filter(school=school, status="Issued").count(),
        "show_getting_started": show_getting_started,
        "getting_started_items": getting_started_items,
    }
    return render(request, "index.html", context)


@login_required
@require_roles("OWNER", "ADMIN")
def add_notice(request):
    school = get_current_school(request)
    if request.method == "POST":
        form = AddNoticeForm(request.POST)
        if form.is_valid():
            Notice.objects.create(
                school=school,
                title=form.cleaned_data["title"],
                message=form.cleaned_data["message"],
            )
    return redirect("index")


@login_required
@require_roles("OWNER")
def delete_notice(request, id):
    school = get_current_school(request)
    get_object_or_404(Notice, id=id, school=school).delete()
    return redirect("index")


@login_required
def debug_test(request):
    return HttpResponse("<h1>Dashboard OK</h1>")
