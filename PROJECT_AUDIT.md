# Django ERP Project Audit Report
**Project:** Prahlad Academy ERP v2.0  
**Date:** January 28, 2026  
**Auditor:** AI Code Analysis

---

## 1. PROJECT OVERVIEW

### Project Structure
- **Framework:** Django 4.2.27
- **Project Name:** `mysite`
- **Main App:** `members`
- **Database:** SQLite3 (development)
- **Deployment:** PythonAnywhere (production)
- **Architecture:** Monolithic Django app with service layer pattern

### Key Features
- ✅ Student Management System
- ✅ Attendance Tracking
- ✅ Library Management (Physical Books)
- ✅ Finance & Fee Collection
- ✅ HR & Payroll
- ✅ Transport Management
- ✅ Academic Records (Exams, Marksheets)
- ✅ PWA Support (Progressive Web App)
- ✅ PDF Generation (Receipts, Marksheets, Salary Slips)

### Technology Stack
- **Backend:** Django 4.2.27, Django REST Framework
- **Task Queue:** Celery 5.3.6 + Redis 5.0.1
- **PDF Generation:** xhtml2pdf, reportlab
- **Excel Export:** xlwt, openpyxl
- **PWA:** django-pwa
- **CORS:** django-cors-headers

---

## 2. APPS OVERVIEW

### Main App: `members`
**Location:** `/mysite/members/`

**Structure:**
```
members/
├── models.py          # All data models (20+ models)
├── views/             # Modular view organization
│   ├── dashboard.py   # Main dashboard
│   ├── students.py    # Student CRUD
│   ├── academic.py   # Attendance, Exams
│   ├── finance.py     # Fees, Expenses
│   ├── library.py     # Library operations
│   ├── hr.py          # Staff & Payroll
│   └── transport.py   # Transport routes
├── services/          # Business logic layer
│   ├── finance.py     # Fee collection service
│   └── library.py     # Book issue/return service
├── templates/         # HTML templates (20+ files)
├── static/            # CSS, JS, images
├── forms.py           # Django forms (1 form: MemberForm)
├── serializers.py     # DRF serializers (1 serializer: StudentSerializer)
├── admin.py           # Django admin configuration
├── decorators.py      # Custom decorators (allowed_users)
├── utils.py           # Utility functions (get_current_school)
├── tasks.py           # Celery background tasks
└── urls.py            # URL routing (98 lines, 30+ routes)
```

**Key Design Patterns:**
- ✅ Service Layer Pattern (for finance & library)
- ✅ View Separation (views split by domain)
- ✅ Decorator-based Authentication (@login_required)
- ⚠️ Missing: Form validation layer, API versioning

---

## 3. URL STRUCTURE

### Root URLs (`mysite/urls.py`)
```
/ → members.urls (main app)
/admin/ → Django admin
/accounts/ → Django auth (login/logout)
/__debug__/ → Debug toolbar (DEBUG only)
```

### Members App URLs (`members/urls.py`)

**Dashboard:**
- `/` → `index` (dashboard)
- `/members/` → `index` (backup link)

**Student Management:**
- `/students/all/` → `all_students`
- `/students/profile/<id>/` → `student_profile`
- `/students/update/<id>/` → `update_student`

**Attendance:**
- `/attendance/` → `attendance` (mark attendance)
- `/attendance_records/` → `attendance_records` (view history)

**Library:**
- `/library/` → `library` (home)
- `/library/add_book/` → `add_book`
- `/library/issue_book/` → `issue_book`
- `/library/return_book/<id>/` → `return_book`
- `/library/delete_book/<id>/` → `delete_book`
- `/library/export/` → `export_library_history` (Excel)

**Finance:**
- `/finance/` → `fee_home`
- `/finance/collect/` → `collect_fee`
- `/finance/config/` → `fee_config`
- `/finance/receipt/<id>/` → `receipt_pdf`
- `/finance/delete/<id>/` → `delete_fee`
- `/finance/get-fee/` → `get_fee_amount` (API endpoint)
- `/add_expense/` → `add_expense`

**Academic:**
- `/add_marks/` → `add_marks`
- `/report_card/` → `report_card`
- `/marksheet_pdf/<id>/` → `marksheet_pdf`

**HR:**
- `/hr/staff/` → `staff_list`
- `/hr/staff/add/` → `add_staff`
- `/hr/salary/pay/` → `pay_salary`
- `/hr/salary/slip/<id>/` → `salary_slip_pdf`

**Transport:**
- `/transport/` → `transport_home`
- `/transport/add-route/` → `add_route`
- `/transport/assign/` → `transport_assign`

**Notices:**
- `/add_notice/` → `add_notice`
- `/delete_notice/<id>/` → `delete_notice`

**Utilities:**
- `/finance/generate-invoices/` → `generate_monthly_dues`
- `/debug-test/` → `debug_test`

**Authentication:**
- `/accounts/login/` → Django LoginView
- `/logout/` → Django LogoutView

**Issues:**
- ⚠️ Duplicate route: `/library/` appears twice (lines 28, 37)
- ⚠️ Commented route: `/digital-library/` (line 36)
- ⚠️ Inconsistent naming: mix of kebab-case and snake_case

---

## 4. VIEWS → MODELS → TEMPLATES MAPPING

### Dashboard Module (`views/dashboard.py`)
- **View:** `index` → **Model:** `Member`, `FeeTransaction`, `StudentTransport`, `LibraryTransaction`, `Staff`, `Notice`
- **Template:** `index.html`
- **View:** `add_notice` → **Model:** `Notice`
- **View:** `delete_notice` → **Model:** `Notice`
- **View:** `debug_test` → No model (test endpoint)

### Students Module (`views/students.py`)
- **View:** `all_students` → **Model:** `Member`, `ClassRoom`, `School`
- **Template:** `all_students.html`
- **View:** `student_profile` → **Model:** `Member`, `ExamScore`, `Attendance`
- **Template:** `student_profile.html`
- **View:** `update` → **Model:** `Member`
- **Template:** `update.html`

**⚠️ BUG:** `student_profile` view references `ExamScore` and `Attendance` without imports (lines 20-21)

### Academic Module (`views/academic.py`)
- **View:** `attendance` → **Model:** `Member`, `Attendance`, `ClassRoom`
- **Template:** `attendance.html`
- **View:** `attendance_records` → **Model:** `Attendance`
- **Template:** `attendance_records.html`
- **View:** `report_card` → **Model:** `ExamScore`
- **Template:** `report_card.html`
- **View:** `add_marks` → **Model:** `ExamScore`, `Member`
- **Template:** `add_marks.html`
- **View:** `marksheet_pdf` → **Model:** `ExamScore`
- **Template:** `marksheet_pdf.html` (PDF generation)

### Finance Module (`views/finance.py`)
- **View:** `fee_home` → **Model:** `FeeTransaction`, `Member`, `ClassRoom`
- **Template:** `fees.html`
- **View:** `collect_fee` → **Model:** `FeeTransaction`, `Member` (via `FinanceService`)
- **View:** `fee_config` → **Model:** `FeeStructure`, `ClassRoom`
- **View:** `generate_monthly_dues` → **Model:** `Member`, `FeeStructure`
- **View:** `receipt_pdf` → **Model:** `FeeTransaction`
- **Template:** `receipt_pdf.html`
- **View:** `delete_fee` → **Model:** `FeeTransaction`, `Member`
- **View:** `get_fee_amount` → **Model:** None (API endpoint, returns empty JSON)
- **View:** `add_expense` → **Model:** `Expense`
- **Template:** `add_expense.html`

**⚠️ BUG:** `get_fee_amount` always returns `{'amount': 0}` (line 87)

### Library Module (`views/library.py`)
- **View:** `library` → **Model:** `Book`, `LibraryTransaction`, `Member`
- **Template:** `library.html`
- **View:** `add_book` → **Model:** `Book`
- **View:** `issue_book` → **Model:** `Book`, `LibraryTransaction`, `Member` (via `LibraryService`)
- **View:** `return_book` → **Model:** `LibraryTransaction` (via `LibraryService`)
- **View:** `delete_book` → **Model:** `Book`, `LibraryTransaction`
- **View:** `export_library_history` → **Model:** `LibraryTransaction` (Excel export)
- **View:** `digital_library` → **Model:** `StudyMaterial`
- **Template:** `library.html` (shared template)

### HR Module (`views/hr.py`)
- **View:** `staff_list` → **Model:** `Staff`, `SalaryTransaction`
- **Template:** `hr_staff.html`
- **View:** `add_staff` → **Model:** `Staff`
- **View:** `pay_salary` → **Model:** `SalaryTransaction`, `Staff`
- **View:** `salary_slip_pdf` → **Model:** `SalaryTransaction`
- **Template:** `salary_slip_pdf.html`

### Transport Module (`views/transport.py`)
- **View:** `transport_home` → **Model:** `TransportRoute`, `StudentTransport`, `Member`
- **Template:** `transport.html`
- **View:** `add_route` → **Model:** `TransportRoute`
- **View:** `transport_assign` → **Model:** `StudentTransport`, `Member`, `TransportRoute`

---

## 5. MODEL DEFINITIONS + RELATIONSHIPS

### Core Models

**School** (Multi-tenancy support)
- Fields: `name`, `address`, `school_code` (unique), `created_at`
- Relationships: Referenced by most models via FK

**UserProfile** (User extension)
- Fields: `user` (OneToOne → User), `school` (FK → School), `role`
- Signals: Auto-created on User creation (post_save)

**ClassRoom**
- Fields: `name`, `section`, `school` (FK → School, nullable)
- Unique: `(name, section)`

**AcademicYear**
- Fields: `name`, `start_date`, `end_date`, `is_active`, `school` (FK → School, nullable)

### Student Models

**Member** (Main student model)
- Fields: 20+ fields including personal info, academic, medical, transport
- Relationships:
  - `school` → FK(School, CASCADE, nullable)
  - `student_class` → FK(ClassRoom, SET_NULL, nullable)
- Legacy fields: `fee_total`, `fee_paid` (still in use)

### Library Models

**Book**
- Fields: `title`, `author`, `isbn`, `category`, `total_copies`, `available_copies`
- Relationships: `school` → FK(School, CASCADE, nullable)

**LibraryTransaction**
- Fields: `issue_date`, `due_date`, `return_date`, `fine_amount`, `status`
- Relationships:
  - `school` → FK(School, CASCADE, nullable)
  - `student` → FK(Member, CASCADE)
  - `book` → FK(Book, CASCADE)

### Finance Models

**FeeStructure**
- Fields: `title`, `amount`, `due_date`
- Relationships:
  - `school` → FK(School, CASCADE, nullable)
  - `class_room` → FK(ClassRoom, CASCADE)

**FeeTransaction** ⚠️ **CRITICAL BUG: DUPLICATE MODEL DEFINITION**
- **First definition (line 213):**
  - Fields: `amount_paid`, `payment_date`, `payment_mode`, `remarks`, `receipt_number` (unique, auto-generated)
  - Relationships: `school` → FK(School), `student` → FK(Member)
  - Custom save(): Auto-generates receipt_number, syncs with Member.fee_paid
- **Second definition (line 261):**
  - Fields: `amount_paid`, `month_year`, `payment_date`, `payment_mode`, `status`
  - Relationships: `student` → FK(Member)
  - **This will cause migration errors!**

### HR Models

**Staff**
- Fields: `first_name`, `last_name`, `email`, `phone`, `designation`, `salary`, `join_date`, `is_active`
- Relationships: `school` → FK(School, CASCADE, nullable)

**SalaryTransaction**
- Fields: `amount_paid`, `payment_date`, `month_year`, `payment_mode`, `remarks`
- Relationships:
  - `school` → FK(School, CASCADE, nullable)
  - `staff` → FK(Staff, CASCADE)

### Transport Models

**TransportRoute**
- Fields: `route_name`, `vehicle_number`, `driver_name`, `driver_phone`
- Relationships: `school` → FK(School, CASCADE)

**StudentTransport**
- Fields: `pickup_point`, `monthly_fee`
- Relationships:
  - `school` → FK(School, CASCADE)
  - `student` → OneToOne(Member, CASCADE)
  - `route` → FK(TransportRoute, CASCADE)

### Academic Models

**ExamScore**
- Fields: `exam_name`, `maths`, `physics`, `chemistry`, `english`, `computer`, `generated_report` (FileField)
- Relationships: `student` → FK(Member, CASCADE)

**Attendance**
- Fields: `date`, `status`
- Relationships: `student` → FK(Member, CASCADE)
- ⚠️ Missing: Unique constraint on `(student, date)` - allows duplicate entries

### Other Models

**Notice**
- Fields: `title`, `message`, `created_at`
- No relationships

**Expense**
- Fields: `description`, `amount`, `date`
- No relationships

**StudyMaterial**
- Fields: `title`, `subject`, `class_name`, `pdf_file`, `video_link`
- No relationships

**Payment** (Legacy, unused)
- Fields: `amount`, `date`
- Relationships: `student` → FK(Member, CASCADE)

### Relationship Summary
- **Foreign Keys:** 15+ FK relationships
- **OneToOne:** 2 (UserProfile→User, StudentTransport→Member)
- **Many-to-Many:** 0
- **Cascade Deletes:** Most use CASCADE, some use SET_NULL

---

## 6. FORMS + SERIALIZERS

### Forms (`forms.py`)
**MemberForm** (ModelForm)
- Model: `Member`
- Fields: `__all__` (all fields)
- Widgets: Custom Bootstrap classes for `firstname`, `lastname`, `profile_pic`
- ⚠️ Issues:
  - No field validation
  - No custom clean methods
  - Missing: Forms for FeeTransaction, Staff, Book, etc.

### Serializers (`serializers.py`)
**StudentSerializer** (ModelSerializer)
- Model: `Member`
- Fields: `__all__`
- ⚠️ Issues:
  - No nested serialization for related objects
  - Missing: Serializers for other models
  - Not used in any API views (DRF configured but no API endpoints)

---

## 7. BUSINESS LOGIC FLOWS

### Fee Collection Flow
1. User navigates to `/finance/collect/`
2. POST request with `student_id`, `amount`, `mode`, `date`
3. `FinanceService.collect_fee()` called:
   - Atomic transaction starts
   - Student row locked (`select_for_update()`)
   - `FeeTransaction` created
   - `Member.fee_paid` updated using `F()` expression (prevents race conditions)
   - Student refreshed from DB
4. Redirect to `fee_home`

**Strengths:**
- ✅ Atomic transactions prevent data corruption
- ✅ Row-level locking prevents race conditions
- ✅ F() expressions for safe concurrent updates

**Issues:**
- ⚠️ No validation of amount (could be negative)
- ⚠️ No check if student exists before processing
- ⚠️ Hardcoded `month_year="Current"` in service

### Library Book Issue Flow
1. User navigates to `/library/issue_book/`
2. POST request with `student_id`, `book_id`, `due_date`
3. `LibraryService.issue_book()` called:
   - Atomic transaction starts
   - Book row locked (`select_for_update()`)
   - Availability checked
   - `LibraryTransaction` created
   - `Book.available_copies` decremented using `F()` expression
4. Redirect to `/library/`

**Strengths:**
- ✅ Prevents negative inventory
- ✅ Atomic operations
- ✅ Proper error handling (ValueError for out of stock)

**Issues:**
- ⚠️ No validation of due_date format
- ⚠️ No check if student already has too many books issued

### Attendance Marking Flow
1. User navigates to `/attendance/`
2. GET: Select class and date, display students
3. POST: Submit attendance for multiple students
4. `update_or_create()` used to prevent duplicates
5. Redirect with query params

**Strengths:**
- ✅ Input sanitization (handles None, 'null', empty strings)
- ✅ Uses `update_or_create()` to prevent duplicates

**Issues:**
- ⚠️ No unique constraint on model (allows duplicates if race condition)
- ⚠️ No validation of date (could be future date)

### Marksheet PDF Generation Flow
1. User requests `/marksheet_pdf/<id>/`
2. Check if `ExamScore.generated_report` exists
3. If exists: Redirect to file URL
4. If not: Trigger Celery task `generate_marksheet_pdf_task.delay(id)`
5. User sees "Please wait and refresh" message
6. Task generates PDF, saves to `ExamScore.generated_report`
7. User refreshes, gets PDF

**Strengths:**
- ✅ Background processing prevents timeout
- ✅ File caching (generated once, reused)

**Issues:**
- ⚠️ No task status tracking
- ⚠️ No error notification if task fails
- ⚠️ User must manually refresh (no polling)

---

## 8. AUTHENTICATION / PERMISSIONS LOGIC

### Authentication
- **Method:** Django's built-in authentication
- **Login URL:** `/accounts/login/`
- **Logout URL:** `/logout/`
- **Redirects:**
  - `LOGIN_REDIRECT_URL = 'index'`
  - `LOGOUT_REDIRECT_URL = 'login'`

### View Protection
- **Decorator:** `@login_required` on all views
- **Custom Decorator:** `allowed_users(allowed_roles=[])` in `decorators.py`
  - Checks user groups or superuser status
  - Returns `HttpResponseForbidden` if unauthorized
  - ⚠️ **Not used anywhere** - all views use `@login_required` only

### Permission Checks
- **Superuser Checks:**
  - `delete_fee` (line 80): Only superuser can delete fees
  - `library` view (commented): Superuser sees all books
- **School-based Filtering:**
  - `get_current_school(request)` utility function
  - Superuser → First school
  - Staff → Their assigned school (via UserProfile)
  - ⚠️ **Inconsistent:** Some views filter by school, others don't

### REST Framework Permissions
- **Global Setting:** `IsAuthenticated` (DRF config)
- ⚠️ **No API endpoints** using DRF (serializers exist but unused)

### Issues
- ⚠️ No role-based access control (RBAC) implementation
- ⚠️ `allowed_users` decorator defined but never used
- ⚠️ Inconsistent school filtering across views
- ⚠️ No permission checks for sensitive operations (delete, modify)
- ⚠️ CORS_ALLOW_ALL_ORIGINS = True (security risk)

---

## 9. DATA STORAGE (MEDIA + STATIC + USER UPLOADS)

### Static Files
- **STATIC_URL:** `/static/`
- **STATICFILES_DIRS:** `BASE_DIR / "static"`
- **STATIC_ROOT:** `staticfiles/` (for collectstatic)
- **Location:** `/mysite/static/` and `/mysite/members/static/`
- **Contents:** CSS, JS, images, vendor libraries (Chart.js, Bootstrap, etc.)

### Media Files
- **MEDIA_URL:** `/media/`
- **MEDIA_ROOT:** `media/` (project root)
- **Upload Paths:**
  - Student images: `student_images/`
  - Study materials: `materials/`
  - Generated reports: `reports/`

### File Handling
- **Library:** `django.core.files.storage.FileSystemStorage`
- **PDF Generation:** xhtml2pdf (in-memory, then saved)
- **Excel Export:** xlwt (in-memory, HttpResponse)

### Issues
- ⚠️ No file size validation
- ⚠️ No file type validation (images could be any format)
- ⚠️ No cleanup of orphaned files
- ⚠️ Media files served in DEBUG mode only (production needs web server config)

---

## 10. SIGNALS / TASKS / CRON JOBS

### Signals (`models.py`)
**User Profile Auto-Creation:**
- `@receiver(post_save, sender=User)` - Two receivers (lines 84, 90)
- **First receiver:** Creates UserProfile on User creation
- **Second receiver:** Saves UserProfile (redundant, could cause issues)
- ⚠️ **Issue:** Two receivers on same signal could cause duplicate profiles

### Celery Tasks (`tasks.py`)
**generate_marksheet_pdf_task:**
- **Type:** `@shared_task`
- **Purpose:** Generate PDF marksheet in background
- **Process:**
  1. Fetch ExamScore
  2. Calculate totals and percentage
  3. Render HTML template
  4. Generate PDF using xhtml2pdf
  5. Save to `ExamScore.generated_report` FileField
- **Error Handling:** Try/except for DoesNotExist

**Celery Configuration (`mysite/celery.py`):**
- App name: `mysite`
- Auto-discovers tasks from all apps
- Uses Django settings

### Cron Jobs
- ❌ **None configured**

### Issues
- ⚠️ Duplicate signal receivers could cause problems
- ⚠️ No task retry logic
- ⚠️ No task status tracking
- ⚠️ No scheduled tasks (no monthly fee generation, etc.)

---

## 11. EXTERNAL DEPENDENCIES (API CALLS, LIBRARIES)

### Third-Party Libraries

**Core Framework:**
- `Django==4.2.27`
- `djangorestframework==3.16.1`
- `django-cors-headers==4.9.0`
- `django-pwa==2.0.1`

**Task Queue:**
- `celery==5.3.6`
- `redis==5.0.1`

**PDF Generation:**
- `xhtml2pdf==0.2.17`
- `reportlab==4.4.7`
- `pypdf==6.5.0`
- `pyHanko==0.32.0` (PDF signing)

**Excel/Data:**
- `openpyxl==3.1.5`
- `xlwt==1.3.0`

**Image Processing:**
- `pillow==11.3.0`

**Payment (unused?):**
- `razorpay==2.0.0`

**Utilities:**
- `arabic-reshaper==3.0.0`
- `python-bidi==0.6.7`

### External API Calls
- ❌ **None found** - No external API integrations

### Issues
- ⚠️ `razorpay` installed but not used in codebase
- ⚠️ `pyHanko` installed but not used (PDF signing not implemented)
- ⚠️ `arabic-reshaper` and `python-bidi` installed but not used
- ⚠️ Many unused dependencies increase deployment size

---

## 12. KNOWN ISSUES / POTENTIAL BUGS

### 🔴 CRITICAL ISSUES

1. **Duplicate FeeTransaction Model Definition**
   - **Location:** `models.py` lines 213 and 261
   - **Impact:** Will cause migration errors, database schema conflicts
   - **Fix:** Remove duplicate definition, consolidate fields

2. **Hardcoded SECRET_KEY in Production Settings**
   - **Location:** `mysite/settings.py` line 16
   - **Impact:** Security vulnerability if code is exposed
   - **Fix:** Use environment variables (`.env` file exists but not used in main settings)

3. **DEBUG = True in Production**
   - **Location:** `mysite/settings.py` line 19
   - **Impact:** Exposes sensitive error information
   - **Fix:** Set `DEBUG = False` and use environment variable

4. **CORS_ALLOW_ALL_ORIGINS = True**
   - **Location:** `mysite/settings.py` line 152
   - **Impact:** Allows any origin to access API (security risk)
   - **Fix:** Whitelist specific origins

5. **Missing Imports in student_profile View**
   - **Location:** `views/students.py` lines 20-21
   - **Impact:** `NameError` when accessing student profile
   - **Fix:** Add `from ..models import ExamScore, Attendance`

### 🟡 HIGH PRIORITY ISSUES

6. **Duplicate Signal Receivers**
   - **Location:** `models.py` lines 84, 90
   - **Impact:** Could create duplicate UserProfile records
   - **Fix:** Remove redundant receiver or add existence check

7. **No Unique Constraint on Attendance**
   - **Location:** `models.py` Attendance model
   - **Impact:** Allows duplicate attendance records for same student/date
   - **Fix:** Add `unique_together = ('student', 'date')` or use `UniqueConstraint`

8. **Inconsistent School Filtering**
   - **Location:** Multiple views
   - **Impact:** Data leakage between schools in multi-tenant setup
   - **Fix:** Ensure all queries filter by `get_current_school(request)`

9. **No Input Validation in Views**
   - **Location:** Most POST handlers
   - **Impact:** Invalid data can be saved, potential SQL injection (though Django ORM protects)
   - **Fix:** Use Django forms or add validation

10. **get_fee_amount Always Returns 0**
    - **Location:** `views/finance.py` line 87
    - **Impact:** Fee calculation API doesn't work
    - **Fix:** Implement actual fee calculation logic

### 🟢 MEDIUM PRIORITY ISSUES

11. **No Error Handling in Many Views**
    - **Location:** Multiple views
    - **Impact:** Unhandled exceptions show 500 errors
    - **Fix:** Add try/except blocks, return user-friendly errors

12. **Library View Shows All Books (Debug Code)**
    - **Location:** `views/library.py` line 16
    - **Impact:** School filtering disabled (commented out)
    - **Fix:** Re-enable school filtering

13. **No File Validation**
    - **Location:** File upload views
    - **Impact:** Large files, wrong file types can be uploaded
    - **Fix:** Add file size/type validation

14. **Unused Decorator**
    - **Location:** `decorators.py`
    - **Impact:** Code clutter, unused functionality
    - **Fix:** Either use it or remove it

15. **Duplicate URL Route**
    - **Location:** `urls.py` lines 28, 37
    - **Impact:** Second route overwrites first
    - **Fix:** Remove duplicate or rename

16. **No Tests**
    - **Location:** `tests.py` (empty)
    - **Impact:** No regression testing, risky refactoring
    - **Fix:** Add unit tests for models, views, services

17. **F() Expression Issue in Library Service**
    - **Location:** `services/library.py` line 38
    - **Impact:** `F()` expression assigned but not used correctly
    - **Fix:** Use `update()` or `refresh_from_db()` after save

18. **Missing Date Field in ExamScore**
    - **Location:** `models.py` ExamScore model
    - **Impact:** Can't filter/sort exams by date
    - **Fix:** Add `date` field

19. **No Pagination**
    - **Location:** List views (all_students, fee_home, etc.)
    - **Impact:** Performance issues with large datasets
    - **Fix:** Add Django pagination

20. **Hardcoded Values**
    - **Location:** Multiple places (fine calculation: 10 Rs/day, due days: 14)
    - **Impact:** Not configurable
    - **Fix:** Move to settings or database config

---

## 13. DEBUG TIPS

### Development Setup
1. **Enable Debug Toolbar:**
   - Already configured in `mysite/urls.py`
   - Access at `/__debug__/`
   - Shows SQL queries, templates, signals

2. **Check Logs:**
   - Django logs to console in DEBUG mode
   - Check for `NameError`, `AttributeError` in views

3. **Database Inspection:**
   - Use Django admin at `/admin/`
   - Or use `python manage.py shell` for direct DB access

### Common Issues & Solutions

**Issue: "NameError: name 'ExamScore' is not defined"**
- **Solution:** Add import in `views/students.py`: `from ..models import ExamScore, Attendance`

**Issue: "Migration conflicts"**
- **Solution:** Check for duplicate model definitions, run `python manage.py makemigrations --dry-run`

**Issue: "CORS errors in production"**
- **Solution:** Update `CORS_ALLOWED_ORIGINS` with specific domains, remove `CORS_ALLOW_ALL_ORIGINS`

**Issue: "PDF generation timeout"**
- **Solution:** Ensure Celery worker is running, check Redis connection

**Issue: "Static files not loading"**
- **Solution:** Run `python manage.py collectstatic`, check `STATIC_ROOT` in production

**Issue: "School filtering not working"**
- **Solution:** Check `get_current_school()` returns correct school, verify UserProfile exists

### Performance Debugging
1. **Use Debug Toolbar** to identify N+1 queries
2. **Check `select_related()` usage** - already implemented in some views
3. **Monitor database queries** - use `connection.queries` in DEBUG mode
4. **Check Celery task status** - use Flower or check Redis

### Testing Checklist
- [ ] Test fee collection with concurrent requests
- [ ] Test library book issue when stock is 0
- [ ] Test attendance marking for same student/date twice
- [ ] Test PDF generation with missing data
- [ ] Test school filtering with multiple schools
- [ ] Test file uploads with large files
- [ ] Test authentication with different user roles

---

## SUMMARY

### Strengths
✅ Service layer pattern for critical operations  
✅ Atomic transactions prevent race conditions  
✅ Good use of `select_related()` for query optimization  
✅ Modular view organization  
✅ PWA support for mobile  
✅ Background task processing for PDFs  

### Weaknesses
❌ Security vulnerabilities (DEBUG=True, CORS, SECRET_KEY)  
❌ Duplicate model definitions  
❌ Missing error handling  
❌ No input validation  
❌ Inconsistent school filtering  
❌ No tests  
❌ Unused dependencies  

### Recommendations
1. **Immediate:** Fix duplicate FeeTransaction model, add missing imports
2. **Security:** Move SECRET_KEY to env, disable DEBUG, restrict CORS
3. **Code Quality:** Add form validation, error handling, tests
4. **Performance:** Add pagination, optimize queries, remove unused dependencies
5. **Features:** Implement RBAC, add file validation, improve PDF task status

---

**End of Audit Report**
