import os
import sys
import django
from datetime import date, timedelta
import random
from decimal import Decimal

# Setup Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from members.models import (
    School, UserProfile, Member, ClassRoom, AcademicYear,
    TransportRoute, TransportZone, TransportStop, StudentTransport,
    Staff, Book, LibraryTransaction, FeeStructure, FeeTransaction,
    Attendance, Notice, Expense, StudyMaterial, ExamType, ExamScore
)
from django.contrib.auth.models import User

def generate_data():
    print("🚀 Starting Dummy Data Generation for Demo School...")
    
    # 1. Get/Create Demo School
    school, _ = School.objects.get_or_create(
        name="Prahlad Academy (Demo)",
        defaults={'address': 'Dummy Address', 'school_code': 'DEMO001', 'code': 'demo', 'is_demo': True}
    )
    print(f"✅ School Active: {school.name}")

    # 2. Academic Year
    ay, _ = AcademicYear.objects.get_or_create(
        school=school, name="2025-2026",
        defaults={'start_date': date(2025, 4, 1), 'end_date': date(2026, 3, 31), 'is_active': True}
    )

    # 3. ClassRooms
    classes_data = [('Class 1', 'A'), ('Class 2', 'A'), ('Class 5', 'B'), ('Class 10', 'A'), ('Class 12', 'Science')]
    class_objs = []
    for c_name, sec in classes_data:
        c_obj, _ = ClassRoom.objects.get_or_create(school=school, name=c_name, section=sec)
        class_objs.append(c_obj)
    print("✅ Classes Created")

    # 4. Staff (Teachers, Driver, Librarian)
    staff_data = [
        ("Rahul", "Sharma", "rahul@example.com", "9876543210", "Math Teacher", 45000),
        ("Priya", "Singh", "priya@example.com", "9876543211", "Science Teacher", 48000),
        ("Amit", "Verma", "amit@example.com", "9876543212", "Librarian", 30000),
        ("Suresh", "Kumar", "suresh@example.com", "9876543213", "Driver", 25000)
    ]
    staff_objs = []
    for f, l, e, p, d, s in staff_data:
        st, _ = Staff.objects.get_or_create(
            school=school, phone=p,
            defaults={'first_name': f, 'last_name': l, 'email': e, 'designation': d, 'salary': s, 'join_date': date(2023, 1, 15)}
        )
        staff_objs.append(st)
    print("✅ Staff Created")

    # 5. Transport (Routes, Zones, Stops)
    route1, _ = TransportRoute.objects.get_or_create(school=school, route_name="City Route 1", defaults={'vehicle_number': 'MP09-AB-1234', 'driver_name': 'Suresh Kumar', 'driver_phone': '9876543213'})
    route2, _ = TransportRoute.objects.get_or_create(school=school, route_name="Suburban Route 2", defaults={'vehicle_number': 'MP09-XY-9876', 'driver_name': 'Ramesh', 'driver_phone': '9988776655'})
    
    zone1, _ = TransportZone.objects.get_or_create(school=school, name="North Zone", defaults={'base_monthly_fee': 1000})
    stop1, _ = TransportStop.objects.get_or_create(school=school, zone=zone1, stop_code="STP-01", defaults={'name': 'Main Square', 'monthly_surcharge': 200})

    # 6. Students (Members) & Student Transport
    first_names = ["Arjun", "Aditi", "Karan", "Diya", "Rohan", "Neha", "Vikram", "Pooja", "Aarav", "Riya", "Sahil", "Sneha", "Kabir", "Meera", "Yash"]
    last_names = ["Patel", "Sharma", "Verma", "Rathore", "Deshmukh", "Joshi", "Iyer", "Nair", "Das", "Bose"]
    
    student_objs = []
    for i in range(15):
        fname = first_names[i]
        lname = random.choice(last_names)
        c_obj = random.choice(class_objs)
        adm_no = f"ADM-2026-{100+i}"
        
        student, _ = Member.objects.get_or_create(
            school=school, admission_no=adm_no,
            defaults={
                'firstname': fname, 'lastname': lname, 'father_name': f"Mr. {lname}",
                'mobile_number': f"91000000{i:02d}", 'student_class': c_obj,
                'gender': 'Male' if i%2==0 else 'Female', 'dob': date(2010, i%12+1, i+1),
                'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+']),
                'transport_mode': 'School Bus' if i < 5 else 'Self'
            }
        )
        student_objs.append(student)

        # Transport for first 5 students
        if i < 5:
            StudentTransport.objects.get_or_create(
                school=school, student=student,
                defaults={'route': route1, 'zone': zone1, 'stop': stop1, 'pickup_point': 'Main Square', 'monthly_fee': 1200}
            )
    print("✅ 15 Students & Transport Configured")

    # 7. Library (Books & Transactions)
    book_titles = ["Physics HC Verma", "RD Sharma Math", "Harry Potter", "Python Crash Course", "History of India"]
    books = []
    for i, t in enumerate(book_titles):
        b, _ = Book.objects.get_or_create(school=school, title=t, defaults={'author': 'Famous Author', 'isbn': f"ISBN-100{i}", 'total_copies': 5, 'available_copies': 4})
        books.append(b)

    for i in range(3):
        LibraryTransaction.objects.get_or_create(
            school=school, student=student_objs[i], book=books[i],
            defaults={'due_date': date.today() + timedelta(days=7), 'status': 'Issued'}
        )
    print("✅ Library Books & Transactions Created")

    # 8. Fees (Structures & Transactions)
    for c_obj in class_objs:
        FeeStructure.objects.get_or_create(
            school=school, class_room=c_obj, title="Tuition Fee Q1",
            defaults={'amount': 5000, 'due_date': date(2026, 4, 15)}
        )
    
    for i in range(8):
        FeeTransaction.objects.get_or_create(
            student=student_objs[i], month_year="April 2026",
            defaults={'amount_paid': 5000, 'payment_mode': 'Online', 'status': 'Paid'}
        )
    print("✅ Fees Structures & Receipts Logged")

    # 9. Attendance
    for i in range(12): # Mark 12 students present
        Attendance.objects.get_or_create(
            student=student_objs[i], date=date.today(), defaults={'status': 'Present'}
        )
    for i in range(12, 15): # Mark 3 absent
        Attendance.objects.get_or_create(
            student=student_objs[i], date=date.today(), defaults={'status': 'Absent'}
        )
    print("✅ Attendance Marked for Today")

    # 10. Exams
    exam_type, _ = ExamType.objects.get_or_create(school=school, name="Mid Term")
    for student in student_objs[:5]:
        ExamScore.objects.get_or_create(
            student=student, exam_name="Mid Term 2025", exam_type=exam_type,
            defaults={'maths': random.randint(50, 95), 'physics': random.randint(40, 90), 'chemistry': random.randint(60, 95), 'english': random.randint(70, 95), 'computer': random.randint(80, 100)}
        )
    print("✅ Exam Scores Added")

    # 11. Extras (Notices, Expenses, Study Materials)
    Notice.objects.get_or_create(school=school, title="Welcome to Term 1", defaults={'message': 'Classes begin at 8 AM daily.'})
    Notice.objects.get_or_create(school=school, title="Fee Deadline", defaults={'message': 'Please clear dues by 15th.'})
    
    Expense.objects.get_or_create(school=school, description="Electricity Bill", defaults={'amount': 15000})
    Expense.objects.get_or_create(school=school, description="Internet Setup", defaults={'amount': 3000})

    StudyMaterial.objects.get_or_create(school=school, title="Trigonometry Notes", subject="Maths", class_name="Class 10")
    print("✅ Notices, Expenses & Study Materials Added")

    print("🎉 DUMMY DATA GENERATION COMPLETE! Dashboard is ready for testing.")

if __name__ == "__main__":
    generate_data()
