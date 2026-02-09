"""Parent portal - read-only view of linked students (attendance, fee, report card)."""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden
from django.db.models import Sum

from ..models import Member, Attendance, FeeTransaction, ExamScore, Notice, StudyMaterial
from ..utils import get_current_school
from ..utils.role_guards import require_roles


def _parent_students(request):
    """Return queryset of students the parent is guardian of (same school)."""
    school = get_current_school(request)
    if not school:
        return Member.objects.none()
    profile = getattr(request.user, "userprofile", None)
    if not profile or profile.role != "PARENT":
        return Member.objects.none()
    return profile.guardian_of.filter(school=school).select_related("student_class")


@login_required
@require_roles("PARENT")
def parent_dashboard(request):
    """List linked students and short summary for each."""
    school = get_current_school(request)
    if not school:
        return HttpResponseForbidden("No school context")
    students = _parent_students(request)
    # Add summary per student: recent attendance count, fee balance, latest exam
    for s in students:
        s.recent_present = Attendance.objects.filter(student=s, status="Present").count()
        s.recent_absent = Attendance.objects.filter(student=s, status="Absent").count()
        s.fee_balance = (s.fee_total or 0) - (s.fee_paid or 0)
        s.latest_exam = ExamScore.objects.filter(student=s).order_by("-created_at").first()
    notices = Notice.objects.filter(school=school).order_by("-created_at")[:5]
    return render(request, "parent_dashboard.html", {"students": students, "notices": notices})


@login_required
@require_roles("PARENT")
def parent_student_detail(request, student_id):
    """One student: attendance summary, fee status, report cards."""
    school = get_current_school(request)
    if not school:
        return HttpResponseForbidden("No school context")
    students_qs = _parent_students(request)
    student = get_object_or_404(students_qs, id=student_id)
    attendance_records = Attendance.objects.filter(student=student).order_by("-date")[:30]
    fee_transactions = FeeTransaction.objects.filter(student=student).order_by("-payment_date")[:10]
    fee_balance = (student.fee_total or 0) - (student.fee_paid or 0)
    scores = ExamScore.objects.filter(student=student).select_related("exam_type").order_by("-created_at")
    materials = StudyMaterial.objects.filter(school=school, class_name=student.student_class.name if student.student_class else "").order_by("-id")[:10]
    return render(
        request,
        "parent_student_detail.html",
        {
            "student": student,
            "attendance_records": attendance_records,
            "fee_transactions": fee_transactions,
            "fee_balance": fee_balance,
            "scores": scores,
            "materials": materials,
        },
    )
