from django.contrib import admin
# Saare models ko import kar rahe hain
from .models import (
    Member, StudyMaterial, Attendance, ExamScore, Notice, Expense,
    AcademicYear, ClassRoom, Parent, TransportRoute, StudentTransport,
    HostelRoom, StudentHostel
)

# --- 1. STUDENT ADMIN (Advanced View) ---
class MemberAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'student_class', 'mobile_number', 'father_name')
    search_fields = ('firstname', 'admission_no', 'mobile_number')
    list_filter = ('student_class', 'gender')

# --- 2. ATTENDANCE ADMIN ---
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status')
    list_filter = ('date', 'status')

# --- 3. TRANSPORT ADMIN ---
class TransportAdmin(admin.ModelAdmin):
    list_display = ('route_name', 'driver_name', 'vehicle_number', 'driver_phone')

class StudentTransportAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'pickup_point', 'monthly_fee')
    list_filter = ('route',)

# --- 4. HOSTEL ADMIN ---
class HostelRoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'type', 'capacity', 'cost_per_year')
    list_filter = ('type',)

class StudentHostelAdmin(admin.ModelAdmin):
    list_display = ('student', 'room', 'join_date')

# --- 5. PARENT ADMIN ---
class ParentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student', 'relation', 'phone')
    search_fields = ('name', 'phone')

# --- REGISTER ALL MODELS ---
admin.site.register(Member, MemberAdmin)
admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(TransportRoute, TransportAdmin)
admin.site.register(StudentTransport, StudentTransportAdmin)
admin.site.register(HostelRoom, HostelRoomAdmin)
admin.site.register(StudentHostel, StudentHostelAdmin)
admin.site.register(Parent, ParentAdmin)

# Simple Registrations (Jinke liye custom view zaroori nahi)
admin.site.register(StudyMaterial)
admin.site.register(ExamScore)
admin.site.register(Notice)
admin.site.register(Expense)
admin.site.register(AcademicYear)
admin.site.register(ClassRoom)