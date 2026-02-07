from .auth import TenantLoginView
from .dashboard import index, add_notice, delete_notice, debug_test
from .students import all_students, student_profile, update
from .academic import (
    attendance, attendance_records, report_card, add_marks, marksheet_pdf
)
from .finance import (
    fee_home, collect_fee, fee_config, generate_monthly_dues, 
    receipt_pdf, delete_fee, get_fee_amount, add_expense
)
from .library import (
    library, digital_library, add_book, issue_book, 
    return_book, delete_book, export_library_history
)
from .hr import staff_list, add_staff, pay_salary, salary_slip_pdf
from .transport import transport_home, add_route, transport_assign