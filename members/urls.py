from django.urls import path
from django.contrib.auth import views as auth_views
from importlib import import_module

from .views.dashboard import index
from .views.auth import user_profile
dashboard = import_module("members.views.dashboard")
students = import_module("members.views.students")
academic = import_module("members.views.academic")
finance = import_module("members.views.finance")
hr = import_module("members.views.hr")
library_views = import_module("members.views.library")
learning_views = import_module("members.views.learning")
school_views = import_module("members.views.schools")
transport = import_module("members.views.transport")

urlpatterns = [
    path("", index, name="index"),
    path("members/", index, name="members"),

    path("students/all/", students.all_students, name="all_students"),
    path("students/profile/<int:id>/", students.student_profile, name="student_profile"),
    path("students/create-login/<int:id>/", students.create_student_login, name="create_student_login"),
    path("students/update/<int:id>/", students.update, name="update_student"),
    path("students/add/", students.add, name="add"),
    path("students/addrecord/", students.addrecord, name="addrecord"),
    path("students/edit/<int:id>/", students.update, name="update"),
    path("students/delete/<int:id>/", students.delete, name="delete"),
    path("students/id-card/<int:id>/", students.id_card, name="id_card"),
    path("students/check-admission-no/", students.check_admission_number, name="check_admission_number"),
    path("students/receipt/<int:id>/", students.admission_receipt_pdf, name="admission_receipt_pdf"),

    path("attendance/", academic.attendance, name="attendance"),
    path("attendance_records/", academic.attendance_records, name="attendance_records"),

    path("library/", library_views.library, name="library_home"),
    path("library/add_book/", library_views.add_book, name="add_book"),
    path("library/issue_book/", library_views.issue_book, name="issue_book"),
    path("library/return_book/<int:id>/", library_views.return_book, name="return_book"),
    path("library/export/", library_views.export_library_history, name="export_library"),
    path("library/delete_book/<int:id>/", library_views.delete_book, name="delete_book"),

    path("learning/", learning_views.learning_hub, name="learning_hub"),
    path("learning/delete/<int:id>/", learning_views.delete_study_material, name="delete_study_material"),
    path("student/", learning_views.student_portal, name="student_portal"),

    path("add_marks/", academic.add_marks, name="add_marks"),
    path("report_card/", academic.report_card, name="report_card"),
    path("marksheet_pdf/<int:id>/", academic.marksheet_pdf, name="marksheet_pdf"),

    path("finance/", finance.fee_home, name="fee_home"),
    path("finance/collect/", finance.collect_fee, name="collect_fee"),
    path("finance/config/", finance.fee_config, name="fee_config"),
    path("finance/get-fee/", finance.get_fee_amount, name="get_fee_amount"),
    path("finance/receipt/<int:id>/", finance.receipt_pdf, name="receipt_pdf"),
    path("finance/delete/<int:id>/", finance.delete_fee, name="delete_fee"),
    path("finance/student-receipt/<int:student_id>/", finance.student_receipt_pdf, name="student_receipt_pdf"),
    path("finance/add-expense/", finance.add_expense, name="add_expense"),
    path("finance/generate-invoices/", finance.generate_monthly_dues, name="generate_monthly_dues"),

    path("add_notice/", dashboard.add_notice, name="add_notice"),
    path("delete_notice/<int:id>/", dashboard.delete_notice, name="delete_notice"),

    path("transport/", transport.transport_home, name="transport_home"),
    path("transport/add-route/", transport.add_route, name="add_route"),
    path("transport/assign/", transport.transport_assign, name="transport_assign"),

    path("hr/staff/", hr.staff_list, name="staff_list"),
    path("hr/staff/add/", hr.add_staff, name="add_staff"),
    path("hr/salary/pay/", hr.pay_salary, name="pay_salary"),
    path("hr/salary/slip/<int:id>/", hr.salary_slip_pdf, name="salary_slip_pdf"),

    path("school/settings/", school_views.school_settings, name="school_settings"),
    path("schools/", school_views.school_list, name="school_list"),
    path("schools/add/", school_views.add_school, name="add_school"),

    path("profile/", user_profile, name="user_profile"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/accounts/login/"), name="logout"),

    path("debug-test/", dashboard.debug_test, name="debug_test"),
]
