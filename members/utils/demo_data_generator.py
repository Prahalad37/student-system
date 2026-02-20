"""
Demo School Data Generator
Generates realistic sample data for demo schools
"""

import random
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from members.models import (
    School, Member, ClassRoom, AcademicYear, 
    Attendance, Book
)


class DemoDataGenerator:
    """Generate realistic demo data for schools"""
    
    # Indian student names
    FIRST_NAMES_BOYS = [
        'Aarav', 'Vivaan', 'Aditya', 'Arjun', 'Sai', 'Aryan', 'Reyansh', 'Ayaan', 
        'Krishna', 'Ishaan', 'Shaurya', 'Atharv', 'Advait', 'Pranav', 'Dhruv',
        'Arnav', 'Kabir', 'Shivansh', 'Rudra', 'Vihaan', 'Ritvik', 'Yash', 'Dev'
    ]
    
    FIRST_NAMES_GIRLS = [
        'Aadhya', 'Ananya', 'Diya', 'Saanvi', 'Pari', 'Angel', 'Myra', 'Sara',
        'Aaradhya', 'Navya', 'Kavya', 'Anika', 'Riya', 'Prisha', 'Avni',
        'Kiara', 'Aditi', 'Ishita', 'Shanaya', 'Ahana', 'Tara', 'Zara', 'Niya'
    ]
    
    LAST_NAMES = [
        'Sharma', 'Verma', 'Gupta', 'Kumar', 'Singh', 'Patel', 'Reddy', 'Rao',
        'Malhotra', 'Joshi', 'Mehta', 'Kapoor', 'Desai', 'Iyer', 'Nair',
        'Chopra', 'Bansal', 'Agarwal', 'Khan', 'Sinha', 'Mishra', 'Pandey'
    ]
    
    TEACHER_SUBJECTS = [
        ('Mathematics', 'Math Teacher'),
        ('Science', 'Science Teacher'),
        ('English', 'English Teacher'),
        ('Hindi', 'Hindi Teacher'),
        ('Social Studies', 'SST Teacher'),
        ('Computer Science', 'CS Teacher'),
        ('Physical Education', 'PE Teacher'),
        ('Art', 'Art Teacher'),
    ]
    
    def __init__(self, school):
        self.school = school
        self.created_users = []
        
    def generate_all(self):
        """Generate all demo data"""
        print(f"🏫 Generating demo data for {self.school.name}...")
        
        # 1. Create academic year
        academic_year = self.create_academic_year()
        print(f"✅ Created academic year: {academic_year.name}")
        
        #  2. Create classes
        classes = self.create_classes()
        print(f"✅ Created {len(classes)} classes")
        
        # 3. Create admin user
        admin_user = self.create_admin_user()
        print(f"✅ Created admin: {admin_user.username}")
        
        # 4. Create staff
        staff = self.create_staff(8)
        print(f"✅ Created {len(staff)} staff members")
        
        # 5. Create students
        students = self.create_students(50, classes)
        print(f"✅ Created {len(students)} students")
        
        # 6. Create attendance
        attendance_count = self.create_attendance(students, days=30)
        print(f"✅ Created {attendance_count} attendance records")
        
        # 7. Create library books
        books = self.create_books(10)
        print(f"✅ Created {len(books)} library books")
        
        print(f"\n🎉 Demo data generation complete!")
        
        return {
            'admin_username': admin_user.username,
            'admin_password': 'demo123',
            'students_count': len(students),
            'staff_count': len(staff),
            'classes_count': len(classes),
        }
    
    def create_academic_year(self):
        """Create current academic year"""
        current_year = datetime.now().year
        ay, _ = AcademicYear.objects.get_or_create(
            school=self.school,
            name=f"{current_year}-{current_year + 1}",
            defaults={
                'start_date': datetime(current_year, 4, 1).date(),
                'end_date': datetime(current_year + 1, 3, 31).date(),
                'is_active': True
            }
        )
        return ay
    
    def create_classes(self):
        """Create class 1 to 5"""
        classes = []
        for i in range(1, 6):
            cls, _ = ClassRoom.objects.get_or_create(
                school=self.school,
                name=f"Class {i}",
                defaults={'section': 'A'}
            )
            classes.append(cls)
        return classes
    
    def create_admin_user(self):
        """Create school admin user"""
        username = f"{self.school.code}_admin"
        
        # Check if user exists
        if User.objects.filter(username=username).exists():
            username = f"{self.school.code}_admin_{random.randint(100, 999)}"
        
        user = User.objects.create_user(
            username=username,
            password='demo123',
            email=f"admin@{self.school.code}.edu",
            first_name='School',
            last_name='Admin',
            is_staff=True
        )
        
        # Create user profile
        if hasattr(user, 'userprofile'):
            user.userprofile.school = self.school
            user.userprofile.role = 'ADMIN'
            user.userprofile.save()
        
        self.created_users.append(user)
        return user
    
    def create_staff(self, count=8):
        """Create staff members"""
        staff_members = []
        
        # Teachers
        for i, (subject, designation) in enumerate(self.TEACHER_SUBJECTS[:count]):
            first_name = random.choice(self.FIRST_NAMES_BOYS + self.FIRST_NAMES_GIRLS)
            last_name = random.choice(self.LAST_NAMES)
            
            username = f"{self.school.code}_teacher_{i+1}"
            if User.objects.filter(username=username).exists():
                username = f"{username}_{random.randint(100, 999)}"
            
            user = User.objects.create_user(
                username=username,
                password='demo123',
                first_name=first_name,
                last_name=last_name
            )
            
            if hasattr(user, 'userprofile'):
                user.userprofile.school = self.school
                user.userprofile.role = 'TEACHER'
                user.userprofile.save()
            
            staff_members.append(user)
        
        return staff_members
    
    def create_students(self, count, classes):
        """Create student members"""
        students = []
        
        for i in range(count):
            # Random gender
            gender = random.choice(['Male', 'Female'])
            first_name = random.choice(
                self.FIRST_NAMES_BOYS if gender == 'Male' else self.FIRST_NAMES_GIRLS
            )
            last_name = random.choice(self.LAST_NAMES)
            
            # Random class
            classroom = random.choice(classes)
            
            # Random age (6-12 years old)
            age = random.randint(6, 12)
            dob = datetime.now() - timedelta(days=age*365 + random.randint(0,  364))
            
            student = Member.objects.create(
                school=self.school,
                admission_no=f"{self.school.school_code}{1000+i}",
                firstname=first_name,
                lastname=last_name,
                gender=gender,
                dob=dob.date(),
                student_class=classroom,
                address=f"{random.randint(1, 999)} {random.choice(['MG Road', 'Park Street', 'Main Street'])}",
                mobile_number=f"98{random.randint(10000000, 99999999)}",
                email=f"{first_name.lower()}.{last_name.lower()}@student.edu",
                father_name=f"{random.choice(self.FIRST_NAMES_BOYS)} {last_name}",
                mother_name=f"{random.choice(self.FIRST_NAMES_GIRLS)} {last_name}",
            )
            students.append(student)
        
        return students
    
    def create_attendance(self, students, days=30):
        """Create attendance records for last 30 days"""
        count = 0
        
        for day in range(days):
            date = datetime.now().date() - timedelta(days=day)
            
            # Skip weekends
            if date.weekday() >= 5:
                continue
            
            for student in students:
                # 90% attendance rate
                status = 'Present' if random.random() < 0.9 else 'Absent'
                
                Attendance.objects.create(
                    student=student,
                    date=date,
                    status=status
                )

                count += 1
        
        return count
    
    def create_books(self, count=10):
        """Create library books"""
        books = []
        
        book_titles = [
            ('Harry Potter', 'J.K. Rowling'),
            ('The Hobbit', 'J.R.R. Tolkien'),
            ('Wings of Fire', 'APJ Abdul Kalam'),
            ('Malgudi Days', 'R.K. Narayan'),
            ('The Secret Seven', 'Enid Blyton'),
            ('Goosebumps', 'R.L. Stine'),
            ('Panchatantra', 'Vishnu Sharma'),
            ('Ramayana for Children', 'Valmiki'),
            ('Science Experiments', 'Various'),
            ('Indian History', 'Various'),
        ]
        
        for title, author in book_titles[:count]:
            copies = random.randint(2, 5)
            
            book = Book.objects.create(
                school=self.school,
                title=title,
                author=author,
                isbn=f"978-{random.randint(1000000000, 9999999999)}",
                category=random.choice(['Fiction', 'Non-Fiction', 'Science', 'History']),
                total_copies=copies,
                available_copies=copies
            )
            books.append(book)
        
        return books
