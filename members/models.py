from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==========================================
# 1. SCHOOL & ACADEMIC MODULE (SaaS Core)
# ==========================================

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    school_code = models.CharField(max_length=50, unique=True) # e.g., 'PRAHLAD01'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, help_text="e.g. 2023-2024")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class ClassRoom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50, help_text="e.g. Class 10")
    section = models.CharField(max_length=10, default='A')

    class Meta:
        unique_together = ('name', 'section') 
        verbose_name = "Class Room"
        verbose_name_plural = "Class Rooms"

    def __str__(self):
        return f"{self.name} - {self.section}"

# ==========================================
# 2. MAIN STUDENT MODULE
# ==========================================

class Member(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    admission_no = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    student_class = models.ForeignKey(ClassRoom, on_delete=models.SET_NULL, null=True, blank=True)
    roll_number = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male')
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    joined_date = models.DateField(auto_now_add=True, null=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="student_images/")
    blood_group = models.CharField(max_length=5, choices=[('A+', 'A+'), ('B+', 'B+'), ('O+', 'O+'), ('AB+', 'AB+'), ('A-', 'A-'), ('B-', 'B-'), ('O-', 'O-'), ('AB-', 'AB-')], null=True, blank=True)
    medical_conditions = models.TextField(null=True, blank=True, help_text="Any allergies or conditions")
    transport_mode = models.CharField(max_length=20, choices=[('School Bus', 'School Bus'), ('Private', 'Private'), ('Self', 'Self')], default='Self')
    route_name = models.CharField(max_length=100, null=True, blank=True, help_text="If School Bus")
    house_team = models.CharField(max_length=20, choices=[('Red', 'Red'), ('Blue', 'Blue'), ('Green', 'Green'), ('Yellow', 'Yellow')], null=True, blank=True)
    preferred_stream = models.CharField(max_length=50, choices=[('General', 'General'), ('Science (PCM)', 'Science (PCM)'), ('Science (PCB)', 'Science (PCB)'), ('Commerce', 'Commerce'), ('Arts', 'Arts')], default='General')
    fee_total = models.IntegerField(default=0)
    fee_paid = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"

    @property
    def due_amount(self):
        return self.fee_total - self.fee_paid

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

# ==========================================
# 3. PARENTS MODULE
# ==========================================

class Parent(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='parents')
    relation = models.CharField(max_length=50, choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Guardian', 'Guardian')])
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.relation})"

# ==========================================
# 4. TRANSPORT MODULE (Advanced)
# ==========================================

class TransportRoute(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    route_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=20)

    def __str__(self):
        return self.route_name

class StudentTransport(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.OneToOneField(Member, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True)
    pickup_point = models.CharField(max_length=100)
    monthly_fee = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.firstname} - {self.route.route_name}"

# ==========================================
# 5. HOSTEL MODULE
# ==========================================

class HostelRoom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    room_number = models.CharField(max_length=20)
    capacity = models.IntegerField(default=2)
    type = models.CharField(max_length=20, choices=[('AC', 'AC'), ('Non-AC', 'Non-AC')], default='Non-AC')
    cost_per_year = models.IntegerField()

    def __str__(self):
        return f"Room {self.room_number} ({self.type})"

class StudentHostel(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.OneToOneField(Member, on_delete=models.CASCADE)
    room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True)
    join_date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.student.firstname} - Room {self.room.room_number}"

# ==========================================
# 6. DOCUMENTS & SCHOLARSHIPS
# ==========================================

class StudentDocument(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    document_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='student_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} - {self.student.firstname}"

class Scholarship(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    discount_amount = models.IntegerField()
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class StudentScholarship(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    awarded_date = models.DateField(default=timezone.now)

# ==========================================
# 7. EXAMS, ATTENDANCE & UTILITIES
# ==========================================

class Attendance(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave')])
    
    class Meta:
        unique_together = ('student', 'date')

class ExamScore(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100, default="Mid-Term")
    maths = models.IntegerField(default=0)
    physics = models.IntegerField(default=0)
    chemistry = models.IntegerField(default=0)
    english = models.IntegerField(default=0)
    computer = models.IntegerField(default=0)

class Notice(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.IntegerField()
    date = models.DateField(auto_now_add=True)

class StudyMaterial(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=50)
    class_name = models.CharField(max_length=10)
    pdf_file = models.FileField(upload_to='materials/pdfs/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# ==========================================
# 8. PAYMENT GATEWAY
# ==========================================

class Payment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)

# ==========================================
# 9. USER PROFILE & SAAS SECURITY (Phase 3 Block 1)
# ==========================================

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=[('Admin', 'Admin'), ('Teacher', 'Teacher'), ('Staff', 'Staff')], default='Staff')
    
    def __str__(self):
        return f"{self.user.username} - {self.school.name if self.school else 'No School'}"

# Signal: Automatically create a UserProfile when a User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

# ... (Previous code remains same) ...

# ==========================================
# 10. LIBRARY MANAGEMENT MODULE
# ==========================================

class Book(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=50, blank=True, null=True, help_text="ISBN or Barcode ID")
    category = models.CharField(max_length=100, default="General")
    
    # Inventory
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.available_copies}/{self.total_copies})"

class LibraryTransaction(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    
    fine_amount = models.IntegerField(default=0, help_text="Calculated automatically if late")
    status = models.CharField(max_length=20, choices=[('Issued', 'Issued'), ('Returned', 'Returned')], default='Issued')

    def __str__(self):
        return f"{self.student.firstname} - {self.book.title}"

    # Auto-Calculate Fine Logic
    @property
    def days_overdue(self):
        from datetime import date
        if self.return_date:
            end_date = self.return_date
        else:
            end_date = date.today()
            
        if end_date > self.due_date:
            return (end_date - self.due_date).days
        return 0
    
# ... (Previous code) ...

# ==========================================
# 12. HR & PAYROLL MODULE
# ==========================================

class Staff(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=15)
    
    designation = models.CharField(max_length=100, choices=[
        ('Teacher', 'Teacher'), 
        ('Principal', 'Principal'),
        ('Accountant', 'Accountant'),
        ('Driver', 'Driver'),
        ('Cleaner', 'Cleaner'),
        ('Other', 'Other')
    ])
    
    salary = models.IntegerField(default=0, help_text="Monthly Salary")
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.designation})"