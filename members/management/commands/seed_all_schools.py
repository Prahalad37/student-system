"""
Seed ALL schools with 100 realistic Indian students and data for all ERP modules.
Usage: python manage.py seed_all_schools [--count 100]
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

# Realistic Indian first names (gender-neutral friendly mix)
FIRST_NAMES_MALE = [
    "Arjun", "Rahul", "Vikram", "Amit", "Rohit", "Karan", "Varun", "Ravi",
    "Sachin", "Ramesh", "Suresh", "Manoj", "Deepak", "Nitin", "Ajay", "Sunil",
    "Prakash", "Anil", "Rajesh", "Sanjay", "Vivek", "Gaurav", "Aditya", "Kunal",
    "Yash", "Ritvik", "Arnav", "Aarav", "Kabir", "Ishaan", "Dev", "Reyansh",
]
FIRST_NAMES_FEMALE = [
    "Priya", "Sneha", "Anita", "Kavita", "Meera", "Pooja", "Neha", "Swati",
    "Divya", "Kirti", "Pallavi", "Anjali", "Shweta", "Ritu", "Preeti", "Nidhi",
    "Komal", "Simran", "Rekha", "Sapna", "Kavya", "Ishita", "Tanvi", "Nisha",
    "Ananya", "Aisha", "Diya", "Isha", "Kiara", "Riya", "Saanvi", "Aaradhya",
]
LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Singh", "Gupta", "Verma", "Yadav", "Reddy",
    "Joshi", "Malhotra", "Nair", "Desai", "Iyer", "Kapoor", "Shah", "Rao",
    "Mehta", "Pillai", "Sinha", "Chopra", "Dubey", "Mishra", "Jain", "Saxena",
    "Bose", "Banerjee", "Chatterjee", "Mukherjee", "Das", "Roy",
]

# Realistic Indian addresses
ADDRESSES = [
    "Sector 15, Block A, Gurgaon, Haryana - 122001",
    "Sector 22, Rohini, Delhi - 110085",
    "Koramangala 5th Block, Bangalore - 560034",
    "Powai, Near IIT, Mumbai - 400076",
    "Saket, Block C, New Delhi - 110017",
    "Indiranagar, 100ft Road, Bangalore - 560038",
    "Andheri West, Link Road, Mumbai - 400058",
    "Karol Bagh, Delhi - 110005",
    "Palam Vihar, Gurgaon - 122017",
    "Jubilee Hills, Hyderabad - 500033",
    "Salt Lake, Sector 5, Kolkata - 700091",
    "Anna Nagar, Chennai - 600040",
    "Vastrapur, Ahmedabad - 380015",
    "MG Road, Pune - 411001",
    "Civil Lines, Jaipur - 302006",
]

# Father/Mother occupations
OCCUPATIONS = [
    "Government Service", "Private Sector", "Business", "Doctor", "Engineer",
    "Teacher", "Bank Officer", "CA", "Architect", "Software Professional",
]

# Religion options
RELIGIONS = ["Hindu", "Sikh", "Christian", "Muslim", "Buddhist", "Jain"]

# Cities for transport routes
CITY_ROUTES = [
    ("Central Route", "MH-12-AB", "Rajesh Kumar"),
    ("East Zone Route", "MH-14-CD", "Amit Sharma"),
    ("West Zone Route", "DL-01-EF", "Vikram Singh"),
    ("North Route", "KA-01-GH", "Suresh Patel"),
]


def get_school_prefix(school):
    """Get 3-4 char prefix from school code for class names, admission nos."""
    code = (school.code or school.school_code or "SCH")[:6]
    return code.replace("-", "")[:4].upper() or "SCH"


def seed_school(school, count, stdout, style):
    prefix = get_school_prefix(school)
    domain = school.code.replace("-", "")[:6].lower() if school.code else "school"

    # 2. Classes (school-prefixed to avoid unique_together clash)
    stdout.write(f"  Creating classes for {school.name}...")
    classes_data = [
        (f"{prefix} 6", "A"), (f"{prefix} 7", "A"), (f"{prefix} 8", "A"),
        (f"{prefix} 9", "A"), (f"{prefix} 10", "A"),
        (f"{prefix} 11", "Science"), (f"{prefix} 12", "Science"),
        (f"{prefix} 11", "Commerce"), (f"{prefix} 12", "Commerce"),
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
        sub, _ = Subject.objects.get_or_create(
            school=school, name=sname, defaults={"code": sname[:3].upper()}
        )
        subjects.append(sub)
    for ename in ["Unit Test", "Mid-Term", "Final"]:
        ExamType.objects.get_or_create(school=school, name=ename)

    # 5. Students - realistic Indian data
    stdout.write(f"  Creating {count} students...")
    students = []
    base_admission = 1000 + Member.objects.filter(school=school).count()
    for i in range(count):
        gender = random.choice(["Male", "Female"])
        first = random.choice(FIRST_NAMES_FEMALE if gender == "Female" else FIRST_NAMES_MALE)
        last = random.choice(LAST_NAMES)
        father_first = random.choice(FIRST_NAMES_MALE)
        father_last = random.choice(LAST_NAMES)
        mother_first = random.choice(FIRST_NAMES_FEMALE)
        mother_last = random.choice(LAST_NAMES)

        student = Member.objects.create(
            school=school,
            admission_no=f"{prefix}2025{base_admission + i}",
            firstname=first,
            lastname=last,
            father_name=f"{father_first} {father_last}",
            mother_name=f"{mother_first} {mother_last}",
            mother_mobile=f"98{random.randint(500000000, 999999999)}",
            father_occupation=random.choice(OCCUPATIONS),
            mother_occupation=random.choice(OCCUPATIONS),
            mobile_number=f"98{random.randint(500000000, 999999999)}",
            email=f"{first.lower()}.{last.lower()}{i}@{domain}.edu.in",
            student_class=random.choice(classes),
            roll_number=str((i % 40) + 1),
            gender=gender,
            dob=date(2008 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 25)),
            address=random.choice(ADDRESSES),
            blood_group=random.choice(["A+", "B+", "O+", "AB+", "A-", "B-", "O-"]),
            caste_category=random.choice(["General", "OBC", "SC", "ST", "EWS"]),
            religion=random.choice(RELIGIONS),
            previous_school=random.choice([
                "St. Xavier's Academy", "Delhi Public School", "Kendriya Vidyalaya",
                "DAV Public School", "Bharatiya Vidya Bhavan", "Navodaya Vidyalaya",
            ]) if random.random() < 0.6 else None,
            previous_class=random.choice(["5", "6", "7", "8"]) if random.random() < 0.5 else None,
            fee_total=22000,
            fee_paid=random.randint(0, 22000),
        )
        students.append(student)

    # 6. Staff
    stdout.write("  Creating staff...")
    staff_data = [
        ("Principal", "Principal"),
        ("Rahul", "Physics Teacher"),
        ("Priya", "Mathematics Teacher"),
        ("Amit", "Chemistry Teacher"),
        ("Sneha", "English Teacher"),
        ("Vikram", "Computer Teacher"),
        ("Admin", "Administrator"),
        ("Librarian", "Librarian"),
        ("Transport", "Transport In-charge"),
    ]
    staff_members = []
    for fname, designation in staff_data:
        lname = random.choice(LAST_NAMES)
        st = Staff.objects.create(
            school=school,
            first_name=fname,
            last_name=lname,
            email=f"{fname.lower().replace(' ', '.')}.{lname.lower()}@{domain}.edu.in",
            phone=f"98{random.randint(500000000, 999999999)}",
            designation=designation,
            salary=random.randint(28000, 65000),
            join_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
            is_active=True,
        )
        staff_members.append(st)

    # 7. Fee
    stdout.write("  Creating fee structures and transactions...")
    for cls in classes:
        FeeStructure.objects.get_or_create(
            school=school,
            class_room=cls,
            title=f"{cls.name} Annual Fee",
            defaults={"amount": 22000, "due_date": date(2026, 4, 30)},
        )
    for student in random.sample(students, min(len(students) // 2 + 10, len(students))):
        for month in ["January", "February", "March", "April"]:
            FeeTransaction.objects.create(
                student=student,
                amount_paid=random.choice([1000, 1500, 2000, 2500, 5000]),
                month_year=f"{month} 2026",
                payment_mode=random.choice(["Cash", "UPI", "Bank Transfer"]),
                status="Paid",
            )

    # 8. Library
    stdout.write("  Creating library books and transactions...")
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
    ]
    books = []
    for title, author, category in books_data:
        for _ in range(random.randint(2, 5)):
            book = Book.objects.create(
                school=school,
                title=title,
                author=author,
                isbn=f"ISBN-{prefix}-{random.randint(1000000, 9999999)}",
                category=category,
                total_copies=1,
                available_copies=random.choice([0, 1]),
            )
            books.append(book)
    for _ in range(min(45, len(books) * 3)):
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
    stdout.write("  Creating transport routes and assignments...")
    routes = []
    for rname, vprefix, driver in CITY_ROUTES:
        route = TransportRoute.objects.create(
            school=school,
            route_name=rname,
            vehicle_number=f"{vprefix}-{random.randint(1000, 9999)}",
            driver_name=driver,
            driver_phone=f"98{random.randint(500000000, 999999999)}",
        )
        routes.append(route)
    for student in random.sample(students, min(35, len(students))):
        if not StudentTransport.objects.filter(student=student).exists():
            StudentTransport.objects.create(
                school=school,
                student=student,
                route=random.choice(routes),
                pickup_point=f"Stop {random.randint(1, 10)}",
                monthly_fee=random.choice([1000, 1500, 2000]),
            )

    # 10. Attendance
    stdout.write("  Creating attendance records...")
    for student in students:
        for days_ago in range(1, 19):
            att_date = date.today() - timedelta(days=days_ago)
            if att_date.weekday() < 5:
                Attendance.objects.get_or_create(
                    student=student,
                    date=att_date,
                    defaults={"status": random.choice(["Present", "Present", "Present", "Absent"])},
                )

    # 11. ExamScore
    stdout.write("  Creating exam scores...")
    exams = ["Unit Test 1", "Mid-Term", "Unit Test 2", "Final Exam"]
    for student in random.sample(students, min(75, len(students))):
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
    stdout.write("  Creating notices...")
    notices_data = [
        ("Fee Due Feb 2026", "कृपया फरवरी शुल्क 10 फरवरी 2026 तक जमा करें। Late fine applicable."),
        ("Sports Day", "Annual Sports Day on 15th March 2026. All students must participate."),
        ("Parent-Teacher Meeting", "PTM on 20th Feb 2026, 10 AM to 2 PM. Parents requested to attend."),
        ("Library New Arrivals", "New books added. Students can issue from tomorrow."),
        ("Holiday List", "School will remain closed on 26th Jan and 15th Aug."),
        ("Exam Schedule", "Final exam schedule will be displayed on notice board by 1st March."),
    ]
    for title, message in notices_data:
        Notice.objects.create(school=school, title=title, message=message)

    # 13. SalaryTransaction
    stdout.write("  Creating salary transactions...")
    for st in staff_members:
        for month_name, year in [("January", "2026"), ("February", "2026"), ("March", "2026")]:
            SalaryTransaction.objects.create(
                school=school,
                staff=st,
                amount_paid=st.salary,
                payment_date=date(int(year), {"January": 1, "February": 2, "March": 3}[month_name], 5),
                month_year=f"{month_name} {year}",
                payment_mode=random.choice(["Bank Transfer", "Cash", "Cheque"]),
            )

    # 14. Expense
    stdout.write("  Creating expenses...")
    expenses_data = [
        ("Sports equipment", 15000),
        ("Library books", 25000),
        ("Lab chemicals", 12000),
        ("Electricity bill", 8000),
        ("Water bill", 3000),
        ("Cleaning supplies", 5000),
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
    stdout.write("  Creating study materials...")
    materials_data = [
        ("Algebra Basics", "Mathematics", f"{prefix} 8"),
        ("Light and Reflection", "Physics", f"{prefix} 10"),
        ("Organic Chemistry Intro", "Chemistry", f"{prefix} 11"),
        ("Essay Writing", "English", f"{prefix} 9"),
        ("Python Basics", "Computer", f"{prefix} 10"),
    ]
    for title, subj, cls_name in materials_data:
        StudyMaterial.objects.create(
            school=school,
            title=title,
            subject=subj,
            class_name=cls_name,
            video_link="https://www.youtube.com/watch?v=example" if random.choice([True, False]) else "",
        )

    # 16. AdmissionEnquiry
    stdout.write("  Creating admission enquiries...")
    for i in range(12):
        gender = random.choice(["Male", "Female"])
        first = random.choice(FIRST_NAMES_FEMALE if gender == "Female" else FIRST_NAMES_MALE)
        AdmissionEnquiry.objects.create(
            school=school,
            name=f"{first} {random.choice(LAST_NAMES)}",
            phone=f"98{random.randint(500000000, 999999999)}",
            email=f"enquiry{i}@{domain}.example.com",
            class_applying=random.choice(["6", "7", "8", "9", "10"]),
            source=random.choice(["Website", "Referral", "Walk-in", "Facebook", "Google"]),
            status=random.choice(["New", "Contacted", "Visited", "Admitted", "Lost"]),
            notes="Interested in admission" if i % 2 else "",
        )

    # 17. TimeSlot & TimetableEntry
    stdout.write("  Creating timetable...")
    slots_data = [
        (time(8, 0), time(8, 45)),
        (time(8, 45), time(9, 30)),
        (time(9, 30), time(10, 15)),
        (time(10, 15), time(11, 0)),
        (time(11, 15), time(12, 0)),
        (time(12, 0), time(12, 45)),
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

    # 18. Notifications
    profile = UserProfile.objects.filter(school=school).first()
    if profile:
        for title, msg in [
            (f"Welcome to {school.name} ERP", "Your school data has been seeded successfully."),
            ("Fee reminder", "February fee due by 10th. Please collect from parents."),
        ]:
            Notification.objects.create(
                school=school,
                user=profile.user,
                title=title,
                message=msg,
                read=False,
            )

    stdout.write(style.SUCCESS(f"  ✓ {school.name}: {len(students)} students, {len(staff_members)} staff"))
    return len(students)


class Command(BaseCommand):
    help = "Seeds ALL schools with 100 realistic students and data for all ERP modules"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=100,
            help="Number of students per school (default: 100)",
        )

    def handle(self, *args, **options):
        count = options["count"]
        schools = list(School.objects.all())
        if not schools:
            self.stdout.write("No schools found. Creating MDP Convent and Demo School...")
            School.objects.get_or_create(
                code="mdp-convent",
                defaults={
                    "name": "MDP Convent",
                    "address": "St. Mary Road, City - 400001",
                    "school_code": "MDP001",
                },
            )
            School.objects.get_or_create(
                code="demo",
                defaults={
                    "name": "Demo School",
                    "address": "123 Education Lane",
                    "school_code": "DEMO001",
                },
            )
            schools = list(School.objects.all())

        self.stdout.write(self.style.SUCCESS(f"\nSeeding {len(schools)} school(s) with {count} students each...\n"))

        total_students = 0
        for school in schools:
            self.stdout.write(f"Seeding {school.name} ({school.code})...")
            try:
                n = seed_school(school, count, self.stdout, self.style)
                total_students += n
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))
                raise

        self.stdout.write(self.style.SUCCESS(f"\n✓ All schools seeded. Total students: {total_students}\n"))
