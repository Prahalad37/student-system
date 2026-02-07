import uuid
from datetime import date
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# ==========================================
# 1. SCHOOL & ACADEMIC MODULE
# ==========================================

class School(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    school_code = models.CharField(max_length=50, unique=True)
    code = models.SlugField(max_length=64, unique=True, help_text="Lower, slug-friendly subdomain (e.g. acme)")
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
    
    # ========== PHASE 1: CRITICAL ADMISSION FIELDS (15 fields) ==========
    # Mother's Information (3 fields)
    mother_name = models.CharField(max_length=100, blank=True, null=True)
    mother_mobile = models.CharField(max_length=15, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    
    # Father's Additional Info (1 field)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    
    # Government & Identity (4 fields)
    aadhaar_number = models.CharField(max_length=12, blank=True, null=True, unique=True, help_text="12-digit Aadhaar number")
    caste_category = models.CharField(max_length=20, choices=[
        ('General', 'General'),
        ('OBC', 'OBC'),
        ('SC', 'SC'),
        ('ST', 'ST'),
        ('EWS', 'EWS')
    ], default='General', blank=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=50, default='Indian', blank=True)
    
    # Previous Education (3 fields)
    previous_school = models.CharField(max_length=200, blank=True, null=True)
    previous_class = models.CharField(max_length=50, blank=True, null=True, help_text="Last class attended")
    tc_number = models.CharField(max_length=50, blank=True, null=True, help_text="Transfer Certificate number")
    
    # Emergency Contact (3 fields)
    emergency_contact_person = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=15, blank=True, null=True)
    emergency_relationship = models.CharField(max_length=50, blank=True, null=True, help_text="Relationship with student")
    
    # Additional Contact (1 field)
    whatsapp_number = models.CharField(max_length=15, blank=True, null=True)
    
    # ========== PHASE 2: COMPLIANCE & MEDICAL FIELDS (20 fields) ==========
    # Medical Information (6 fields)
    known_allergies = models.TextField(blank=True, null=True, help_text="Food, medicine, or other allergies")
    chronic_conditions = models.TextField(blank=True, null=True, help_text="Diabetes, Asthma, etc.")
    vaccination_status = models.CharField(max_length=100, blank=True, null=True, help_text="COVID-19, MMR, etc.")
    family_doctor_name = models.CharField(max_length=100, blank=True, null=True)
    family_doctor_phone = models.CharField(max_length=15, blank=True, null=True)
    special_needs = models.TextField(blank=True, null=True, help_text="Physical or learning disabilities")
    
    # Family Financial (2 fields)
    annual_income = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, help_text="Annual family income")
    parent_education = models.CharField(max_length=100, blank=True, null=True, help_text="Highest education of parents")
    
    # Guardian Information (3 fields) - if different from parents
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_relationship = models.CharField(max_length=50, blank=True, null=True, help_text="Grandparent, Uncle, etc.")
    guardian_contact = models.CharField(max_length=15, blank=True, null=True)
    
    # Document Uploads (5 fields)
    birth_certificate = models.FileField(upload_to='documents/birth_certificates/', blank=True, null=True)
    aadhaar_card = models.FileField(upload_to='documents/aadhaar/', blank=True, null=True)
    transfer_certificate = models.FileField(upload_to='documents/tc/', blank=True, null=True)
    previous_marksheet = models.FileField(upload_to='documents/marksheets/', blank=True, null=True)
    photo_id = models.FileField(upload_to='documents/photo_ids/', blank=True, null=True)
    
    # Sibling Information (2 fields)
    sibling_in_school = models.BooleanField(default=False, help_text="Does student have siblings in this school?")
    sibling_details = models.TextField(blank=True, null=True, help_text="Name, Class, Admission No of siblings")
    
    # Additional Contacts (2 fields)
    alternate_email = models.EmailField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True, help_text="If different from current address")
    
    # ========== PHASE 3: CONSENT & PERMISSIONS (3 fields) ==========
    terms_consent = models.BooleanField(default=False, help_text="Agreement to school terms and conditions")
    photo_permission = models.BooleanField(default=False, help_text="Permission to use photos/videos")
    communication_consent = models.BooleanField(default=True, help_text="Consent for SMS/Email notifications")

    def __str__(self):
        return f"{self.firstname} {self.lastname}"

# ==========================================
# 3. CORE UTILITIES
# ==========================================

ROLE_CHOICES = [
    ("OWNER", "OWNER"),
    ("ADMIN", "ADMIN"),
    ("ACCOUNTANT", "ACCOUNTANT"),
    ("TEACHER", "TEACHER"),
    ("STAFF", "STAFF"),
    ("STUDENT", "STUDENT"),
]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="OWNER")
    member = models.ForeignKey("Member", on_delete=models.SET_NULL, null=True, blank=True,
                               related_name="user_profiles", help_text="Linked student when role=STUDENT")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        default_school = School.objects.first()
        UserProfile.objects.create(user=instance, school=default_school, role="OWNER")
    else:
        # Update existing profile if it exists
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

class TransportZone(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    base_monthly_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('school', 'name')

    def __str__(self):
        return f"{self.school.name} - {self.name}"

class TransportStop(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    zone = models.ForeignKey(TransportZone, on_delete=models.CASCADE, related_name='stops')
    name = models.CharField(max_length=120)
    stop_code = models.CharField(max_length=50)
    monthly_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        unique_together = ('school', 'stop_code')

    def __str__(self):
        return f"{self.zone.name} - {self.name}"

class StudentTransport(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.OneToOneField(Member, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE)
    zone = models.ForeignKey(TransportZone, on_delete=models.SET_NULL, null=True, blank=True)
    stop = models.ForeignKey(TransportStop, on_delete=models.SET_NULL, null=True, blank=True)
    billing_mode = models.CharField(
        max_length=20,
        choices=[('Manual', 'Manual'), ('Zone', 'Zone'), ('Stop', 'Stop'), ('Hybrid', 'Hybrid')],
        default='Manual',
    )
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
    created_at = models.DateTimeField(auto_now_add=True)
    generated_report = models.FileField(upload_to='reports/', null=True, blank=True)
    # Aap naye subjects bhi add kar sakte hain yahan

class Attendance(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10)
    
    class Meta:
        unique_together = ('student', 'date')
        verbose_name_plural = 'Attendance Records'

class Notice(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Expense(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)

class StudyMaterial(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=50)
    pdf_file = models.FileField(upload_to='materials/', null=True, blank=True)
    video_link = models.URLField(null=True, blank=True, help_text="YouTube or other video URL")

    def __str__(self):
        return f"{self.title} ({self.subject} - {self.class_name})"

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
    
# ==========================================
# 💳 FEES TRANSACTIONS (LEGACY RECEIPTS)
# - Aligned to migrations 0019+ (month_year/status, no receipt_number column)
# ==========================================

class FeeTransaction(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    month_year = models.CharField(max_length=20) # e.g., "January 2026"
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Paid') # Paid, Partial, Unpaid

    def __str__(self):
        return f"{self.student.firstname} - ₹{self.amount_paid} ({self.payment_mode})"

    @property
    def receipt_code(self) -> str:
        return f"REC-{self.payment_date.strftime('%Y%m%d')}-{self.id}"


# ==========================================
# ✅ FINANCE ENGINE v2 (Installments + Payments + Refunds)
# ==========================================

class LateFeePolicy(models.Model):
    school = models.OneToOneField(School, on_delete=models.CASCADE)
    grace_days = models.PositiveIntegerField(default=0)
    per_day_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cap_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.school.name} late fee policy"


class FeeDiscount(models.Model):
    DISCOUNT_TYPES = [('Percent', 'Percent'), ('Fixed', 'Fixed')]
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES, default='Fixed')
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_concession = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('school', 'name')

    def __str__(self):
        return f"{self.school.name} - {self.name}"


class StudentConcession(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    discount = models.ForeignKey(FeeDiscount, on_delete=models.CASCADE)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('school', 'student', 'discount')


class FeeInstallment(models.Model):
    QUARTERS = [('Q1', 'Q1'), ('Q2', 'Q2'), ('Q3', 'Q3'), ('Q4', 'Q4')]
    STATUSES = [('Due', 'Due'), ('Partial', 'Partial'), ('Paid', 'Paid'), ('Waived', 'Waived')]

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)
    quarter = models.CharField(max_length=2, choices=QUARTERS)
    due_date = models.DateField()
    principal_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    late_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUSES, default='Due')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'student', 'academic_year', 'quarter')

    @property
    def net_due(self):
        return (self.principal_amount + self.late_fee_amount) - self.discount_amount

    @property
    def remaining(self):
        return max(self.net_due - self.paid_amount, 0)


class FeePaymentReceipt(models.Model):
    MODES = [('Cash', 'Cash'), ('UPI', 'UPI'), ('Bank', 'Bank'), ('Cheque', 'Cheque'), ('Gateway', 'Gateway')]
    STATUSES = [('Success', 'Success'), ('Pending', 'Pending'), ('Failed', 'Failed')]

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.CharField(max_length=20, choices=MODES)
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='Success')

    upi_ref = models.CharField(max_length=120, blank=True)
    bank_ref = models.CharField(max_length=120, blank=True)
    cheque_no = models.CharField(max_length=60, blank=True)
    gateway_order_id = models.CharField(max_length=120, blank=True)
    gateway_payment_id = models.CharField(max_length=120, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    legacy_fee_transaction = models.OneToOneField(FeeTransaction, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.student.firstname} - ₹{self.amount} ({self.mode})"


class FeePaymentAllocation(models.Model):
    receipt = models.ForeignKey(FeePaymentReceipt, on_delete=models.CASCADE, related_name='allocations')
    installment = models.ForeignKey(FeeInstallment, on_delete=models.CASCADE, related_name='allocations')
    allocated_amount = models.DecimalField(max_digits=10, decimal_places=2)


class FeeRefund(models.Model):
    STATUSES = [('Initiated', 'Initiated'), ('Processed', 'Processed'), ('Rejected', 'Rejected')]

    school = models.ForeignKey(School, on_delete=models.CASCADE)
    receipt = models.ForeignKey(FeePaymentReceipt, on_delete=models.CASCADE, related_name='refunds')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUSES, default='Initiated')
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)