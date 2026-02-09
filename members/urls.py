from django.urls import path
from django.contrib.auth import views as auth_views
from importlib import import_module

from .views.dashboard import index, landing
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
timetable_views = import_module("members.views.timetable")
admissions_views = import_module("members.views.admissions")
parent_views = import_module("members.views.parent_portal")
notification_views = import_module("members.views.notifications")

urlpatterns = [
    path("", landing, name="landing"),
    path("dashboard/", index, name="index"),
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
    path("academic/subjects/", academic.subject_list, name="subject_list"),
    path("academic/subjects/<int:pk>/edit/", academic.subject_edit, name="subject_edit"),
    path("academic/exam-types/", academic.exam_type_list, name="exam_type_list"),
    path("academic/exam-types/<int:pk>/edit/", academic.exam_type_edit, name="exam_type_edit"),

    path("finance/", finance.fee_home, name="fee_home"),
    path("finance/collect/", finance.collect_fee, name="collect_fee"),
    path("finance/config/", finance.fee_config, name="fee_config"),
    path("finance/get-fee/", finance.get_fee_amount, name="get_fee_amount"),
    path("finance/receipt/<int:id>/", finance.receipt_pdf, name="receipt_pdf"),
    path("finance/delete/<int:id>/", finance.delete_fee, name="delete_fee"),
    path("finance/student-receipt/<int:student_id>/", finance.student_receipt_pdf, name="student_receipt_pdf"),
    path("finance/add-expense/", finance.add_expense, name="add_expense"),
    path("finance/generate-invoices/", finance.generate_monthly_dues, name="generate_monthly_dues"),
    path("finance/installments/", finance.fee_installments, name="fee_installments"),
    path("finance/discounts/", finance.fee_discounts, name="fee_discounts"),
    path("finance/discounts/add/", finance.fee_discount_add, name="fee_discount_add"),
    path("finance/discounts/<int:pk>/edit/", finance.fee_discount_edit, name="fee_discount_edit"),
    path("finance/discounts/<int:pk>/delete/", finance.fee_discount_delete, name="fee_discount_delete"),
    path("finance/concessions/", finance.fee_concessions, name="fee_concessions"),
    path("finance/late-fee-policy/", finance.fee_late_fee_policy, name="fee_late_fee_policy"),
    path("finance/receipts/", finance.fee_receipts, name="fee_receipts"),
    path("finance/receipts/<int:receipt_id>/refund/", finance.fee_refund_request, name="fee_refund_request"),
    path("finance/refunds/", finance.fee_refunds, name="fee_refunds"),
    path("finance/refunds/<int:refund_id>/process/", finance.fee_refund_process, name="fee_refund_process"),

    path("add_notice/", dashboard.add_notice, name="add_notice"),
    path("delete_notice/<int:id>/", dashboard.delete_notice, name="delete_notice"),

    path("transport/", transport.transport_home, name="transport_home"),
    path("transport/add-route/", transport.add_route, name="add_route"),
    path("transport/assign/", transport.transport_assign, name="transport_assign"),

    path("timetable/", timetable_views.timetable_view, name="timetable_view"),
    path("timetable/edit/", timetable_views.timetable_edit, name="timetable_edit"),
    path("timetable/entry/<int:entry_id>/delete/", timetable_views.timetable_delete_entry, name="timetable_delete_entry"),

    path("admissions/enquiries/", admissions_views.enquiry_list, name="enquiry_list"),
    path("admissions/enquiries/add/", admissions_views.enquiry_add, name="enquiry_add"),
    path("admissions/enquiries/<int:pk>/edit/", admissions_views.enquiry_edit, name="enquiry_edit"),
    path("admissions/enquiries/<int:pk>/convert/", admissions_views.enquiry_convert, name="enquiry_convert"),
    path("admissions/enquiries/<int:pk>/status/", admissions_views.enquiry_change_status, name="enquiry_change_status"),

    path("parent/", parent_views.parent_dashboard, name="parent_dashboard"),
    path("parent/student/<int:student_id>/", parent_views.parent_student_detail, name="parent_student_detail"),

    path("notifications/", notification_views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/read/", notification_views.notification_mark_read, name="notification_mark_read"),
    path("notifications/read-all/", notification_views.notification_mark_all_read, name="notification_mark_all_read"),
    path("notifications/send/", notification_views.notification_send, name="notification_send"),

    path("hr/staff/", hr.staff_list, name="staff_list"),
    path("hr/staff/add/", hr.add_staff, name="add_staff"),
    path("hr/salary/pay/", hr.pay_salary, name="pay_salary"),
    path("hr/salary/slip/<int:id>/", hr.salary_slip_pdf, name="salary_slip_pdf"),

    path("school/settings/", school_views.school_settings, name="school_settings"),
    path("school/users/", school_views.school_user_list, name="school_user_list"),
    path("school/users/add/", school_views.school_user_add, name="school_user_add"),
    path("school/users/<int:user_id>/edit/", school_views.school_user_edit, name="school_user_edit"),
    path("school/users/<int:user_id>/deactivate/", school_views.school_user_deactivate, name="school_user_deactivate"),
    path("school/academic-years/", school_views.academic_year_list, name="academic_year_list"),
    path("school/academic-years/<int:year_id>/edit/", school_views.academic_year_edit, name="academic_year_edit"),
    path("school/backup/", school_views.school_backup_json, name="school_backup_json"),
    path("school/dismiss-getting-started/", school_views.dismiss_getting_started, name="dismiss_getting_started"),
    path("onboarding/", school_views.onboarding_wizard, name="onboarding"),
    path("schools/", school_views.school_list, name="school_list"),
    path("schools/add/", school_views.add_school, name="add_school"),

    path("profile/", user_profile, name="user_profile"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/accounts/login/"), name="logout"),

    path("debug-test/", dashboard.debug_test, name="debug_test"),
]
