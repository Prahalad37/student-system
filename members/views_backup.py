import openpyxl
import xlwt
import datetime
from datetime import date
from decimal import Decimal

# Django Core Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.template import loader
from django.template.loader import get_template
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

# Third-Party Imports
from xhtml2pdf import pisa

# Utils
from .utils import get_current_school

# REST Framework Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import StudentSerializer

# Local App Imports
from .models import (
    Member, Attendance, Notice, Expense, ClassRoom, 
    School, Payment, UserProfile,
    StudyMaterial, ExamScore,
    Book, LibraryTransaction,
    TransportRoute, StudentTransport,
    Staff, SalaryTransaction,
    FeeStructure, FeeTransaction 
)

# ==========================================
# 1. DASHBOARD
# ==========================================
@login_required
def index(request):
    """The Command Center: Aggregates data from all modules"""
    
    # 1. Student Stats
    total_students = Member.objects.count()
    new_admissions = Member.objects.filter(joined_date__month=date.today().month).count()
    
    # 2. Financial Health (Live Calculation)
    revenue_stats = Member.objects.aggregate(
        total_expected=Sum('fee_total'),
        total_collected=Sum('fee_paid')
    )
    total_revenue = revenue_stats['total_collected'] or 0
    pending_dues = (revenue_stats['total_expected'] or 0) - total_revenue
    
    # Recent Fee Transactions (Last 5)
    recent_transactions = FeeTransaction.objects.select_related('student').order_by('-payment_date')[:5]

    # 3. Operational Stats
    students_on_bus = StudentTransport.objects.count()
    books_issued = LibraryTransaction.objects.filter(status='Issued').count()
    total_staff = Staff.objects.filter(is_active=True).count()

    context = {
        'total_students': total_students,
        'new_admissions': new_admissions,
        'total_revenue': total_revenue,
        'pending_dues': pending_dues,
        'students_on_bus': students_on_bus,
        'books_issued': books_issued,
        'total_staff': total_staff,
        'recent_transactions': recent_transactions,
        'notices': Notice.objects.all().order_by('-id')[:3]
    }
    return render(request, 'index.html', context)

# ==========================================
# 2. STUDENT MANAGEMENT
# ==========================================
@login_required
def all_students(request):
    mymembers = Member.objects.all().order_by('firstname')
    return render(request, 'all_students.html', {'mymembers': mymembers})

@login_required
def student_profile(request, id):
    student = get_object_or_404(Member, id=id)
    exams = ExamScore.objects.filter(student=student).order_by('-id')
    attendance_list = Attendance.objects.filter(student=student).order_by('-date')
    total_days = attendance_list.count()
    present_days = attendance_list.filter(status='Present').count()
    attendance_percent = round((present_days / total_days) * 100, 1) if total_days > 0 else 0

    context = {
        'student': student, 'exams': exams, 'attendance_list': attendance_list,
        'attendance_percent': attendance_percent, 'present_days': present_days, 'total_days': total_days
    }
    return render(request, 'student_profile.html', context)

@login_required
def add(request):
    return render(request, 'add.html')

@login_required
def addrecord(request):
    if request.method == "POST":
        class_name = request.POST.get('student_class')
        section_name = request.POST.get('section') or 'A'
        
        class_obj = None
        if class_name:
            class_obj, created = ClassRoom.objects.get_or_create(name=class_name, section=section_name)

        Member.objects.create(
            firstname=request.POST['first'], lastname=request.POST['last'], 
            father_name=request.POST.get('father_name'), mobile_number=request.POST.get('mobile_number'), 
            email=request.POST.get('email'), admission_no=request.POST.get('admission_no'),
            joined_date=request.POST.get('joined_date') or None, roll_number=request.POST.get('roll_number'), 
            gender=request.POST.get('gender') or 'Male', dob=request.POST.get('dob') or None, 
            address=request.POST.get('address'), student_class=class_obj,
            house_team=request.POST.get('house_team'), preferred_stream=request.POST.get('preferred_stream'), 
            blood_group=request.POST.get('blood_group'), medical_conditions=request.POST.get('medical_conditions'), 
            transport_mode=request.POST.get('transport_mode'), route_name=request.POST.get('route_name'),
            fee_total=request.POST.get('fee_total', 0), fee_paid=request.POST.get('fee_paid', 0), 
            profile_pic=request.FILES.get('file')
        )
        return HttpResponseRedirect(reverse('index'))
    return redirect('add')

@login_required
def delete(request, id):
    member = get_object_or_404(Member, id=id)
    member.delete()
    return HttpResponseRedirect(reverse('index'))

@login_required
def update(request, id):
    mymember = get_object_or_404(Member, id=id)
    return render(request, 'update.html', {'mymember': mymember})

@login_required
def updaterecord(request, id):
    if request.method == "POST":
        member = get_object_or_404(Member, id=id)
        member.firstname = request.POST['first']; member.lastname = request.POST['last']
        member.father_name = request.POST.get('father_name'); member.mobile_number = request.POST.get('mobile_number')
        member.email = request.POST.get('email'); member.address = request.POST.get('address')
        member.admission_no = request.POST.get('admission_no'); member.roll_number = request.POST.get('roll_number')
        member.gender = request.POST.get('gender')
        
        if request.POST.get('joined_date'): member.joined_date = request.POST.get('joined_date')
        if request.POST.get('dob'): member.dob = request.POST.get('dob')
        
        class_name = request.POST.get('student_class')
        section_name = request.POST.get('section') or 'A'
        if class_name:
            class_obj, created = ClassRoom.objects.get_or_create(name=class_name, section=section_name)
            member.student_class = class_obj
            
        member.house_team = request.POST.get('house_team')
        member.preferred_stream = request.POST.get('preferred_stream')
        member.blood_group = request.POST.get('blood_group')
        member.medical_conditions = request.POST.get('medical_conditions')
        member.transport_mode = request.POST.get('transport_mode')
        member.route_name = request.POST.get('route_name')
        member.fee_total = request.POST.get('fee_total', 0)
        member.fee_paid = request.POST.get('fee_paid', 0)
        
        if request.FILES.get('file'): member.profile_pic = request.FILES['file']
        
        member.save()
        return HttpResponseRedirect(reverse('index'))
    return redirect('index')

# ==========================================
# 3. ATTENDANCE (FIXED: Linked via Student)
# ==========================================

@login_required
def attendance(request):
    """Crash-Proof Attendance Register"""
    school = get_current_school(request)
    classes = ClassRoom.objects.filter(school=school)
    
    # 1. INPUT SANITIZATION
    raw_class_id = request.GET.get('class_id')
    selected_date = request.GET.get('date') or date.today().isoformat()
    
    selected_class_id = None
    
    # Check if ID is valid number, ignore 'None' string
    if raw_class_id and raw_class_id not in ['None', '', 'null']:
        try:
            selected_class_id = int(raw_class_id)
        except (ValueError, TypeError):
            selected_class_id = None

    # 2. FETCH STUDENTS
    students = []
    if selected_class_id:
        students = Member.objects.filter(school=school, student_class_id=selected_class_id).order_by('firstname')
        
        # Check existing attendance (FIXED: student__school instead of school)
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
        
        # Safety for Redirect URL
        if not class_input or class_input in ['None', '']:
            class_input = ''
            
        student_ids = request.POST.getlist('student_ids')
        if student_ids:
            students_to_mark = Member.objects.filter(id__in=student_ids)
            for student in students_to_mark:
                status = request.POST.get(f'status_{student.id}')
                if status:
                    # FIXED: Removed 'school=school' from create/update
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
def attendance_records(request):
    """View Historical Attendance Logs"""
    school = get_current_school(request)
    
    # 1. Get Filter Parameters
    date_filter = request.GET.get('date')
    class_filter = request.GET.get('class_id')
    
    # 2. Base Query (FIXED: student__school instead of school)
    records = Attendance.objects.filter(student__school=school).select_related('student', 'student__student_class').order_by('-date', 'student__firstname')
    
    # 3. Apply Filters
    if date_filter:
        records = records.filter(date=date_filter)
    
    if class_filter and class_filter not in ['None', '']:
        records = records.filter(student__student_class_id=class_filter)
    
    # 4. Limit results if no filter
    if not date_filter and not class_filter:
        records = records[:50]

    classes = ClassRoom.objects.filter(school=school)

    context = {
        'records': records,
        'classes': classes,
        'selected_date': date_filter,
        'selected_class': int(class_filter) if class_filter and class_filter.isdigit() else None
    }
    return render(request, 'attendance_records.html', context)

# ==========================================
# 4. DIGITAL LIBRARY
# ==========================================
@login_required
def digital_library(request): 
    if request.method == "POST":
        pdf_file = None
        if request.FILES.get('pdf_file'):
            fs = FileSystemStorage()
            pdf_file = fs.url(fs.save(request.FILES['pdf_file'].name, request.FILES['pdf_file']))
        StudyMaterial.objects.create(
            title=request.POST.get('title'), subject=request.POST.get('subject'), 
            class_name=request.POST.get('class_name'), video_link=request.POST.get('video_link'),
            pdf_file=pdf_file
        )
        return redirect('digital_library')
    materials = StudyMaterial.objects.all().order_by('-id')
    return render(request, 'library.html', {'materials': materials})

# ==========================================
# 5. EXAMS & REPORT CARDS
# ==========================================
@login_required
def report_card(request):
    """Dashboard for Exam Results"""
    school = get_current_school(request)
    scores = ExamScore.objects.filter(student__school=school).select_related('student').order_by('-id')
    
    context = {
        'scores': scores,
        'total_exams': scores.count(),
    }
    return render(request, 'report_card.html', context)

@login_required
def add_marks(request):
    """Entry Form with Auto-Calculation"""
    school = get_current_school(request)
    
    if request.method == "POST":
        student = get_object_or_404(Member, id=request.POST.get('student_id'))
        
        ExamScore.objects.create(
            student=student,
            exam_name=request.POST.get('exam_name'),
            maths=request.POST.get('maths', 0),
            physics=request.POST.get('physics', 0),
            chemistry=request.POST.get('chemistry', 0),
            english=request.POST.get('english', 0),
            computer=request.POST.get('computer', 0)
        )
        return redirect('report_card')
        
    # Send all students for the dropdown
    students = Member.objects.filter(school=school).order_by('firstname')
    return render(request, 'add_marks.html', {'students': students})

@login_required
def marksheet_pdf(request, id):
    """Generate Professional PDF Report Card"""
    score = get_object_or_404(ExamScore, id=id)
    
    # Calculate Totals
    total_obtained = score.maths + score.physics + score.chemistry + score.english + score.computer
    total_max = 500
    percentage = round((total_obtained / total_max) * 100, 2)
    
    # Determine Grade
    if percentage >= 90: grade = "A+"
    elif percentage >= 80: grade = "A"
    elif percentage >= 70: grade = "B"
    elif percentage >= 60: grade = "C"
    elif percentage >= 50: grade = "D"
    else: grade = "F"

    result_status = "PASS" if percentage >= 33 else "FAIL"

    context = {
        'score': score,
        'student': score.student,
        'total_obtained': total_obtained,
        'total_max': total_max,
        'percentage': percentage,
        'grade': grade,
        'result_status': result_status,
        'date': date.today(),
        'school': get_current_school(request)
    }
    
    # Render PDF
    template = get_template('marksheet_pdf.html')
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename="Report_{score.student.firstname}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

# ==========================================
# 6. EXPENSES
# ==========================================
@login_required
def add_expense(request):
    if request.method == "POST":
        Expense.objects.create(description=request.POST.get('description'), amount=request.POST.get('amount'))
        return redirect('add_expense')
    expenses = Expense.objects.all().order_by('-id')
    return render(request, 'add_expense.html', {'expenses': expenses})

# ==========================================
# 7. PHYSICAL LIBRARY
# ==========================================
@login_required
def library(request):
    school = get_current_school(request)
    
    if request.user.is_superuser:
        books = Book.objects.all()
    else:
        books = Book.objects.filter(school=school)
        
    transactions = LibraryTransaction.objects.filter(status='Issued')
    
    # All students for Dropdown
    all_students = Member.objects.all().order_by('firstname')

    context = {
        'books': books,
        'transactions': transactions,
        'total_books': books.count(),
        'issued_books': transactions.count(),
        'all_students': all_students
    }
    return render(request, 'library.html', context)

@login_required
def add_book(request):
    if request.method == "POST":
        Book.objects.create(
            school=get_current_school(request),
            title=request.POST['title'], author=request.POST['author'],
            isbn=request.POST.get('isbn', ''), total_copies=int(request.POST['copies']),
            available_copies=int(request.POST['copies'])
        )
    return redirect('/library/')

@login_required
def issue_book(request):
    if request.method == "POST":
        try:
            student_id = request.POST.get('student_id')
            book_id = request.POST.get('book_id')
            due_date = request.POST.get('due_date')
            
            student = get_object_or_404(Member, id=student_id)
            book = get_object_or_404(Book, id=book_id)

            if book.available_copies > 0:
                LibraryTransaction.objects.create(
                    school=get_current_school(request),
                    student=student,
                    book=book,
                    due_date=due_date,
                    status='Issued'
                )
                book.available_copies -= 1
                book.save()
                return redirect('/library/')
            else:
                return HttpResponse("Book out of stock!")
        except Exception as e:
            return HttpResponse(f"Error: {e}. Check Student ID.")
    return redirect('/library/')

@login_required
def return_book(request, id):
    trans = get_object_or_404(LibraryTransaction, id=id)
    if trans.status == 'Issued':
        trans.status = "Returned"; trans.return_date = date.today()
        if trans.return_date > trans.due_date:
            trans.fine_amount = (trans.return_date - trans.due_date).days * 10
        trans.save()
        book = trans.book; book.available_copies += 1; book.save()
    return redirect('/library/')

@login_required
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    pending_issues = LibraryTransaction.objects.filter(book=book, status='Issued').exists()
    if pending_issues:
        return HttpResponse("Cannot delete book with pending issues.")
    book.delete()
    return redirect('/library/')

@login_required
def export_library_history(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Library_Report.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Library')
    columns = ['Student', 'Book', 'Issue Date', 'Due Date', 'Status', 'Fine']
    for col, name in enumerate(columns): ws.write(0, col, name)
    for row, t in enumerate(LibraryTransaction.objects.all(), 1):
        ws.write(row, 0, f"{t.student.firstname} {t.student.lastname}")
        ws.write(row, 1, t.book.title)
        ws.write(row, 2, str(t.issue_date))
        ws.write(row, 3, str(t.due_date))
        ws.write(row, 4, t.status)
        ws.write(row, 5, t.fine_amount)
    wb.save(response)
    return response

# ==========================================
# 8. FINANCE
# ==========================================
@login_required
def fee_home(request):
    transactions = FeeTransaction.objects.all().select_related('student').order_by('-payment_date')
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    class_filter = request.GET.get('class_id')
    mode_filter = request.GET.get('mode')

    if start_date: transactions = transactions.filter(payment_date__gte=start_date)
    if end_date: transactions = transactions.filter(payment_date__lte=end_date)
    if class_filter: transactions = transactions.filter(student__student_class__id=class_filter)
    if mode_filter: transactions = transactions.filter(payment_mode=mode_filter)

    total_collected = transactions.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    students = Member.objects.annotate(balance=F('fee_total') - F('fee_paid')).order_by('-balance')

    context = {
        'transactions': transactions, 'total_collected': total_collected,
        'classes': ClassRoom.objects.all(), 'students': students
    }
    return render(request, 'fees.html', context)

@login_required
def collect_fee(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        amount = request.POST.get('amount')
        mode = request.POST.get('mode')
        date_paid = request.POST.get('date')
        
        student = get_object_or_404(Member, id=student_id)
        
        FeeTransaction.objects.create(
            student=student, amount_paid=amount, payment_mode=mode,
            payment_date=date_paid, month_year="Current", status="Paid"
        )
        
        student.fee_paid += Decimal(amount)
        student.save()
        
    return redirect('fee_home')

@login_required
def fee_config(request):
    if request.method == "POST":
        FeeStructure.objects.create(
            school=get_current_school(request),
            class_room=ClassRoom.objects.get(id=request.POST.get('class_id')),
            title=request.POST.get('title'), amount=request.POST.get('amount')
        )
    return redirect('fee_home')

@login_required
def generate_monthly_dues(request):
    if request.method == "POST":
        for student in Member.objects.all():
            fee = FeeStructure.objects.filter(class_room=student.student_class).aggregate(Sum('amount'))['amount__sum']
            if fee: student.fee_total += fee; student.save()
    return redirect('fee_home')

@login_required
def receipt_pdf(request, id):
    t = get_object_or_404(FeeTransaction, id=id)
    template = get_template('receipt_pdf.html')
    html = template.render({'t': t})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response

@login_required
def delete_fee(request, id):
    if request.user.is_superuser:
        t = get_object_or_404(FeeTransaction, id=id)
        t.student.fee_paid -= t.amount_paid; t.student.save(); t.delete()
    return redirect('fee_home')

@login_required
def get_fee_amount(request):
    return JsonResponse({'amount': 0}) 

# ==========================================
# 9. HR & PAYROLL
# ==========================================
@login_required
def staff_list(request):
    school = get_current_school(request)
    staff_members = Staff.objects.filter(school=school, is_active=True)
    salary_history = SalaryTransaction.objects.select_related('staff').filter(school=school).order_by('-payment_date')[:50]
    total_staff = staff_members.count()
    monthly_payroll_est = staff_members.aggregate(Sum('salary'))['salary__sum'] or 0

    context = {
        'staff_members': staff_members,
        'salary_history': salary_history,
        'total_staff': total_staff,
        'monthly_payroll_est': monthly_payroll_est
    }
    return render(request, 'hr_staff.html', context)

@login_required
def add_staff(request):
    if request.method == "POST":
        Staff.objects.create(
            school=get_current_school(request), first_name=request.POST['first_name'], 
            last_name=request.POST['last_name'], phone=request.POST['phone'], 
            designation=request.POST['designation'], salary=request.POST['salary'], 
            join_date=request.POST['join_date']
        )
    return redirect('staff_list')

@login_required
def pay_salary(request):
    if request.method == "POST":
        staff = get_object_or_404(Staff, id=request.POST.get('staff_id'))
        SalaryTransaction.objects.create(school=staff.school, staff=staff, amount_paid=request.POST.get('amount'), month_year=request.POST.get('month_year'), payment_date=request.POST.get('payment_date'), payment_mode=request.POST.get('mode'))
    return redirect('staff_list')

@login_required
def salary_slip_pdf(request, id):
    t = get_object_or_404(SalaryTransaction, id=id)
    template = get_template('salary_slip_pdf.html')
    html = template.render({'t': t, 'school': t.school})
    response = HttpResponse(content_type='application/pdf')
    pisa.CreatePDF(html, dest=response)
    return response

# ==========================================
# 10. TRANSPORT
# ==========================================
@login_required
def transport_home(request):
    routes = TransportRoute.objects.all()
    transport_students = StudentTransport.objects.select_related('student', 'route').all()
    
    total_buses = routes.count()
    students_on_bus = transport_students.count()
    total_revenue = transport_students.aggregate(Sum('monthly_fee'))['monthly_fee__sum'] or 0
    
    assigned_ids = transport_students.values_list('student_id', flat=True)
    available_students = Member.objects.exclude(id__in=assigned_ids)

    context = {
        'routes': routes,
        'transport_students': transport_students,
        'students': available_students, # For Dropdown
        'total_buses': total_buses,
        'students_on_bus': students_on_bus,
        'total_revenue': total_revenue
    }
    return render(request, 'transport.html', context)

@login_required
def add_route(request):
    if request.method == "POST":
        TransportRoute.objects.create(
            school=get_current_school(request),
            route_name=request.POST.get('route_name'),
            vehicle_number=request.POST.get('vehicle_number'),
            driver_name=request.POST.get('driver_name'),
            driver_phone=request.POST.get('driver_phone')
        )
    return redirect('transport_home')

@login_required
def transport_assign(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        route_id = request.POST.get('route_id')
        pickup = request.POST.get('pickup_point')
        fee = request.POST.get('monthly_fee')
        
        student = get_object_or_404(Member, id=student_id)
        route = get_object_or_404(TransportRoute, id=route_id)
        
        StudentTransport.objects.update_or_create(
            school=get_current_school(request),
            student=student,
            defaults={
                'route': route,
                'pickup_point': pickup,
                'monthly_fee': fee
            }
        )
        
        student.transport_mode = 'School Bus'
        student.route_name = route.route_name
        student.save()
        
    return redirect('transport_home')

# ==========================================
# 11. UTILS & OTHERS
# ==========================================
@login_required
def add_notice(request):
    if request.method == "POST":
        Notice.objects.create(title=request.POST.get('title'), message=request.POST.get('message'))
    return redirect('index')

@login_required
def delete_notice(request, id):
    get_object_or_404(Notice, id=id).delete()
    return redirect('index')

@login_required
def id_card(request, id):
    return render(request, 'id_card.html', {'student': get_object_or_404(Member, id=id)})

@login_required
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Students.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Students')
    for col, name in enumerate(['ID', 'Name', 'Class', 'Total Fee', 'Paid']): ws.write(0, col, name)
    for row, m in enumerate(Member.objects.all(), 1):
        ws.write(row, 0, m.id); ws.write(row, 1, m.firstname); ws.write(row, 2, str(m.student_class))
        ws.write(row, 3, m.fee_total); ws.write(row, 4, m.fee_paid)
    wb.save(response)
    return response

@login_required
def import_students(request):
    return render(request, 'import_students.html')

# ==========================================
# 12. API
# ==========================================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_api_list(request):
    students = Member.objects.all()
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)