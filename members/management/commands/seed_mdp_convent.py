"""
Seed MDP Convent school with 100 students and data for all ERP modules.
Usage: python manage.py seed_mdp_convent
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import date, timedelta, time
import random

from members.models import (
    School,
    ClassRoom,
    AcademicYear,
    Subject,
    ExamType,
    Member,
    Staff,
    FeeStructure,
    FeeTransaction,
    Book,
    LibraryTransaction,
    TransportRoute,
    StudentTransport,
    Attendance,
    ExamScore,
    Notice,
    SalaryTransaction,
    Expense,
    StudyMaterial,
    AdmissionEnquiry,
    TimeSlot,
    TimetableEntry,
    Notification,
)
from members.models import UserProfile

User = get_user_model()

FIRST_NAMES = [
    "Rajesh", "Priya", "Amit", "Sneha", "Vikram", "Anita", "Rohit", "Kavita",
    "Arjun", "Meera", "Karan", "Pooja", "Sanjay", "Neha", "Rahul", "Swati",
    "Vivek", "Divya", "Ravi", "Kirti", "Suresh", "Pallavi", "Manoj", "Anjali",
    "Deepak", "Shweta", "Nitin", "Ritu", "Ajay", "Preeti", "Sunil", "Nidhi",
    "Ramesh", "Komal", "Vijay", "Simran", "Prakash", "Rekha", "Anil", "Sapna",
    "Sachin", "Kavya", "Rahul", "Ishita", "Varun", "Tanvi", "Gaurav", "Nisha",
]
LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Singh", "Gupta", "Verma", "Yadav", "Reddy",
    "Joshi", "Malhotra", "Nair", "Desai", "Iyer", "Kapoor", "Shah", "Rao",
    "Mehta", "Pillai", "Sinha", "Chopra", "Dubey", "Mishra", "Jain", "Saxena",
]


class Command(BaseCommand):
    help = "Seeds MDP Convent with 100 students and data for all modules"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Seeding MDP Convent...\n"))

        # 1. School
        school, created = School.objects.get_or_create(
            code="mdp-convent",
            defaults={
                "name": "MDP Convent",
                "address": "MDP Convent, St. Mary Road, City - 400001",
                "school_code": "MDP001",
            },
        )
        if created:
            self.stdout.write("Created school: MDP Convent")
        else:
            self.stdout.write("Using existing school: MDP Convent")

        # 2. Classes (MDP-prefixed to avoid unique_together clash with other schools)
        self.stdout.write("Creating classes...")
        classes_data = [
            ("MDP 6", "A"), ("MDP 7", "A"), ("MDP 8", "A"), ("MDP 9", "A"), ("MDP 10", "A"),
            ("MDP 11", "Science"), ("MDP 12", "Science"), ("MDP 11", "Commerce"), ("MDP 12", "Commerce"),
        ]
        classes = []
        for name, section in classes_data:
            cls, _ = ClassRoom.objects.get_or_create(
                school=school,
                name=name,
                section=section,
            )
            classes.append(cls)

        # 3. AcademicYear
        ay, _ = AcademicYear.objects.get_or_create(
            school=school,
            name="2025-26",
            defaults={
                "start_date": date(2025, 4, 1),
                "end_date": date(2026, 3, 31),
                "is_active": True,
            },
        )
        AcademicYear.objects.filter(school=school).exclude(id=ay.id).update(is_active=False)

        # 4. Subject & ExamType
        subject_names = ["Maths", "Physics", "Chemistry", "English", "Hindi", "Computer"]
        subjects = []
        for sname in subject_names:
            sub, _ = Subject.objects.get_or_create(school=school, name=sname, defaults={"code": sname[:3].upper()})
            subjects.append(sub)
        exam_types = []
        for ename in ["Unit Test", "Mid-Term", "Final"]:
            et, _ = ExamType.objects.get_or_create(school=school, name=ename)
            exam_types.append(et)

        # 5. 100 Students
        self.stdout.write("Creating 100 students...")
        students = []
        for i in range(100):
            student = Member.objects.create(
                school=school,
                admission_no=f"MDP2025{1000 + i}",
                firstname=random.choice(FIRST_NAMES),
                lastname=random.choice(LAST_NAMES),
                father_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                mobile_number=f"98765{43210 + (i % 100000)}",
                email=f"mdp.student{i}@mdpconvent.edu",
                student_class=random.choice(classes),
                roll_number=str((i % 40) + 1),
                gender=random.choice(["Male", "Female"]),
                dob=date(2008 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                address=f"{random.randint(1, 150)} St. Mary Road, City",
                blood_group=random.choice(["A+", "B+", "O+", "AB+", "A-", "B-", "O-"]),
                fee_total=22000,
                fee_paid=random.randint(0, 22000),
            )
            students.append(student)

        # 6. Staff
        self.stdout.write("Creating staff...")
        staff_data = [
            ("John", "Principal", "Principal"),
            ("Rahul", "Sharma", "Physics Teacher"),
            ("Priya", "Patel", "Mathematics Teacher"),
            ("Amit", "Kumar", "Chemistry Teacher"),
            ("Sneha", "Verma", "English Teacher"),
            ("Vikram", "Singh", "Computer Teacher"),
            ("Admin", "Office", "Administrator"),
            ("Librarian", "Gupta", "Librarian"),
            ("Transport", "Manager", "Transport In-charge"),
        ]
        staff_members = []
        for fname, lname, designation in staff_data:
            st = Staff.objects.create(
                school=school,
                first_name=fname,
                last_name=lname,
                email=f"{fname.lower().replace(' ', '.')}.{lname.lower()}@mdpconvent.edu",
                phone=f"9876{random.randint(100000, 999999)}",
                designation=designation,
                salary=random.randint(28000, 65000),
                join_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
                is_active=True,
            )
            staff_members.append(st)

        # 7. Fee
        self.stdout.write("Creating fee structures and transactions...")
        for cls in classes:
            FeeStructure.objects.get_or_create(
                school=school,
                class_room=cls,
                title=f"{cls.name} Annual Fee",
                defaults={"amount": 22000, "due_date": date(2026, 4, 30)},
            )
        for student in random.sample(students, 55):
            for month in ["January", "February", "March", "April"]:
                FeeTransaction.objects.create(
                    student=student,
                    amount_paid=random.choice([1000, 1500, 2000, 2500, 5000]),
                    month_year=f"{month} 2026",
                    payment_mode=random.choice(["Cash", "UPI", "Bank Transfer"]),
                    status="Paid",
                )

        # 8. Library
        self.stdout.write("Creating library books and transactions...")
        books_data = [
            ("Physics Class 10", "NCERT", "Physics"),
            ("Chemistry Class 10", "NCERT", "Chemistry"),
            ("Mathematics Class 10", "R.D. Sharma", "Mathematics"),
            ("English Grammar", "Wren & Martin", "English"),
            ("Computer Science", "Sumita Arora", "Computer"),
            ("The Alchemist", "Paulo Coelho", "Fiction"),
            ("Wings of Fire", "APJ Abdul Kalam", "Biography"),
            ("Hindi Vyakaran", "NCERT", "Hindi"),
            ("History of India", "NCERT", "History"),
            ("Geography Class 10", "NCERT", "Geography"),
        ]
        books = []
        for title, author, category in books_data:
            for _ in range(random.randint(2, 5)):
                book = Book.objects.create(
                    school=school,
                    title=title,
                    author=author,
                    isbn=f"ISBN-MDP-{random.randint(1000000, 9999999)}",
                    category=category,
                    total_copies=1,
                    available_copies=random.choice([0, 1]),
                )
                books.append(book)
        for _ in range(45):
            book = random.choice(books)
            student = random.choice(students)
            issue_date = date.today() - timedelta(days=random.randint(1, 30))
            due_date = issue_date + timedelta(days=14)
            LibraryTransaction.objects.create(
                school=school,
                student=student,
                book=book,
                issue_date=issue_date,
                due_date=due_date,
                status=random.choice(["Issued", "Returned"]),
                fine_amount=random.choice([0, 0, 10, 20]),
            )

        # 9. Transport
        self.stdout.write("Creating transport routes and assignments...")
        routes_data = [
            ("Route A - City Center", "MH-12-AB-1234", "Rajesh Kumar", "9876543210"),
            ("Route B - East Zone", "MH-12-CD-5678", "Amit Sharma", "9876543211"),
            ("Route C - West Zone", "MH-12-EF-9012", "Vikram Singh", "9876543212"),
            ("Route D - North Zone", "MH-12-GH-3456", "Suresh Patel", "9876543213"),
        ]
        routes = []
        for rname, vehicle, driver, phone in routes_data:
            route = TransportRoute.objects.create(
                school=school,
                route_name=rname,
                vehicle_number=vehicle,
                driver_name=driver,
                driver_phone=phone,
            )
            routes.append(route)
        for student in random.sample(students, 35):
            if not StudentTransport.objects.filter(student=student).exists():
                StudentTransport.objects.create(
                    school=school,
                    student=student,
                    route=random.choice(routes),
                    pickup_point=f"Stop {random.randint(1, 10)}",
                    monthly_fee=random.choice([1000, 1500, 2000]),
                )

        # 10. Attendance (all 100, last 18 days)
        self.stdout.write("Creating attendance records...")
        for student in students:
            for days_ago in range(1, 19):
                att_date = date.today() - timedelta(days=days_ago)
                if att_date.weekday() < 5:  # Mon-Fri
                    Attendance.objects.get_or_create(
                        student=student,
                        date=att_date,
                        defaults={"status": random.choice(["Present", "Present", "Present", "Absent"])},
                    )

        # 11. ExamScore
        self.stdout.write("Creating exam scores...")
        exams = ["Unit Test 1", "Mid-Term", "Unit Test 2", "Final Exam"]
        for student in random.sample(students, 75):
            for exam in random.sample(exams, random.randint(2, 3)):
                ExamScore.objects.create(
                    student=student,
                    exam_name=exam,
                    maths=random.randint(55, 100),
                    physics=random.randint(50, 100),
                    chemistry=random.randint(50, 100),
                    english=random.randint(60, 100),
                    computer=random.randint(65, 100),
                )

        # 12. Notices
        self.stdout.write("Creating notices...")
        notices_data = [
            ("Fee Due Feb 2026", "Please submit February fee by 10th Feb 2026. Late fine applicable."),
            ("Sports Day", "Annual Sports Day on 15th March 2026. All students must participate."),
            ("Parent-Teacher Meeting", "PTM on 20th Feb 2026, 10 AM to 2 PM. Parents requested to attend."),
            ("Library New Arrivals", "New books added. Students can issue from tomorrow."),
            ("Holiday List", "School will remain closed on 26th Jan and 15th Aug."),
            ("Exam Schedule", "Final exam schedule will be displayed on notice board by 1st March."),
            ("Transport Fee", "Transport fee for Q2 due by 5th April 2026."),
        ]
        for title, message in notices_data:
            Notice.objects.create(school=school, title=title, message=message)

        # 13. SalaryTransaction
        self.stdout.write("Creating salary transactions...")
        months = [("January", "2026"), ("February", "2026"), ("March", "2026")]
        for st in staff_members:
            for month_name, year in months:
                SalaryTransaction.objects.create(
                    school=school,
                    staff=st,
                    amount_paid=st.salary,
                    payment_date=date(int(year), {"January": 1, "February": 2, "March": 3}[month_name], 1) + timedelta(days=4),
                    month_year=f"{month_name} {year}",
                    payment_mode=random.choice(["Bank Transfer", "Cash", "Cheque"]),
                )

        # 14. Expense
        self.stdout.write("Creating expenses...")
        expenses_data = [
            ("Sports equipment", 15000),
            ("Library books", 25000),
            ("Lab chemicals", 12000),
            ("Electricity bill", 8000),
            ("Water bill", 3000),
            ("Cleaning supplies", 5000),
            ("PTA refreshments", 4000),
            ("Annual day decoration", 18000),
        ]
        for desc, amt in expenses_data:
            Expense.objects.create(
                school=school,
                description=desc,
                amount=amt,
                date=date.today() - timedelta(days=random.randint(1, 60)),
            )

        # 15. StudyMaterial
        self.stdout.write("Creating study materials...")
        materials_data = [
            ("Algebra Basics", "Mathematics", "MDP 8"),
            ("Light and Reflection", "Physics", "MDP 10"),
            ("Organic Chemistry Intro", "Chemistry", "MDP 11"),
            ("Essay Writing", "English", "MDP 9"),
            ("Python Basics", "Computer", "MDP 10"),
            ("Hindi Grammar", "Hindi", "MDP 7"),
        ]
        for title, subj, cls_name in materials_data:
            StudyMaterial.objects.create(
                school=school,
                title=title,
                subject=subj,
                class_name=cls_name,
                video_link="https://www.youtube.com/watch?v=dQw4w9WgXcQ" if random.choice([True, False]) else "",
            )

        # 16. AdmissionEnquiry
        self.stdout.write("Creating admission enquiries...")
        for i in range(12):
            AdmissionEnquiry.objects.create(
                school=school,
                name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
                phone=f"98{random.randint(100000000, 999999999)}",
                email=f"enquiry{i}@example.com",
                class_applying=random.choice(["6", "7", "8", "9", "10"]),
                source=random.choice(["Website", "Referral", "Walk-in", "Facebook"]),
                status=random.choice(["New", "Contacted", "Visited", "Admitted", "Lost"]),
                notes="Sample enquiry" if i % 2 else "",
            )

        # 17. TimeSlot & TimetableEntry
        self.stdout.write("Creating timetable...")
        slots_data = [
            (time(8, 0), time(8, 45)),
            (time(8, 45), time(9, 30)),
            (time(9, 30), time(10, 15)),
            (time(10, 15), time(11, 0)),
            (time(11, 15), time(12, 0)),
            (time(12, 0), time(12, 45)),
            (time(12, 45), time(13, 30)),
            (time(14, 0), time(14, 45)),
        ]
        time_slots = []
        for order, (start, end) in enumerate(slots_data):
            ts, _ = TimeSlot.objects.get_or_create(
                school=school,
                start_time=start,
                end_time=end,
                defaults={"order": order},
            )
            time_slots.append(ts)
        # Entries for first 3 classes, first 4 subjects, first 5 staff, Mon-Fri, first 5 slots
        entry_count = 0
        for cls in classes[:3]:
            for day in range(1, 6):
                for slot in time_slots[:5]:
                    sub = random.choice(subjects)
                    teacher = random.choice(staff_members[:6])
                    if not TimetableEntry.objects.filter(
                        school=school, class_room=cls, day_of_week=day, time_slot=slot
                    ).exists():
                        TimetableEntry.objects.create(
                            school=school,
                            class_room=cls,
                            subject=sub,
                            staff=teacher,
                            day_of_week=day,
                            time_slot=slot,
                        )
                        entry_count += 1
                        if entry_count >= 60:
                            break
                if entry_count >= 60:
                    break
            if entry_count >= 60:
                break

        # 18. Notifications (for a user linked to this school if any)
        self.stdout.write("Creating notifications...")
        profile = UserProfile.objects.filter(school=school).first()
        if profile:
            for title, msg in [
                ("Welcome to MDP Convent ERP", "Your school data has been seeded successfully."),
                ("Fee reminder", "February fee due by 10th. Please collect from parents."),
            ]:
                Notification.objects.create(
                    school=school,
                    user=profile.user,
                    title=title,
                    message=msg,
                    read=False,
                )

        # Summary
        self.stdout.write(self.style.SUCCESS("\nMDP Convent seed completed.\n"))
        self.stdout.write(f"  School: {school.name}")
        self.stdout.write(f"  Classes: {ClassRoom.objects.filter(school=school).count()}")
        self.stdout.write(f"  Students: {Member.objects.filter(school=school).count()}")
        self.stdout.write(f"  Staff: {Staff.objects.filter(school=school).count()}")
        self.stdout.write(f"  Books: {Book.objects.filter(school=school).count()}")
        self.stdout.write(f"  Fee transactions: {FeeTransaction.objects.filter(student__school=school).count()}")
        self.stdout.write(f"  Attendance: {Attendance.objects.filter(student__school=school).count()}")
        self.stdout.write(f"  Exam scores: {ExamScore.objects.filter(student__school=school).count()}")
        self.stdout.write(f"  Notices: {Notice.objects.filter(school=school).count()}")
        self.stdout.write(f"  Enquiries: {AdmissionEnquiry.objects.filter(school=school).count()}")
        self.stdout.write(f"  Timetable entries: {TimetableEntry.objects.filter(school=school).count()}\n")
