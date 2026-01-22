import uuid
from datetime import date
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# ==========================================
# 1. SCHOOL & ACADEMIC MODULE
# ==========================================

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    school_code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AcademicYear(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

class ClassRoom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, default='A')

    class Meta:
        unique_together = ('name', 'section') 

    def __str__(self):
        return f"{self.name} - {self.section}"

# ==========================================
# 2. STUDENT MODULE
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
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')], default='Male')
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    joined_date = models.DateField(auto_now_add=True, null=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="student_images/")
    
    # Extra Fields
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    medical_conditions = models.TextField(null=True, blank=True)
    transport_mode = models.CharField(max_length=20, null=True, blank=True)
    route_name = models.CharField(max_length=100, null=True, blank=True)
    house_team = models.CharField(max_length=20, null=True, blank=True)
    preferred_stream = models.CharField(max_length=50, null=True, blank=True)
    
    # Legacy Fee (Still needed for old code)
    fee_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fee_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

# ==========================================
# 3. CORE UTILITIES
# ==========================================

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, default='Staff')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_school = School.objects.first()
        UserProfile.objects.create(user=instance, school=default_school, role='Admin')

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()

# ==========================================
# 4. LIBRARY MODULE
# ==========================================

class Book(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=50, blank=True, null=True)
    category = models.CharField(max_length=100, default="General")
    total_copies = models.IntegerField(default=1)
    available_copies = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class LibraryTransaction(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    status = models.CharField(max_length=20, default='Issued')

    def __str__(self):
        return f"{self.student.firstname} - {self.book.title}"

# ==========================================
# 5. TRANSPORT, HR, EXAMS (Support Models)
# ==========================================

# Check members/models.py for these:
class TransportRoute(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    route_name = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=50)
    driver_name = models.CharField(max_length=100)
    driver_phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.route_name} ({self.vehicle_number})"

class StudentTransport(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.OneToOneField(Member, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE)
    pickup_point = models.CharField(max_length=100, blank=True)
    monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.student.firstname} - {self.route.route_name}"

class Staff(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15)
    designation = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    join_date = models.DateField()
    is_active = models.BooleanField(default=True)

class ExamScore(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    exam_name = models.CharField(max_length=100)
    maths = models.IntegerField(default=0)
    physics = models.IntegerField(default=0)
    chemistry = models.IntegerField(default=0)
    english = models.IntegerField(default=0)
    computer = models.IntegerField(default=0)
    # Aap naye subjects bhi add kar sakte hain yahan

class Attendance(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)

class Notice(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    pdf_file = models.FileField(upload_to='materials/', null=True)
    video_link = models.URLField(null=True)

class Payment(models.Model): # Legacy
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

# ==========================================
# 💰 6. FINANCE & FEES (PHASE 4 - CRITICAL)
# ==========================================

class FeeStructure(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    class_room = models.ForeignKey(ClassRoom, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.class_room.name}"

class FeeTransaction(models.Model):
    PAYMENT_MODES = [('Cash', 'Cash'), ('Online', 'Online'), ('Cheque', 'Cheque')]

    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=date.today)
    payment_mode = models.CharField(max_length=20, choices=PAYMENT_MODES, default='Cash')
    remarks = models.CharField(max_length=200, blank=True)
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            today_str = date.today().strftime('%Y%m%d')
            random_str = str(uuid.uuid4().int)[:4]
            self.receipt_number = f"REC-{today_str}-{random_str}"
        super().save(*args, **kwargs)
        
        # Sync with Member Table
        student = self.student
        current_total = student.fee_paid if student.fee_paid else 0
        student.fee_paid = float(current_total) + float(self.amount_paid)
        student.save()

    def __str__(self):
        return f"{self.student.firstname} - ₹{self.amount_paid}"
    
    # ==========================================
# 💼 HR & PAYROLL (PHASE 5)
# ==========================================

class SalaryTransaction(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True)
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=date.today)
    
    # Month for which salary is paid (e.g., "January 2026")
    month_year = models.CharField(max_length=50) 
    
    payment_mode = models.CharField(max_length=20, choices=[('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer'), ('Cheque', 'Cheque')], default='Bank Transfer')
    remarks = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.staff.first_name} - {self.month_year}"
    
    # members/models.py mein ensure karein
class FeeTransaction(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    month_year = models.CharField(max_length=20) # e.g., "January 2026"
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Paid') # Paid, Partial, Unpaid