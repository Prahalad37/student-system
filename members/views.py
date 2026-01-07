from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import render
from .models import Member, StudyMaterial, Attendance # Dono models import hone chahiye
from datetime import date
from .models import Member, Attendance  # Attendance zaroor import karo
def index(request):
    # ✅ CORRECT CHANGE: .values() hata diya taaki ye 'Objects' rahein
    mymembers = Member.objects.all()
    
    # 1. Total Students Count
    total_students = Member.objects.count()
    
    # 2. Total Revenue Logic
    revenue_data = Member.objects.aggregate(Sum('fee_paid'))
    total_revenue = revenue_data['fee_paid__sum']
    
    if total_revenue is None:
        total_revenue = 0

    # 3. Attendance Percentage Logic
    total_records = Attendance.objects.count()
    present_records = Attendance.objects.filter(status='Present').count()
    
    if total_records > 0:
        attendance_percent = round((present_records / total_records) * 100)
    else:
        attendance_percent = 0

    context = {
        'mymembers': mymembers,
        'total_students': total_students,
        'total_revenue': total_revenue,
        'attendance_percent': attendance_percent,
    }
    return render(request, 'index.html', context)

def add(request):
  template = loader.get_template('add.html')
  return HttpResponse(template.render({}, request))

def addrecord(request):
    # 1. HTML Form se Data Nikalo
    first = request.POST['first']
    last = request.POST['last']
    fee_total = request.POST['fee_total']
    fee_paid = request.POST['fee_paid']
    
    # 2. Check karo ki Image upload hui hai ya nahi
    if len(request.FILES) != 0:
        img = request.FILES['file']
        # Image ke saath save karo
        member = Member(firstname=first, lastname=last, profile_pic=img, fee_total=fee_total, fee_paid=fee_paid)
    else:
        # Bina Image ke save karo
        member = Member(firstname=first, lastname=last, fee_total=fee_total, fee_paid=fee_paid)
    
    # 3. Database me Save karo
    member.save()
    
    # 4. Wapas Dashboard par bhejo
    return HttpResponseRedirect(reverse('index'))


def delete(request, id):
  member = Member.objects.get(id=id)
  member.delete()
  return HttpResponseRedirect(reverse('index'))

def update(request, id):
  mymember = Member.objects.get(id=id)
  template = loader.get_template('update.html')
  context = {
    'mymember': mymember,
  }
  return HttpResponse(template.render(context, request))

# --- UPDATE RECORD LOGIC ---
def updaterecord(request, id):
    first = request.POST['first']
    last = request.POST['last']
    
    # 1. Fees ka data uthao
    fee_total = request.POST['fee_total']
    fee_paid = request.POST['fee_paid']

    member = Member.objects.get(id=id)
    member.firstname = first
    member.lastname = last
    
    # 2. Fees save karo
    member.fee_total = fee_total
    member.fee_paid = fee_paid

    # 3. Photo Tabhi update karo agar nayi file aayi ho
    if len(request.FILES) != 0:
        member.profile_pic = request.FILES['file']

    member.save()
    return HttpResponseRedirect(reverse('index'))

# --- NEW LIBRARY VIEW ---
def library(request):
    # Saare materials lao, latest pehle
    materials = StudyMaterial.objects.all().order_by('-created_at')
    return render(request, 'library.html', {'materials': materials})

# --- ATTENDANCE VIEW ---
def attendance(request):
    if request.method == 'POST':
        attendance_date = request.POST.get('attendance_date')
        students = Member.objects.all()

        for student in students:
            # HTML se status uthao (e.g., status_16)
            status = request.POST.get(f'status_{student.id}')

            if status:
                # Attendance save ya update karo
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': status}
                )

        return render(request, 'attendance.html', {
            'students': students, 
            'today': attendance_date, 
            'message': "Attendance Marked Successfully! ✅"
        })

    # Agar GET request hai (Page khol rahe ho)
    students = Member.objects.all()
    today = date.today().strftime('%Y-%m-%d') # Aaj ki date auto-fill ke liye
    return render(request, 'attendance.html', {'students': students, 'today': today})

# --- VIEW ATTENDANCE HISTORY ---
def attendance_records(request):
    # Saara data nikalo, latest date sabse upar (order_by -date)
    records = Attendance.objects.all().order_by('-date', 'student__firstname')
    return render(request, 'attendance_records.html', {'records': records})