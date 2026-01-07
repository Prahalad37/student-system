import openpyxl  # <--- Ye line add karo top par
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.template.loader import get_template
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from datetime import date
from xhtml2pdf import pisa
from .models import Member, Attendance, StudyMaterial, ExamScore, Notice, Expense
import xlwt
# --- DASHBOARD ---
@login_required
def index(request):
    # 1. Basic Data
    mymembers = Member.objects.all()
    total_students = Member.objects.count()
    notices = Notice.objects.all().order_by('-created_at')

    # 2. Revenue (Income)
    revenue_data = Member.objects.aggregate(Sum('fee_paid'))
    total_revenue = revenue_data['fee_paid__sum'] if revenue_data['fee_paid__sum'] else 0

    # 3. Expenses (Kharche) - NEW LOGIC ✅
    expense_data = Expense.objects.aggregate(Sum('amount'))
    total_expense = expense_data['amount__sum'] if expense_data['amount__sum'] else 0

    # 4. Net Profit (Income - Expense) - NEW LOGIC ✅
    net_profit = total_revenue - total_expense

    # 5. Attendance
    total_records = Attendance.objects.count()
    present_records = Attendance.objects.filter(status='Present').count()
    attendance_percent = round((present_records / total_records) * 100) if total_records > 0 else 0

    context = {
        'mymembers': mymembers,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'total_expense': total_expense, # <-- New
        'net_profit': net_profit,       # <-- New
        'attendance_percent': attendance_percent,
        'notices': notices,
    }
    return render(request, 'index.html', context)
# --- STUDENT MANAGEMENT (Add, Delete, Update) ---
@login_required
def add(request):
    template = loader.get_template('add.html')
    return HttpResponse(template.render({}, request))

@login_required
def addrecord(request):
    first = request.POST['first']
    last = request.POST['last']
    fee_total = request.POST['fee_total']
    fee_paid = request.POST['fee_paid']
    
    if len(request.FILES) != 0:
        img = request.FILES['file']
        member = Member(firstname=first, lastname=last, profile_pic=img, fee_total=fee_total, fee_paid=fee_paid)
    else:
        member = Member(firstname=first, lastname=last, fee_total=fee_total, fee_paid=fee_paid)
    
    member.save()
    return HttpResponseRedirect(reverse('index'))

@login_required
def delete(request, id):
    member = get_object_or_404(Member, id=id)
    member.delete()
    return HttpResponseRedirect(reverse('index'))

@login_required
def update(request, id):
    mymember = get_object_or_404(Member, id=id)
    template = loader.get_template('update.html')
    context = {'mymember': mymember}
    return HttpResponse(template.render(context, request))

@login_required
def updaterecord(request, id):
    first = request.POST['first']
    last = request.POST['last']
    fee_total = request.POST['fee_total']
    fee_paid = request.POST['fee_paid']

    member = get_object_or_404(Member, id=id)
    member.firstname = first
    member.lastname = last
    member.fee_total = fee_total
    member.fee_paid = fee_paid

    if len(request.FILES) != 0:
        member.profile_pic = request.FILES['file']

    member.save()
    return HttpResponseRedirect(reverse('index'))

# --- ATTENDANCE SYSTEM ---
@login_required
def attendance(request):
    if request.method == "POST":
        selected_date = request.POST.get('date')
        all_students = Member.objects.all()
        
        for student in all_students:
            status_value = request.POST.get(f'status_{student.id}')
            if status_value:
                Attendance.objects.update_or_create(
                    student=student,
                    date=selected_date,
                    defaults={'status': status_value}
                )
        return redirect('attendance_records')

    mymembers = Member.objects.all()
    return render(request, 'attendance.html', {'mymembers': mymembers})

@login_required
def attendance_records(request):
    records = Attendance.objects.all().order_by('-date', 'student__firstname')
    return render(request, 'attendance_records.html', {'records': records})

# --- DIGITAL LIBRARY ---
@login_required
def library(request):
    if request.method == "POST":
        title = request.POST.get('title')
        subject = request.POST.get('subject')
        class_name = request.POST.get('class_name')
        video_link = request.POST.get('video_link')
        
        pdf_file = None
        if request.FILES.get('pdf_file'):
            pdf = request.FILES['pdf_file']
            fs = FileSystemStorage()
            filename = fs.save(pdf.name, pdf)
            pdf_file = fs.url(filename)

        StudyMaterial.objects.create(
            title=title, subject=subject, class_name=class_name,
            video_link=video_link, pdf_file=pdf_file
        )
        return redirect('library')

    materials = StudyMaterial.objects.all().order_by('-created_at')
    return render(request, 'library.html', {'materials': materials})

# --- EXAMS & RESULTS ---
@login_required
def add_marks(request):
    if request.method == "POST":
        student_id = request.POST.get('student_id')
        exam_name = request.POST.get('exam_name')
        
        student = get_object_or_404(Member, id=student_id)
        
        ExamScore.objects.create(
            student=student, exam_name=exam_name,
            maths=request.POST.get('maths'),
            physics=request.POST.get('physics'),
            chemistry=request.POST.get('chemistry'),
            english=request.POST.get('english'),
            computer=request.POST.get('computer')
        )
        return redirect('report_card')

    students = Member.objects.all()
    return render(request, 'add_marks.html', {'students': students})

@login_required
def report_card(request):
    scores = ExamScore.objects.all().order_by('-created_at')
    return render(request, 'report_card.html', {'scores': scores})

# --- STUDENT PROFILE ---
@login_required
def student_profile(request, id):
    student = get_object_or_404(Member, id=id)
    exams = ExamScore.objects.filter(student=student).order_by('-created_at')
    attendance_list = Attendance.objects.filter(student=student).order_by('-date')
    
    total_days = attendance_list.count()
    present_days = attendance_list.filter(status='Present').count()
    
    if total_days > 0:
        attendance_percent = round((present_days / total_days) * 100, 1)
    else:
        attendance_percent = 0
        
    context = {
        'student': student,
        'exams': exams,
        'attendance_list': attendance_list,
        'attendance_percent': attendance_percent,
        'present_days': present_days,
        'total_days': total_days
    }
    return render(request, 'student_profile.html', context)

# --- FEE RECEIPT PDF ---
@login_required
def receipt_pdf(request, id):
    student = get_object_or_404(Member, id=id)
    context = {
        'student': student,
        'date': date.today(),
        'receipt_no': f"REC-{student.id}-{date.today().strftime('%m%d')}"
    }
    
    template_path = 'receipt_pdf.html'
    template = get_template(template_path)
    html = template.render(context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Receipt_{student.firstname}.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse(f'PDF Error: <pre>{html}</pre>')
    return response

# --- NOTICE BOARD ACTIONS ---
@login_required
def add_notice(request):
    if request.method == "POST":
        title = request.POST.get('title')
        message = request.POST.get('message')
        Notice.objects.create(title=title, message=message)
    return redirect('index')

@login_required
def delete_notice(request, id):
    notice = get_object_or_404(Notice, id=id)
    notice.delete()
    return redirect('index')
@login_required
def id_card(request, id):
    student = get_object_or_404(Member, id=id)
    return render(request, 'id_card.html', {'student': student})
# Expense Model import karna mat bhoolna upar
# from .models import Expense

@login_required
def add_expense(request):
    if request.method == "POST":
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        Expense.objects.create(description=description, amount=amount)
        return redirect('index')
    return render(request, 'add_expense.html')

@login_required
def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Student_List.xls"'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Students')

    # Sheet Header (Pehli Line)
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['ID', 'First Name', 'Last Name', 'Total Fees', 'Paid Fees', 'Due Amount']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet Body (Data)
    font_style = xlwt.XFStyle()
    rows = Member.objects.all().values_list('id', 'firstname', 'lastname', 'fee_total', 'fee_paid')

    for row in rows:
        row_num += 1
        # Calculate Due Amount manually (Total - Paid)
        due_amount = row[3] - row[4]
        
        # Row ko list mein convert karke Due Amount add karo
        row_data = list(row)
        row_data.append(due_amount)

        for col_num in range(len(row_data)):
            ws.write(row_num, col_num, row_data[col_num], font_style)

    wb.save(response)
    return response

@login_required
def import_students(request):
    if request.method == "POST" and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        
        # Workbook load karo
        wb = openpyxl.load_workbook(excel_file)
        worksheet = wb.active
        
        # Loop chalao (Row 2 se shuru kyunki Row 1 header hai)
        for row in worksheet.iter_rows(min_row=2, values_only=True):
            # Excel columns: A=Firstname, B=Lastname, C=Total Fees, D=Paid Fees
            first_name = row[0]
            last_name = row[1]
            fee_total = row[2]
            fee_paid = row[3]
            
            if first_name: # Agar naam hai tabhi save karo
                Member.objects.create(
                    firstname=first_name,
                    lastname=last_name,
                    fee_total=fee_total if fee_total else 0,
                    fee_paid=fee_paid if fee_paid else 0
                )
        
        return redirect('index')

    return render(request, 'import_students.html')