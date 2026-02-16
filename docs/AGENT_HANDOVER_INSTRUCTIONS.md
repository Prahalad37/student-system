# Agent Handover Instructions (Antigravity Agent)

This document is for the **antigravity agent** (or any follow-up agent) taking over work on the School ERP Django project. It describes the current state, how to run the app, important gotchas, and where key code lives.

---

## 1. Project Overview

- **Project:** School ERP (multi-tenant) – Django app with Volt Dashboard UI.
- **Root:** Run all commands from `mysite/` (where `manage.py` lives).
- **Settings:** `mysite/settings.py` (used via `DJANGO_SETTINGS_MODULE=mysite.settings`).
- **Main app:** `members/` – URLs, views, models, templates, static, middleware.

---

## 2. Current State (What’s Done)

- **Volt Dashboard UI** is integrated:
  - Base layout: `templates/layouts/base.html`.
  - Includes: `templates/includes/` (sidebar, nav, head, scripts, footer, theme-settings).
  - All member app templates extend `layouts/base.html` (not `master.html`).
- **Static files:** Volt assets are under `static/`: `static/assets/`, `static/css/volt.css`, `static/vendor/` (Bootstrap, SweetAlert2, Notyf, SimpleBar, etc.). Already committed and pushed.
- **Sidebar** uses `members` URL names and role flags: `is_owner`, `is_admin`, `is_student`, `is_parent`, etc. Role-based menu visibility is in place.
- **Public pages:** Landing (`/`), login (`/accounts/login/`), onboarding wizard (`/onboarding/`).
- **Feature set:** 16 modules (Students, Finance, Library, HR, Transport, Learning, Timetable, Admissions/Enquiries, Parent portal, Notifications, School settings, etc.). See `docs/MODULES_AND_FEATURES.md` and `docs/BETTER_SYSTEM_DESIGN.md`.

---

## 3. How to Run the Application

1. **From project root:**  
   `cd /Users/prahalad/django_projects/mysite`  
   (or your workspace path to `mysite`).

2. **Use a virtualenv** (recommended):  
   Activate it, then install deps if needed: `pip install -r requirements.txt` (or project’s dependency file).

3. **Database:**  
   Ensure DB is migrated: `python manage.py migrate`.

4. **Run server:**  
   `python manage.py runserver`  
   (or with explicit host/port if required).

---

## 4. CRITICAL: Static Files and DEBUG

- With **DEBUG=False**, Django’s `runserver` **does not serve static files**. All requests to `/static/...` (e.g. `volt.css`, `volt.js`, vendor assets) will return **404**.
- **Fix for local development:** Run with **DEBUG=True**:
  - Either: `DEBUG=True python manage.py runserver`
  - Or set `DEBUG=True` in `.env` or in `mysite/settings.py` for local dev only.
- **Production:** Use a real static file server (e.g. WhiteNoise, nginx, or your hosting’s static serving); do not rely on `runserver` for static in production.

---

## 5. Diagnostic Command (Static)

- **Command:** `python manage.py check_static`
- **Location:** `members/management/commands/check_static.py`
- **Behavior:** Runs only when **DEBUG is True**. Prints:
  - `BASE_DIR`, `STATICFILES_DIRS`
  - Result of `findstatic` for `assets/js/volt.js` and `css/volt.css`
  - On-disk paths for those files
- **Use case:** If Volt assets still 404, run with DEBUG=True and then run `check_static` to verify paths and collectstatic/configuration.

---

## 6. Key Paths (Quick Reference)

| What | Path |
|------|------|
| Project root | `mysite/` |
| Settings | `mysite/settings.py` |
| Main URLs | `members/urls.py` |
| Volt base layout | `templates/layouts/base.html` |
| Sidebar / includes | `templates/includes/sidebar.html`, `navigation.html`, etc. |
| App templates | `members/templates/` (extend `layouts/base.html`) |
| Static (Volt) | `static/assets/`, `static/css/volt.css`, `static/vendor/` |
| Docs | `docs/` (MODULES_AND_FEATURES.md, BETTER_SYSTEM_DESIGN.md, USER_AND_ONBOARDING_GUIDE.md) |

---

## 7. Suggested Next Steps (Optional)

- Run the app with **DEBUG=True** and confirm Volt CSS/JS and vendor assets load (no 404s).
- Use **TEST_ALL_FEATURES_PROMPT.md** (in `docs/`) to run through login, dashboard, sidebar, roles, and critical flows.
- If you add new static files, ensure they’re under `STATICFILES_DIRS` or app `static/` and run `collectstatic` for production.

---

## 8. Handover Summary

- **You are taking over:** A working Volt UI integration and a full School ERP feature set. The main known issue was static 404s when DEBUG=False; fix is to use DEBUG=True locally.
- **You have:** Handover instructions (this file), a feature-testing prompt (`TEST_ALL_FEATURES_PROMPT.md`), and module/design docs in `docs/`.
- **When in doubt:** Check `members/urls.py` for routes, `templates/includes/sidebar.html` for menu structure, and `docs/MODULES_AND_FEATURES.md` for role–module mapping.
