from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ==============================
    # 🏠 DASHBOARD
    # ==============================
    path('', views.index, name='index'),
    path('members/', views.index, name='members'),  # Backup link

    # ==============================
    # 🎓 STUDENT MANAGEMENT
    # ==============================
    path('students/all/', views.all_students, name='all_students'),
    path('profile/<int:id>/', views.student_profile, name='student_profile'),
    path('add/', views.add, name='add'),
    path('add/addrecord/', views.addrecord, name='addrecord'),
    path('delete/<int:id>/', views.delete, name='delete'),
    path('update/<int:id>/', views.update, name='update'),
    path('updaterecord/<int:id>/', views.updaterecord, name='updaterecord'),

    # ==============================
    # 📂 IMPORT / EXPORT
    # ==============================
    path('import_students/', views.import_students, name='import_students'),
    path('export_excel/', views.export_excel, name='export_excel'),

    # ==============================
    # 📅 ATTENDANCE
    # ==============================
    path('attendance/', views.attendance, name='attendance'),
    path('attendance_records/', views.attendance_records, name='attendance_records'),

    # ==============================
    # 📚 LIBRARY (Physical Books)
    # ==============================
    path('library/', views.library, name='library_home'), 
    path('library/add/', views.add_book, name='add_book'),
    path('library/issue/', views.issue_book, name='issue_book'),
    path('library/return/<int:id>/', views.return_book, name='return_book'),

    # ==============================
    # 💻 DIGITAL LIBRARY (PDFs)
    # ==============================
   # path('digital-library/', views.digital_library, name='digital_library'),
    path('library/', views.library, name='library'),

    # ==============================
    # 📊 EXAMS & RESULTS
    # ==============================
    path('add_marks/', views.add_marks, name='add_marks'),
    path('report_card/', views.report_card, name='report_card'),
    path('marksheet_pdf/<int:id>/', views.marksheet_pdf, name='marksheet_pdf'),

    # ==============================
    # 💰 FINANCE & FEES (UPDATED)
    # ==============================
    path('finance/', views.fee_home, name='fee_home'),
    path('finance/collect/', views.collect_fee, name='collect_fee'),
    path('finance/config/', views.fee_config, name='fee_config'),
    path('finance/get-fee/', views.get_fee_amount, name='get_fee_amount'), # API
    
    # ✅ NEW PATHS FOR RECEIPT & DELETE
    path('finance/receipt/<int:id>/', views.receipt_pdf, name='receipt_pdf'),
    path('finance/delete/<int:id>/', views.delete_fee, name='delete_fee'),
    
    path('add_expense/', views.add_expense, name='add_expense'),

    # ==============================
    # 🪪 NOTICES & IDENTITY
    # ==============================
    path('id_card/<int:id>/', views.id_card, name='id_card'),
    path('add_notice/', views.add_notice, name='add_notice'),
    path('delete_notice/<int:id>/', views.delete_notice, name='delete_notice'),

    # ==============================
    # 🚌 TRANSPORT
    # ==============================
    path('transport/', views.transport_home, name='transport_home'),
    path('transport/add-route/', views.add_route, name='add_route'),
    path('transport/assign/', views.transport_assign, name='transport_assign'),

    # ==============================
    # 👔 HR & STAFF (FIXED)
    # ==============================
    path('hr/staff/', views.staff_list, name='staff_list'),
    path('hr/staff/add/', views.add_staff, name='add_staff'),  # ✅ Yeh line MISSING thi, ab add kar di hai
    path('hr/salary/pay/', views.pay_salary, name='pay_salary'),

    # ==============================
    # 🔐 AUTHENTICATION
    # ==============================
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ==============================
    # 📱 API
    # ==============================
    path('api/students/', views.student_api_list, name='student_api_list'),

    # ✅ NEW: Salary Slip PDF generate karne ka path
    path('hr/salary/slip/<int:id>/', views.salary_slip_pdf, name='salary_slip_pdf'),

    path('finance/generate-invoices/', views.generate_monthly_dues, name='generate_monthly_dues'),
    path('library/export/', views.export_library_history, name='export_library_history'),


    path('library/delete/<int:id>/', views.delete_book, name='delete_book'),
    
   
]