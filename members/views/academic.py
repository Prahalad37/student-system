from datetime import date
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.utils.html import format_html
from xhtml2pdf import pisa
from ..models import Member, Attendance, ClassRoom, ExamScore
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
        'student', 'student__student_class'
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
    classes = ClassRoom.objects.filter(school=school).order_by('name')

    return render(request, 'report_card.html', {
        'scores': page_obj,
        'page_obj': page_obj,
        'total_exams': scores.count(),
        'classes': classes,
        'class_filter': class_filter or '',
        'student_filter': student_filter or '',
        'exam_filter': exam_filter or '',
    })

@login_required
@require_roles("OWNER", "ADMIN", "TEACHER")
def add_marks(request):
    school = get_current_school(request)
    if request.method == "POST":
        student = get_object_or_404(Member, id=request.POST.get('student_id'), school=school)
        ExamScore.objects.create(
            student=student,
            exam_name=request.POST.get('exam_name'),
            maths=request.POST.get('maths', 0), physics=request.POST.get('physics', 0),
            chemistry=request.POST.get('chemistry', 0), english=request.POST.get('english', 0),
            computer=request.POST.get('computer', 0)
        )
        return redirect('report_card')
    students = Member.objects.filter(school=school).order_by('firstname')
    return render(request, 'add_marks.html', {'students': students})

@login_required
@require_roles("OWNER", "ADMIN", "TEACHER", "STAFF")
def marksheet_pdf(request, id):
    """Generate marksheet PDF synchronously (no background task required)"""
    school = get_current_school(request)
    score = get_object_or_404(ExamScore, id=id, student__school=school)
    
    from django.utils import timezone
    total_obtained = (score.maths or 0) + (score.physics or 0) + (score.chemistry or 0) + (score.english or 0) + (score.computer or 0)
    total_max = 500
    percentage = round((total_obtained / total_max) * 100, 2) if total_max > 0 else 0
    result_status = 'PASS' if total_obtained >= 165 else 'FAIL'

    template = get_template('marksheet_pdf.html')
    html = template.render({
        'score': score,
        'student': score.student,
        'school': school,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'percentage': percentage,
        'result_status': result_status,
        'date': timezone.now().date(),
    })
    
    # Generate PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="marksheet_{score.student.firstname}_{score.exam_name}.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response