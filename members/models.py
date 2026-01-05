from django.db import models

# --- MEMBER (STUDENT) MODEL ---
class Member(models.Model):
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
  phone = models.IntegerField(null=True)
  joined_date = models.DateField(null=True)
  # Note: upload_to folder name should be consistent
  profile_pic = models.ImageField(null=True, blank=True, upload_to="images/")
  
  fee_total = models.IntegerField(default=0)  # Total fees (e.g. 20000)
  fee_paid = models.IntegerField(default=0)   # Ab tak kitni di hai (e.g. 5000)

  # ✅ CORRECT LOCATION: Ye function Member class ke andar hona chahiye
  @property
  def due_amount(self):
      return self.fee_total - self.fee_paid

  def __str__(self):
    return f"{self.firstname} {self.lastname}"


# --- STUDY MATERIAL MODEL ---
class StudyMaterial(models.Model):
    SUBJECT_CHOICES = [
        ('Maths', 'Mathematics'),
        ('Physics', 'Physics'),
        ('Chemistry', 'Chemistry'),
        ('Biology', 'Biology'),
        ('English', 'English'),
    ]
    
    CLASS_CHOICES = [
        ('10', 'Class 10'),
        ('11', 'Class 11'),
        ('12', 'Class 12'),
    ]

    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    class_name = models.CharField(max_length=10, choices=CLASS_CHOICES, verbose_name="Class")
    pdf_file = models.FileField(upload_to='materials/pdfs/', blank=True, null=True)
    video_link = models.URLField(blank=True, null=True, help_text="Paste YouTube Video Link here")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.subject})"


# --- ATTENDANCE MODEL ---
class Attendance(models.Model):
    student = models.ForeignKey(Member, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent'), ('Leave', 'Leave')])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'date')  # Ek student ki ek din mein ek hi attendance lagegi
    
    def __str__(self):
        return f"{self.student.firstname} - {self.date} - {self.status}"