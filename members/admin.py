from django.contrib import admin
from .models import Member, StudyMaterial, Attendance

# Attendance ko Admin panel me acche se dikhane ke liye setting
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status') # Columns dikhenge
    list_filter = ('date', 'status')             # Filter karne ka option aayega

# Models ko register karo
admin.site.register(Member)
admin.site.register(StudyMaterial)
admin.site.register(Attendance, AttendanceAdmin) # <-- Ye line zaroori hai