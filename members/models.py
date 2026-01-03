from django.db import models

class Member(models.Model):
    """
    Represents a student in the Student Management System.
    Stores personal details and profile picture.
    """

    # --- Personal Information ---
    firstname = models.CharField(max_length=255, help_text="Enter first name")
    lastname = models.CharField(max_length=255, help_text="Enter last name")

    # --- Media Fields ---
    # Images will be stored in 'media/student_images/' folder
    profile_pic = models.ImageField(
        upload_to='student_images/', 
        blank=True, 
        null=True,
        help_text="Upload a profile picture (Optional)"
    )

    class Meta:
        """
        Metadata options for the model.
        """
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['firstname']  # Default sorting: A to Z by First Name

    def __str__(self):
        """
        String representation of the object (e.g., showing Name in Admin panel).
        """
        return f"{self.firstname} {self.lastname}"