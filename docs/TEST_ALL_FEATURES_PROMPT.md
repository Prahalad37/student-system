# Test All Features – Prompt for QA / Agent

Use this as a **reusable prompt** for a human or an agent to verify all major features of the School ERP. Run the app with **DEBUG=True** from project root (`mysite/`) before testing so that Volt static files load.

---

## Copy-paste prompt (English)

**Task:** Test all major features of the School ERP app and report what works and what fails.

**Preconditions:**
- Run the server from project root: `cd mysite && DEBUG=True python manage.py runserver`.
- Use a browser (or automation). If no school exists, complete onboarding first at `/onboarding/`.

**Test in this order:**

1. **Public pages (no login)**
   - Landing: open `/` – page loads, no console errors, Volt styling applied (no 404s for `/static/...`).
   - Login: open `/accounts/login/` – form visible, can log in with valid credentials.
   - Onboarding: open `/onboarding/` – 3-step wizard (school details → owner account → review) completes and creates school + owner.

2. **After login (e.g. as Owner/Admin)**
   - Dashboard: open `/dashboard/` – Command Center loads, sidebar visible, no static 404s (check Network tab for `volt.css`, `volt.js`, vendor assets).
   - Sidebar: click each main section and confirm pages load:
     - **Students:** View All, New Admission, Enquiries.
     - **Attendance:** Mark/view attendance.
     - **Exams & Reports:** Report card, Add marks; Subjects and Exam types (if linked).
     - **Learning Hub:** Materials list/upload.
     - **Timetable:** View and (if role allows) Edit.
     - **Finance:** Fee home, Collect fee, Config, Receipts, Installments, Discounts, Concessions, Late fee policy, Refunds.
     - **Library:** Home, Add book, Issue/return.
     - **Transport:** Home, Add route, Assign.
     - **HR:** Staff list, Add staff, Pay salary.
     - **School:** Settings, Users, Academic years, Backup (Owner), Dismiss getting started.
   - **Notifications:** Navbar bell – list, mark read, mark all read; Send notification (if role allows).
   - **Profile:** Profile page and logout work.

3. **Role-based access**
   - As **PARENT:** Login → Parent dashboard and linked student detail (attendance, fee, report cards) – no staff-only menus.
   - As **STUDENT:** Login → Student portal (learning materials) – no staff menus.
   - As **ACCOUNTANT:** Finance and relevant menus visible; no HR or School admin if not allowed.
   - As **OWNER/ADMIN:** Full sidebar; backup and user management visible for OWNER.

4. **Critical actions (smoke)**
   - Add one student (New Admission), view list, open one profile.
   - Mark attendance for one class/date.
   - Add one fee payment (Collect fee), open a receipt PDF.
   - Add one book, issue to student, return.
   - Add one enquiry, change status, optionally convert to admission.
   - Open report card and (if data exists) marksheet PDF.
   - Send one in-app notification.

5. **Volt / static**
   - On dashboard and 2–3 inner pages: no 404s for `volt.css`, `volt.js`, or files under `/static/vendor/` or `/static/assets/`. Sidebar and top nav render with Volt styling.

**Report:** List each section (1–5) and note: OK / Failed. For failures, note URL, role, and short error description (e.g. “404 for volt.css”, “500 on finance/collect/”).

---

## Copy-paste prompt (Hindi/English – same checklist)

**Kaam:** School ERP app ke saare major features test karo aur batao kya kaam kar raha hai, kya fail ho raha hai.

**Pehle:**  
- Project root se server chalao: `cd mysite && DEBUG=True python manage.py runserver`.  
- Browser se test karo. Agar school nahi hai to pehle `/onboarding/` complete karo.

**Test is order mein karo:**

1. **Public pages (bina login)**  
   - Landing `/`, Login `/accounts/login/`, Onboarding `/onboarding/` – teeno load hon, styling theek ho, static 404 na aaye.

2. **Login ke baad (Owner/Admin)**  
   - Dashboard `/dashboard/` – sidebar dikhe, Volt CSS/JS 404 na ho.  
   - Sidebar se har section check karo: Students (View All, New Admission, Enquiries), Attendance, Exams & Reports, Learning Hub, Timetable, Finance (sari sub-pages), Library, Transport, HR, School (Settings, Users, Academic years, Backup), Notifications, Profile, Logout.

3. **Role-based**  
   - PARENT → Parent dashboard, linked student only.  
   - STUDENT → Student portal only.  
   - ACCOUNTANT → Finance dikhe, HR/School admin role ke hisaab se.  
   - OWNER/ADMIN → Full access.

4. **Critical actions**  
   - Ek student add karo, list dekho, profile kholo.  
   - Ek class/date ki attendance mark karo.  
   - Ek fee payment karo, receipt PDF kholo.  
   - Ek book add karo, issue/return karo.  
   - Ek enquiry add karo, status change karo.  
   - Report card / marksheet PDF kholo.  
   - Ek notification bhejo.

5. **Volt / static**  
   - Dashboard aur 2–3 pages par `/static/` ke liye 404 nahi aane chahiye; Volt styling sahi dikhni chahiye.

**Report:** Har section (1–5) ke liye likho: OK ya Failed. Fail ho to URL, role aur chota error description do.

---

## Quick checklist (one-liner reminder)

Public pages → Login → Dashboard & sidebar (all modules) → Role-based (Parent, Student, Accountant, Owner) → Smoke: student, attendance, fee, library, enquiry, report card, notification → Volt static no 404.
