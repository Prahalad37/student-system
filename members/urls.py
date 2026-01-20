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
    # 📂 IMPORT / EXPORT (EXCEL)
    # ==============================
    path('import_students/', views.import_students, name='import_students'),
    path('export_excel/', views.export_excel, name='export_excel'),

    # ==============================
    # 📅 ATTENDANCE
    # ==============================
    path('attendance/', views.attendance, name='attendance'),
    path('attendance_records/', views.attendance_records, name='attendance_records'),

    # ==============================
    # 📚 ACADEMICS (Library & Exams)
    # ==============================
    path('library/', views.library, name='library'),
    path('add_marks/', views.add_marks, name='add_marks'),
    path('report_card/', views.report_card, name='report_card'),
    path('marksheet_pdf/<int:id>/', views.marksheet_pdf, name='marksheet_pdf'),

    # ==============================
    # 💰 FINANCE (Fees & Expenses)
    # ==============================
    path('add_expense/', views.add_expense, name='add_expense'),
    path('receipt/<int:id>/', views.receipt_pdf, name='receipt_pdf'),

    # ==============================
    # 🪪 NOTICES & IDENTITY
    # ==============================
    path('id_card/<int:id>/', views.id_card, name='id_card'),
    path('add_notice/', views.add_notice, name='add_notice'),
    path('delete_notice/<int:id>/', views.delete_notice, name='delete_notice'),

    # ==============================
    # 🔐 AUTHENTICATION (Login/Logout)
    # ==============================
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ==============================
    # 📱 MOBILE API (New)
    # ==============================
    path('api/students/', views.student_api_list, name='student_api_list'),

    
    # ==============================
    # LIBRARY PATHS
    # ==============================
    path('library/', views.library_home, name='library_home'),
    path('library/add/', views.add_book, name='add_book'),
    path('library/issue/', views.issue_book, name='issue_book'),
    path('library/return/<int:id>/', views.return_book, name='return_book'),

    # ==============================
    # TRANSPORT PATHS
    # ==============================
    path('transport/', views.transport_home, name='transport_home'),
    path('transport/add-route/', views.add_route, name='add_route'),
    path('transport/assign/', views.transport_assign, name='transport_assign'),

    # HR Paths
    path('hr/staff/', views.staff_list, name='staff_list'),
    path('hr/staff/add/', views.add_staff, name='add_staff'),
]