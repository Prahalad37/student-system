# Modules and Features

This document lists all functional modules in the School ERP and their features.

**Total: 16 modules** (15 for school users + 1 Superuser-only).

---

## 1. Auth

- Login, logout
- User profile view and edit
- Password change
- Role-based access: OWNER, ADMIN, ACCOUNTANT, TEACHER, STAFF, STUDENT, PARENT

---

## 2. Onboarding

- Public 3-step wizard (no login required):
  - **Step 1:** School details (name, address, school code, slug)
  - **Step 2:** Owner account (username, email, password)
  - **Step 3:** Review and create
- Creates one School and first Owner (User + UserProfile)

---

## 3. Students

- List all students (paginated)
- Add new admission
- Edit student
- Delete student
- View student profile (detailed)
- Export students as CSV
- Import students from CSV or Excel (bulk)
- Admission receipt PDF
- ID card (PDF)
- Create student login (username + temp password)
- Check admission number (duplicate check, e.g. for forms)

---

## 4. Academic – Attendance

- Mark attendance (by class/section and date)
- View attendance records

---

## 5. Academic – Exams & Reports

- Add marks (exam scores) with configurable subjects and exam types
- Subject and Exam type management (list, add, edit)
- Report card view (filter by class etc.) with dynamic subject columns
- Marksheet PDF download

---

## 6. Learning

- Learning hub: upload, view, delete study materials
- Student portal: student-specific view (materials, links)

---

## 7. Finance

- Fee home/dashboard
- Collect fee (record payment)
- Fee config (fee structure)
- View receipts, delete transaction
- Student receipt PDF
- Add expense
- Generate monthly dues (invoices)
- **Finance v2:** Installments view, Fee discounts & concessions, Late fee policy, Receipts list, Refund requests (initiate and approve/reject)

---

## 8. Library

- Add new book (title, author, ISBN, copies)
- Issue book to student (with due date)
- Return book
- View currently issued books
- Export library history (Excel)

---

## 9. Transport

- Add routes
- Assign students to routes
- Transport home (overview)

---

## 10. HR & Payroll

- Staff list
- Add staff
- Pay salary (record payment)
- Salary slip PDF

---

## 11. School admin

- School settings (edit name, address, code, etc.)
- Download JSON backup (OWNER only)
- Manage users: list, add, edit role/password/active, deactivate/activate; link PARENT to students (guardian_of) (OWNER/ADMIN)
- Academic years: list, add, edit (OWNER/ADMIN)
- Dismiss “getting started” banner

---

## 12. Timetable

- View timetable by class or by teacher (grid: days × slots)
- Edit timetable: add time slots, add/edit/delete entries (class, subject, teacher, day, slot)
- Conflict check: one entry per class per day per slot (OWNER/ADMIN edit)

---

## 13. Admissions / Enquiries (CRM)

- List enquiries with status filter (New, Contacted, Visited, Admitted, Lost)
- Add and edit enquiry; change status; convert to admission (redirect to New Admission)

---

## 14. Parent portal

- Role PARENT with guardian_of (M2M to students); link in School admin when role is PARENT
- Parent dashboard and student detail (attendance, fee, report cards, materials)
- Marksheet PDF restricted to linked students for PARENT

---

## 15. Notifications

- In-app notifications; navbar bell dropdown; mark read / mark all read
- Send notification to all staff & parents or to parents of a class

---

## 16. Superuser only

- List all schools (multi-tenant)
- Add new school (creates tenant)

---

## Seeding demo data

To populate **MDP Convent** with 100 students and sample data for all modules (fee, library, transport, attendance, exams, notices, HR, expense, study materials, enquiries, timetable, etc.), run: `python manage.py seed_mdp_convent`. To do the same for **Demo School**, run: `python manage.py seed_demo_school`.

---

## Quick reference (by role)

| Module        | Typical access (roles)        |
|---------------|-------------------------------|
| Auth          | All authenticated             |
| Onboarding    | Public                         |
| Students      | OWNER, ADMIN, ACCOUNTANT, TEACHER, STAFF |
| Enquiries     | OWNER, ADMIN, ACCOUNTANT, TEACHER, STAFF |
| Attendance    | OWNER, ADMIN, TEACHER, STAFF   |
| Exams/Reports | OWNER, ADMIN, TEACHER, STAFF   |
| Timetable     | OWNER, ADMIN, TEACHER, STAFF (view); OWNER, ADMIN (edit) |
| Learning      | OWNER, ADMIN, TEACHER, STAFF; STUDENT (portal) |
| Finance       | OWNER, ADMIN, ACCOUNTANT       |
| Library       | OWNER, ADMIN, TEACHER, STAFF   |
| Transport     | OWNER, ADMIN, STAFF            |
| HR            | OWNER, ADMIN                   |
| School admin  | OWNER, ADMIN (backup: OWNER only) |
| Parent portal | PARENT (linked students only) |
| Notifications | All (in-app); Send: OWNER, ADMIN, TEACHER |
| Superuser     | is_superuser only              |
