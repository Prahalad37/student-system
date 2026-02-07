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


@login_required
@require_roles("OWNER", "ADMIN", "ACCOUNTANT", "TEACHER", "STAFF", "STUDENT")
def index(request):
    if get_user_role(request) == "STUDENT":
        return redirect("student_portal")
    school = get_current_school(request)
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
