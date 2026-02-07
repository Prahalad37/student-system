# 🎯 Django ERP Testing Guide

## 🔑 Login Credentials

### Superuser Account
Create your superuser with:
```bash
source ../myenv/bin/activate
python manage.py createsuperuser
```

**Recommended Credentials:**
- Username: `admin`
- Email: `admin@prahlad.edu`
- Password: `admin123` (change for production!)

---

## 📊 Test Data Summary

The system now has:
- ✅ **3 Schools** (Prah lad Academy + 2 test schools)
- ✅ **52 Students** across 9 classes (Class 6-12)
- ✅ **8 Staff Members** (Teachers, Admin, Librarian)
- ✅ **58 Library Books** (NCERT textbooks, fiction, biography)
- ✅ **3 Transport Routes** with vehicles and drivers
- ✅  **91 Fee Transactions** (January, February, March 2026)
- ✅ **451 Attendance Records** (last 15 days for 30 students)
- ✅ **51 Exam Scores** (Unit Tests, Mid-Terms, Finals)
- ✅ **4 Notices** (Fee reminders, events)

---

## 🧪 Feature Testing Checklist

### 1. ✅ Dashboard (`/`)
- [ ] View total students count
- [ ] Check fee collection summary
- [ ] See latest notices
- [ ] View recent activities

### 2. 👥 Student Management (`/students/all/`)
- [ ] View all students list
- [ ] Search/filter by class
- [ ] Click on a student to view profile
- [ ] Check student details (name, class, roll number, photo)
- [ ] View attendance percentage
- [ ] Check fee status (total, paid, due)
- [ ] See exam scores
- [ ] Edit student information
- [ ] Add new student (`/add/`)
- [ ] Upload profile picture

### 3. 📝 Attendance (`/attendance/`)
- [ ] Select class from dropdown
- [ ] Choose date
- [ ] Mark Present/Absent for multiple students
- [ ] Submit attendance
- [ ] View attendance records (`/attendance_records/`)
- [ ] Filter by class and date range
- [ ] Verify no duplicate entries possible (same student, same date)

### 4. 💰 Fee Management (`/finance/`)
- [ ] View fee collection dashboard
- [ ] See pending fees list
- [ ] Collect fee from student
  - [ ] Select student
  - [ ] Enter amount
  - [ ] Choose payment mode (Cash/UPI/Bank Transfer/Cheque)
  - [ ] Submit
- [ ] Generate PDF receipt (`/finance/receipt/<id>/`)
- [ ] Download receipt
- [ ] Check receipt has unique code (REC-YYYYMMDD-ID)
- [ ] View fee history by student
- [ ] Add expense (`/add_expense/`)
- [ ] Configure fee structure (`/finance/config/`)

### 5. 📚 Library Management (`/library/`)
- [ ] View all books with availability
- [ ] See total books count
- [ ] Check issued books count
- [ ] Add new book
  - [ ] Enter title, author, ISBN, category
  - [ ] Set number of copies
- [ ] Issue book to student
  - [ ] Select student
  - [ ] Select book
  - [ ] Set due date (typically 14 days)
  - [ ] Verify available copies decrease
- [ ] Return book
  - [ ] Click return on issued book
  - [ ] Check if fine calculated for overdue
  - [ ] Verify available copies increase
- [ ] Delete book (only if not issued)
- [ ] Export library history to Excel

### 6. 📊 Academic/Exams (`/add_marks/`)
- [ ] Add exam marks for student
  - [ ] Select student
  - [ ] Enter exam name
  - [ ] Enter subject marks (Maths, Physics, Chemistry, English, Computer)
  - [ ] Submit
- [ ] View report card (`/report_card/`)
- [ ] Generate marksheet PDF (`/marksheet_pdf/<id>/`)
- [ ] Download marksheet
- [ ] Verify total and percentage calculated automatically

### 7. 👔 HR & Payroll (`/hr/staff/`)
- [ ] View all staff list
- [ ] See salary details
- [ ] Add new staff member
  - [ ] Enter name, email, phone
  - [ ] Set designation, salary
  - [ ] Set join date
- [ ] Pay salary
  - [ ] Select staff
  - [ ] Enter month/year
  - [ ] Choose amount and payment mode
  - [ ] Submit
- [ ] Generate salary slip PDF (`/hr/salary/slip/<id>/`)
- [ ] Download salary slip

### 8. 🚌 Transport Management (`/transport/`)
- [ ] View all transport routes
- [ ] See assigned students count
- [ ] Add new transport route
  - [ ] Enter route name
  - [ ] Add vehicle number
  - [ ] Set driver name and phone
- [ ] Assign student to route
  - [ ] Select student
  - [ ] Choose route
  - [ ] Set pickup point
  - [ ] Enter monthly fee
- [ ] View transport fee collection

### 9. 📢 Notices
- [ ] View all notices on dashboard
- [ ] Add new notice (`/add_notice/`)
  - [ ] Enter title
  - [ ] Write message
  - [ ] Post
- [ ] Delete notice (superuser only)

### 10. 🔧 Admin Panel (`/admin/`)
- [ ] Login to Django admin
- [ ] Browse all models
- [ ] Check data integrity
- [ ] Create/edit records directly

---

## 🐛 Known Limitations (For Testing Awareness)

### Currently Working:
- ✅ Core CRUD operations for all modules
- ✅ PDF generation (receipts, marksheets, salary slips)
- ✅ Excel export (library history)
- ✅ File uploads (student photos, study materials)
- ✅ Multi-tenant (multiple schools)
- ✅ Atomic transactions (fee collection, library)
- ✅ Unique constraints (attendance)

### Not Yet Implemented:
- ❌ WhatsApp notifications
- ❌ Email notifications
- ❌ Online payment gateway (Razorpay installed but not integrated)
- ❌ Parent portal/login
- ❌ Student login panel
- ❌ Digital library frontend (backend exists)
- ❌ Bulk CSV import/export
- ❌ Advanced analytics dashboards
- ❌ Automated fee reminders
- ❌ ID card generation
- ❌ Certificate printing (TC, Bonafide)

---

## 🎨 UI/UX Notes

**Current Template:** SB Admin 2 (Bootstrap-based)
- Professional but dated design
- Good for admin panels
- Mobile responsive
- Chart.js integration

**Recommended Improvements:**
- Modern UI with Tailwind CSS or Material Design
- Dark mode toggle
- Better data visualization
- Improved mobile experience

---

## 🚀 Quick Start Commands

```bash
# Activate virtual environment
source ../myenv/bin/activate

# Run development server
python manage.py runserver

# Access in browser
open http://127.0.0.1:8000/

# Create superuser (if not exists)
python manage.py createsuperuser

# Regenerate test data (optional)
python manage.py create_test_data

# Collect static files (for production)
python manage.py collectstatic
```

---

## 📝 Test Scenarios

### Scenario 1: New Student Enrollment
1. Go to `/add/`
2. Fill all student details
3. Upload photo
4. Set class and roll number
5. Save
6. Verify student appears in `/students/all/`

### Scenario 2: Monthly Fee Collection
1. Go to `/finance/`
2. Find student with pending fee
3. Click "Collect Fee"
4. Enter amount, select UPI
5. Generate receipt
6. Verify student's `fee_paid` updated
7. Check `fee_due` decreased

### Scenario 3: Library Book Issue-Return Flow
1. Add a new book with 5 copies
2. Issue to Student A → Available: 4
3. Issue to Student B → Available: 3
4. Return from Student A → Available: 4
5. Issue to Student C with past due date
6. Return from Student C → Check fine calculated

### Scenario 4: Attendance Marking
1. Go to `/attendance/`
2. Select "Class 10 - A"
3. Choose today's date
4. Mark 5 present, 2 absent
5. Submit
6. Try marking same students again for same date → Should prevent duplicates

### Scenario 5: Exam Report Generation
1. Add marks for "Final Exam" for Student A
2. Navigate to `/report_card/`
3. Select student
4. Generate PDF marksheet
5. First time: Shows "Generating..." (Celery task)
6. Refresh after few seconds
7. PDF should download

---

## ⚠️ Security Checklist (Before Production)

- [ ] Change DEBUG = False in settings.py
- [ ] Update SECRET_KEY to random value
- [ ] Restrict CORS_ALLOWED_ORIGINS
- [ ] Set SECURE_HSTS_SECONDS
- [ ] Enable SESSION_COOKIE_SECURE
- [ ] Enable CSRF_COOKIE_SECURE
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper logging
- [ ] Configure email backend
- [ ] Add rate limiting
- [ ] Enable SSL/HTTPS

---

## 📞 Support Info

**System Status:** ✅ Ready for Testing  
**Database:** SQLite (development)  
**Python Version:** 3.9  
**Django Version:** 4.2.27  

**Need Help?**
- Check Django debug toolbar at `/__debug__/`
- View server logs in terminal
- Check `PROJECT_AUDIT.md` for detailed code analysis
- Review `ROADMAP.md` for planned features

---

**Happy Testing! 🎉**
