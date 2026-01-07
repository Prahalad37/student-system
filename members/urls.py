from django.urls import path
from . import views  # Ye 'members' folder ke andar hai, isliye yahan views mil jayega
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.index, name='index'),
    path('add/', views.add, name='add'),
    path('add/addrecord/', views.addrecord, name='addrecord'),
    path('delete/<int:id>', views.delete, name='delete'),
    path('update/<int:id>', views.update, name='update'),
    path('updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    
    # Library ka rasta
    path('library/', views.library, name='library'),
    path('attendance/', views.attendance, name='attendance'),
    path('attendance_records/', views.attendance_records, name='attendance_records'),

    # Login Page
   path('accounts/login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

    # Logout Action
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('add_marks/', views.add_marks, name='add_marks'),
    path('report_card/', views.report_card, name='report_card'),
    # Student Profile
    path('profile/<int:id>/', views.student_profile, name='student_profile'),
    path('receipt/<int:id>/', views.receipt_pdf, name='receipt_pdf'),
    path('add_notice/', views.add_notice, name='add_notice'),
    path('delete_notice/<int:id>/', views.delete_notice, name='delete_notice'),
    path('id_card/<int:id>/', views.id_card, name='id_card'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('export_excel/', views.export_excel, name='export_excel'),
    path('import_students/', views.import_students, name='import_students'),
]