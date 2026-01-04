from django.db import models

class Member(models.Model):
  firstname = models.CharField(max_length=255)
  lastname = models.CharField(max_length=255)
  phone = models.IntegerField(null=True)
  joined_date = models.DateField(null=True)
  profile_pic = models.ImageField(null=True, blank=True, upload_to="images/")

  def __str__(self):
    return f"{self.firstname} {self.lastname}"

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