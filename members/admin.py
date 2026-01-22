from django.contrib import admin
from .models import (
    School, UserProfile, Member, ClassRoom, AcademicYear,
    Attendance, Notice, Expense, StudyMaterial, ExamScore,
    TransportRoute, StudentTransport, Book, LibraryTransaction,
    Staff, SalaryTransaction, FeeStructure, FeeTransaction 
)

# --- 0. SAAS & SECURITY ADMIN ---
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'school_code', 'created_at')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'school', 'role')
    list_filter = ('school', 'role')

# --- 1. STUDENT ADMIN ---
class MemberAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'student_class', 'mobile_number')
    search_fields = ('firstname', 'admission_no', 'mobile_number')
    list_filter = ('student_class', 'gender')

# --- 2. ACADEMIC ADMIN ---
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')

# --- 3. TRANSPORT ADMIN ---
class TransportAdmin(admin.ModelAdmin):
    list_display = ('route_name', 'driver_name', 'vehicle_number')

class StudentTransportAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'pickup_point', 'monthly_fee')
    list_filter = ('route',)

# --- 4. LIBRARY ADMIN ---
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'available_copies')
    search_fields = ('title', 'isbn')

class LibraryTransactionAdmin(admin.ModelAdmin):
    list_display = ('student', 'book', 'issue_date', 'due_date', 'status')
    list_filter = ('status', 'due_date')

# --- 5. HR & PAYROLL ADMIN ---
class StaffAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'designation', 'phone', 'salary', 'is_active')
    list_filter = ('designation', 'is_active')
    search_fields = ('first_name', 'phone')

class SalaryTransactionAdmin(admin.ModelAdmin):
    list_display = ('staff', 'amount_paid', 'month_year', 'payment_date', 'payment_mode')
    list_filter = ('month_year', 'payment_mode')
    search_fields = ('staff__first_name', 'month_year')

# --- 6. FINANCE ADMIN ---
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_room', 'amount')
    list_filter = ('class_room',)

class FeeTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'amount_paid', 'month_year', 'status', 'payment_date')
    list_filter = ('status', 'month_year')
    search_fields = ('student__firstname',)

# --- REGISTER ALL MODELS ---
admin.site.register(School, SchoolAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(ClassRoom, ClassRoomAdmin)
admin.site.register(AcademicYear)
admin.site.register(TransportRoute, TransportAdmin)
admin.site.register(StudentTransport, StudentTransportAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(LibraryTransaction, LibraryTransactionAdmin)
admin.site.register(Staff, StaffAdmin)
admin.site.register(SalaryTransaction, SalaryTransactionAdmin)
admin.site.register(FeeStructure, FeeStructureAdmin)
admin.site.register(FeeTransaction, FeeTransactionAdmin)
admin.site.register(Attendance)
admin.site.register(StudyMaterial)
admin.site.register(ExamScore)
admin.site.register(Notice)
admin.site.register(Expense)