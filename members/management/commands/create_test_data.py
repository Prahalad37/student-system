"""
Management command to create comprehensive test data for the ERP system.
Usage: python manage.py create_test_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, timedelta
import random
from members.models import (
    School, ClassRoom, Member, Book, LibraryTransaction,
    TransportRoute, StudentTransport, Staff, ExamScore,
    Attendance, Notice, FeeStructure, FeeTransaction
)

class Command(BaseCommand):
    help = 'Creates comprehensive test data for Django ERP'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Creating test data...\n'))
        
        # Use first school (same one shown on localhost dashboard) or create one
        school1 = School.objects.first()
        if not school1:
            self.stdout.write('Creating school...')
            school1 = School.objects.create(
                name='Prahlad Academy',
                address='123 Main Street, City',
                school_code='PTEST001',
                code='prahlad'
            )
        else:
            self.stdout.write(f'Using existing school: {school1.name}')
        
        # Create Classes (use school-specific names to avoid unique_together conflicts)
        self.stdout.write('Creating classes...')
        prefix = school1.code[:4].upper() if school1.code else "S"
        classes_data = [
            (f'{prefix} Class 6', 'A'), (f'{prefix} Class 7', 'A'), (f'{prefix} Class 8', 'A'),
            (f'{prefix} Class 9', 'A'), (f'{prefix} Class 10', 'A'), (f'{prefix} Class 11', 'Science'),
            (f'{prefix} Class 12', 'Science'), (f'{prefix} Class 11', 'Commerce'), (f'{prefix} Class 12', 'Commerce')
        ]
        classes = []
        for class_name, section in classes_data:
            cls, _ = ClassRoom.objects.get_or_create(
                school=school1,
                name=class_name,
                section=section
            )
            classes.append(cls)
        
        # Create Students
        self.stdout.write('Creating students...')
        first_names = ['Rajesh', 'Priya', 'Amit', 'Sneha', 'Vikram', 'Anita', 'Rohit', 'Kavita',
                      'Arjun', 'Meera', 'Karan', 'Pooja', 'Sanjay', 'Neha', 'Rahul', 'Swati']
        last_names = ['Kumar', 'Sharma', 'Patel', 'Singh', 'Gupta', 'Verma', 'Yadav', 'Reddy',
                     'Joshi', 'Malhotra', 'Nair', 'Desai', 'Iyer', 'Kapoor']
        
        students = []
        for i in range(50):
            student = Member.objects.create(
                school=school1,
                admission_no=f'STU{1000+i}',
                firstname=random.choice(first_names),
                lastname=random.choice(last_names),
                father_name=f'{random.choice(first_names)} {random.choice(last_names)}',
                mobile_number=f'98765{43210+i}',
                email=f'student{i}@test.com',
                student_class=random.choice(classes),
                roll_number=str(random.randint(1, 50)),
                gender=random.choice(['Male', 'Female']),
                dob=date(2008 + random.randint(0, 5), random.randint(1, 12), random.randint(1, 28)),
                address=f'{random.randint(1, 100)} Sample Street, City',
                blood_group=random.choice(['A+', 'B+', 'O+', 'AB+', 'A-', 'B-', 'O-', 'AB-']),
                fee_total=20000,
                fee_paid=random.randint(0, 20000)
            )
            students.append(student)
        
        # Create Staff
        self.stdout.write('Creating staff...')
        staff_names = [
            ('Rahul', 'Sharma', 'Physics Teacher'),
            ('Priya', 'Patel', 'Mathematics Teacher'),
            ('Amit', 'Kumar', 'Chemistry Teacher'),
            ('Sneha', 'Verma', 'English Teacher'),
            ('Vikram', 'Singh', 'Computer Teacher'),
            ('Admin', 'Staff', 'Administrator'),
            ('Librarian', 'Gupta', 'Librarian'),
            ('Transport', 'Manager', 'Transport In-charge')
        ]
        staff_members = []
        for fname, lname, designation in staff_names:
            staff = Staff.objects.create(
                school=school1,
                first_name=fname,
                last_name=lname,
                email=f'{fname.lower()}.{lname.lower()}@prahlad.edu',
                phone=f'9876{random.randint(100000, 999999)}',
                designation=designation,
                salary=random.randint(25000, 60000),
                join_date=date(2023, random.randint(1, 12), random.randint(1, 28)),
                is_active=True
            )
            staff_members.append(staff)
        
        # Create Fee Structures
        self.stdout.write('Creating fee structures...')
        for cls in classes:
            FeeStructure.objects.get_or_create(
                school=school1,
                class_room=cls,
                title=f'{cls.name} Annual Fee',
                defaults={
                    'amount': 20000,
                    'due_date': date(2026, 4, 30)
                }
            )
        
        # Create Fee Transactions
        self.stdout.write('Creating fee transactions...')
        for student in random.sample(students, 30):
            for month in ['January', 'February', 'March']:
                FeeTransaction.objects.create(
                    student=student,
                    amount_paid=random.choice([1000, 1500, 2000, 2500, 5000]),
                    month_year=f'{month} 2026',
                    payment_mode=random.choice(['Cash', 'UPI', 'Bank Transfer']),
                    status='Paid'
                )
        
        # Create Library Books
        self.stdout.write('Creating library books...')
        books_data = [
            ('Physics Class 10', 'NCERT', 'Physics'),
            ('Chemistry Class 10', 'NCERT', 'Chemistry'),
            ('Mathematics Class 10', 'R.D. Sharma', 'Mathematics'),
            ('English Grammar', 'Wren & Martin', 'English'),
            ('Computer Science', 'Sumita Arora', 'Computer'),
            ('The Alchemist', 'Paulo Coelho', 'Fiction'),
            ('Wings of Fire', 'APJ Abdul Kalam', 'Biography'),
            ('Harry Potter Series', 'J.K. Rowling', 'Fiction'),
            ('The Discovery of India', 'Jawaharlal Nehru', 'History'),
            ('Geeta Rahasya', 'Lokmanya Tilak', 'Philosophy')
        ]
        books = []
        for title, author, category in books_data:
            for copy_num in range(random.randint(3, 8)):
                book = Book.objects.create(
                    school=school1,
                    title=title,
                    author=author,
                    isbn=f'ISBN-{random.randint(1000000000, 9999999999)}',
                    category=category,
                    total_copies=1,
                    available_copies=random.choice([0, 1])
                )
                books.append(book)
        
        # Create Library Transactions
        self.stdout.write('Creating library transactions...')
        for i in range(25):
            book = random.choice(books)
            student = random.choice(students)
            issue_date = date.today() - timedelta(days=random.randint(1, 30))
            due_date = issue_date + timedelta(days=14)
            
            LibraryTransaction.objects.create(
                school=school1,
                student=student,
                book=book,
                issue_date=issue_date,
                due_date=due_date,
                status=random.choice(['Issued', 'Returned']),
                fine_amount=random.choice([0, 0, 0, 10, 20, 50])
            )
        
        # Create Transport Routes
        self.stdout.write('Creating transport routes...')
        routes_data = [
            ('Route A - City Center', 'MH-12-AB-1234', 'Rajesh Kumar', '9876543210'),
            ('Route B - East Zone', 'MH-12-CD-5678', 'Amit Sharma', '9876543211'),
            ('Route C - West Zone', 'MH-12-EF-9012', 'Vikram Singh', '9876543212'),
        ]
        routes = []
        for route_name, vehicle, driver, phone in routes_data:
            route = TransportRoute.objects.create(
                school=school1,
                route_name=route_name,
                vehicle_number=vehicle,
                driver_name=driver,
                driver_phone=phone
            )
            routes.append(route)
        
        # Assign Transport to Students
        self.stdout.write('Assigning transport to students...')
        for student in random.sample(students, 15):
            StudentTransport.objects.get_or_create(
                school=school1,
                student=student,
                defaults={
                    'route': random.choice(routes),
                    'pickup_point': f'Stop {random.randint(1, 10)}',
                    'monthly_fee': random.choice([1000, 1500, 2000])
                }
            )
        
        # Create Attendance Records
        self.stdout.write('Creating attendance records...')
        for student in random.sample(students, 30):
            for days_ago in range(1, 16):  # Last 15 days
                attendance_date = date.today() - timedelta(days=days_ago)
                Attendance.objects.get_or_create(
                    student=student,
                    date=attendance_date,
                    defaults={'status': random.choice(['Present', 'Present', 'Present', 'Absent'])}
                )
        
        # Create Exam Scores
        self.stdout.write('Creating exam scores...')
        exams = ['Unit Test 1', 'Mid-Term', 'Unit Test 2', 'Final Exam']
        for student in random.sample(students, 25):
            for exam in random.sample(exams, 2):
                ExamScore.objects.create(
                    student=student,
                    exam_name=exam,
                    maths=random.randint(60, 100),
                    physics=random.randint(55, 100),
                    chemistry=random.randint(50, 100),
                    english=random.randint(65, 100),
                    computer=random.randint(70, 100)
                )
        
        # Create Notices
        self.stdout.write('Creating notices...')
        notices_data = [
            ('Important: Feb Fee Due', 'Please submit February fee by 10th Feb 2026. Late fine applicable after due date.'),
            ('Sports Day Announcement', 'Annual Sports Day will be held on 15th March 2026. All students must participate.'),
            ('Parent-Teacher Meeting', 'PTM scheduled for 20th Feb 2026 from 10 AM to 2 PM. Parents are requested to attend.'),
            ('Library Update', 'New books have been added to the library. Students can issue them from tomorrow.'),
        ]
        for title, message in notices_data:
            Notice.objects.create(
                school=school1,
                title=title,
                message=message
            )
        
        # Summary
        self.stdout.write(self.style.SUCCESS('\n✅ Test Data Created Successfully!\n'))
        self.stdout.write(f'  📚 Schools: {School.objects.count()}')
        self.stdout.write(f'  🎓 Students: {Member.objects.count()}')
        self.stdout.write(f'  👨‍🏫 Staff: {Staff.objects.count()}')
        self.stdout.write(f'  📖 Books: {Book.objects.count()}')
        self.stdout.write(f'  🚌 Transport Routes: {TransportRoute.objects.count()}')
        self.stdout.write(f'  📝 Fee Transactions: {FeeTransaction.objects.count()}')
        self.stdout.write(f'  ✅ Attendance Records: {Attendance.objects.count()}')
        self.stdout.write(f'  📊 Exam Scores: {ExamScore.objects.count()}')
        self.stdout.write(f'  📢 Notices: {Notice.objects.count()}\n')
