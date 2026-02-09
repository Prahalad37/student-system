from datetime import date
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
from xhtml2pdf import pisa
from ..models import Member, Attendance, ClassRoom, ExamScore, Subject, ExamType
from ..utils import get_current_school
from ..utils.role_guards import require_roles

@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def attendance(request):
    """Crash-Proof Attendance Register"""
    school = get_current_school(request)
    classes = ClassRoom.objects.filter(school=school)
    
    # 1. INPUT SANITIZATION
    raw_class_id = request.GET.get('class_id')
    selected_date = request.GET.get('date') or date.today().isoformat()
    
    selected_class_id = None
    if raw_class_id and raw_class_id not in ['None', '', 'null']:
        try:
            selected_class_id = int(raw_class_id)
        except (ValueError, TypeError):
            selected_class_id = None

    # 2. FETCH STUDENTS
    students = []
    if selected_class_id:
        students = Member.objects.filter(school=school, student_class_id=selected_class_id).order_by('firstname')
        existing_records = Attendance.objects.filter(
            student__school=school, 
            student__student_class_id=selected_class_id, 
            date=selected_date
        )
        attendance_map = {rec.student_id: rec.status for rec in existing_records}
        for student in students:
            student.current_status = attendance_map.get(student.id, 'Present')

    # 3. HANDLE FORM SAVE
    if request.method == "POST":
        date_input = request.POST.get('date')
        class_input = request.POST.get('class_id')
        if not class_input or class_input in ['None', '']:
            class_input = ''
            
        student_ids = request.POST.getlist('student_ids')
        if student_ids:
            students_to_mark = Member.objects.filter(school=school, id__in=student_ids)
            for student in students_to_mark:
                status = request.POST.get(f'status_{student.id}')
                if status:
                    Attendance.objects.update_or_create(
                        student=student,
                        date=date_input,
                        defaults={'status': status}
                    )
        return redirect(f'/attendance/?class_id={class_input}&date={date_input}')

    context = {
        'classes': classes,
        'students': students,
        'selected_class_id': selected_class_id,
        'selected_date': selected_date
    }
    return render(request, 'attendance.html', context)

@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def attendance_records(request):
    """View Historical Attendance Logs"""
    school = get_current_school(request)
    date_filter = request.GET.get('date')
    class_filter = request.GET.get('class_id')
    
    records = Attendance.objects.filter(student__school=school).select_related('student', 'student__student_class').order_by('-date', 'student__firstname')
    
    if date_filter:
        records = records.filter(date=date_filter)
    if class_filter and class_filter not in ['None', '']:
        records = records.filter(student__student_class_id=class_filter)
    
    paginator = Paginator(records, 50)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    classes = ClassRoom.objects.filter(school=school)
    context = {
        'records': page_obj,
        'page_obj': page_obj,
        'classes': classes,
        'selected_date': date_filter,
        'selected_class': int(class_filter) if class_filter and class_filter.isdigit() else None
    }
    return render(request, 'attendance_records.html', context)

@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def report_card(request):
    school = get_current_school(request)
    scores = ExamScore.objects.filter(student__school=school).select_related(
        'student', 'student__student_class', 'exam_type'
    ).order_by('-id')

    class_filter = request.GET.get('class_id')
    student_filter = request.GET.get('student')
    exam_filter = request.GET.get('exam')

    if class_filter and class_filter not in ('', 'None'):
        scores = scores.filter(student__student_class_id=class_filter)
    if student_filter:
        scores = scores.filter(
            Q(student__firstname__icontains=student_filter) |
            Q(student__lastname__icontains=student_filter) |
            Q(student__admission_no__icontains=student_filter)
        )
    if exam_filter:
        scores = scores.filter(exam_name__icontains=exam_filter)

    paginator = Paginator(scores, 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    subjects = Subject.objects.filter(school=school).order_by('name')
    max_total = (subjects.count() * 100) if subjects.exists() else 500
    for s in page_obj.object_list:
        s.subject_marks_display = _get_legacy_subject_marks(s)
        s.marks_list = [(sub.name, s.subject_marks_display.get(sub.name, 0)) for sub in subjects]
        s.total_marks = sum(v for v in s.subject_marks_display.values() if isinstance(v, (int, float)))
        s.percentage = round((s.total_marks / max_total * 100), 1) if max_total else 0
        s.passed = s.total_marks >= (max_total * 0.33) if max_total else False
    classes = ClassRoom.objects.filter(school=school).order_by('name')

    return render(request, 'report_card.html', {
        'scores': page_obj,
        'page_obj': page_obj,
        'total_exams': scores.count(),
        'classes': classes,
        'subjects': subjects,
        'class_filter': class_filter or '',
        'student_filter': student_filter or '',
        'exam_filter': exam_filter or '',
    })

def _get_legacy_subject_marks(score):
    """Return subject name -> marks from legacy columns or subject_marks."""
    if score.subject_marks:
        return score.subject_marks
    return {
        'Maths': score.maths or 0,
        'Physics': score.physics or 0,
        'Chemistry': score.chemistry or 0,
        'English': score.english or 0,
        'Computer': score.computer or 0,
    }


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def add_marks(request):
    school = get_current_school(request)
    subjects = Subject.objects.filter(school=school).order_by('name')
    exam_types = ExamType.objects.filter(school=school).order_by('name')
    if request.method == "POST":
        student = get_object_or_404(Member, id=request.POST.get('student_id'), school=school)
        exam_name = request.POST.get('exam_name', '').strip() or 'Exam'
        exam_type_id = request.POST.get('exam_type_id') or None
        exam_type = ExamType.objects.filter(id=exam_type_id, school=school).first() if exam_type_id else None
        subject_marks = {}
        if subjects.exists():
            for s in subjects:
                val = request.POST.get(f'subject_{s.id}')
                if val is not None:
                    try:
                        subject_marks[s.name] = int(val)
                    except (ValueError, TypeError):
                        subject_marks[s.name] = 0
        ExamScore.objects.create(
            student=student,
            exam_name=exam_name,
            exam_type=exam_type,
            subject_marks=subject_marks if subject_marks else None,
            maths=request.POST.get('maths', 0) if not subjects.exists() else 0,
            physics=request.POST.get('physics', 0) if not subjects.exists() else 0,
            chemistry=request.POST.get('chemistry', 0) if not subjects.exists() else 0,
            english=request.POST.get('english', 0) if not subjects.exists() else 0,
            computer=request.POST.get('computer', 0) if not subjects.exists() else 0,
        )
        return redirect('report_card')
    students = Member.objects.filter(school=school).select_related('student_class').order_by('firstname')
    return render(request, 'add_marks.html', {'students': students, 'subjects': subjects, 'exam_types': exam_types})

@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF", "PARENT")
def marksheet_pdf(request, id):
    """Generate marksheet PDF synchronously (no background task required)"""
    school = get_current_school(request)
    score = get_object_or_404(ExamScore, id=id, student__school=school)
    from ..utils.roles import get_user_role
    if get_user_role(request) == "PARENT":
        profile = getattr(request.user, "userprofile", None)
        if not profile or score.student not in profile.guardian_of.all():
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("You can only view your linked students' report cards.")

    from django.utils import timezone

    subject_marks_dict = _get_legacy_subject_marks(score)
    total_obtained = sum(v for k, v in subject_marks_dict.items() if isinstance(v, (int, float)))
    total_max = len(subject_marks_dict) * 100 if subject_marks_dict else 500
    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0
    result_status = 'PASS' if total_obtained >= (total_max * 0.33) else 'FAIL'

    template = get_template('marksheet_pdf.html')
    html = template.render({
        'score': score,
        'student': score.student,
        'school': school,
        'subject_marks_dict': subject_marks_dict,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'percentage': percentage,
        'result_status': result_status,
        'date': timezone.now().date(),
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="marksheet_{score.student.firstname}_{score.exam_name}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response


# --- Subject & Exam type management ---


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def subject_list(request):
    school = get_current_school(request)
    subjects = Subject.objects.filter(school=school).order_by('name')
    if request.method == "POST" and request.POST.get('action') == 'add':
        name = request.POST.get('name', '').strip()
        code = request.POST.get('code', '').strip()
        if name:
            Subject.objects.get_or_create(school=school, name=name, defaults={'code': code})
            return redirect('subject_list')
    return render(request, 'subject_list.html', {'subjects': subjects})


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def subject_edit(request, pk):
    school = get_current_school(request)
    sub = get_object_or_404(Subject, pk=pk, school=school)
    if request.method == "POST":
        sub.name = request.POST.get('name', sub.name).strip()
        sub.code = request.POST.get('code', sub.code).strip()
        sub.save()
        return redirect('subject_list')
    return render(request, 'subject_edit.html', {'subject': sub})


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def exam_type_list(request):
    school = get_current_school(request)
    exam_types = ExamType.objects.filter(school=school).order_by('name')
    if request.method == "POST" and request.POST.get('action') == 'add':
        name = request.POST.get('name', '').strip()
        if name:
            ExamType.objects.get_or_create(school=school, name=name)
            return redirect('exam_type_list')
    return render(request, 'exam_type_list.html', {'exam_types': exam_types})


@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def exam_type_edit(request, pk):
    school = get_current_school(request)
    et = get_object_or_404(ExamType, pk=pk, school=school)
    if request.method == "POST":
        et.name = request.POST.get('name', et.name).strip()
        et.save()
        return redirect('exam_type_list')
    return render(request, 'exam_type_edit.html', {'exam_type': et})