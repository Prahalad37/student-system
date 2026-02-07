# Tenant-First Phase Report

## Files Changed

| Path | Changes |
|------|---------|
| `members/views/dashboard.py` | Index: marketing when `request.school` is None; dashboard only with tenant + auth; redirect to login when unauthenticated on tenant; added `FeeTransaction` and `recent_transactions` in context; removed TEMP no-op. |
| `members/views/auth.py` | Replaced `login_redirect` with `TenantLoginView`: dispatch redirects to index when no tenant; `form_valid` rejects login when `UserProfile.school` != `request.school` (unless superuser); uses `form.add_error` + `form_invalid` on mismatch. |
| `members/views/__init__.py` | Switched export from `login_redirect` to `TenantLoginView`. |
| `members/urls.py` | Removed `login` route (moved to main urls); removed unused `auth` import; kept `logout` with `next_page="/accounts/login/"`. |
| `mysite/urls.py` | Removed `login_redirect` route and import; added `path('accounts/login/', TenantLoginView.as_view(), name='login')` before `include('django.contrib.auth.urls')` so tenant login is used. |
| `members/templates/registration/login.html` | Error block now shows `form.non_field_errors` (with fallback “Invalid Username or Password”) so “You do not belong to this school.” displays. |
| `members/templates/members/dashboard.html` | `{{ tx.amount }}` → `{{ tx.amount_paid }}` for `FeeTransaction`. |

## What Was Broken Before

- Dashboard could render with `school is None` (TEMP no-op), exposing metrics without a tenant.
- Login was not tenant-aware: any valid user could log in on any subdomain.
- No check that `UserProfile.school` matched the request’s tenant; cross-tenant login was possible.
- Root (localhost) and tenant subdomains shared the same index behavior; root could effectively act like a dashboard.
- `login_redirect` and root login flow were redundant and confusing.
- Dashboard used `recent_transactions = []` and template expected `tx.amount`; `FeeTransaction` uses `amount_paid`.

## What Was Fixed

1. **Tenant rules**
   - `request.school` None → only marketing (and tenant-aware login redirect via redirect to index).
   - `request.school` set → dashboard only for authenticated users; otherwise redirect to tenant login.

2. **Root vs tenant**
   - `localhost:8000` → marketing only.
   - `prahlad.localhost:8000` → dashboard only (after login). No dashboard on root.

3. **Tenant-aware login**
   - Login auto-detects tenant from `request.school` (middleware sets it from host).
   - Login allowed only on tenant subdomain; on root, redirect to index (marketing).
   - After success, redirect to `/` (tenant dashboard) via `LOGIN_REDIRECT_URL`.

4. **Security**
   - User must belong to `request.school` (`UserProfile.school` match) or be superuser; otherwise login rejected with “You do not belong to this school.” and no session.
   - Middleware continues to 404 when an authenticated user’s school does not match the request’s tenant (except superusers).

5. **Cleanup**
   - Removed `login_redirect` and its route; use `TenantLoginView` and `LOGIN_REDIRECT_URL = "/"`.
   - Dashboard context now includes `school`, metrics, and `recent_transactions` from `FeeTransaction`.
   - Template updated for `amount_paid`; non-field login errors displayed correctly.

## Final Request Flow

### Root (e.g. `localhost:8000`)

- `/` → `index`; `request.school` is None → render `marketing.html`. No dashboard.
- `/accounts/login/` → `TenantLoginView.dispatch` sees no tenant → redirect to `index` (marketing). No login form on root.
- Other app routes (e.g. `/students/...`) → views use `get_current_school` → 404 when no tenant.

### Tenant (e.g. `prahlad.localhost:8000`)

- `/` (unauthenticated) → `index`; `request.school` set, user not logged in → `redirect_to_login` to `/accounts/login/` (same host).
- `/` (authenticated, same tenant) → `index` → dashboard with `school`, metrics, `recent_transactions`.
- `/accounts/login/` (unauthenticated) → show login form.
- `/accounts/login/` (authenticated) → `redirect_authenticated_user` → redirect to `/`.
- POST `/accounts/login/` → authenticate; if `UserProfile.school` != `request.school` (and not superuser) → `form_invalid`, no login; else → login and redirect to `/`.
- Logout → redirect to `/accounts/login/` on same host.

### Login Flow (tenant)

1. User visits `prahlad.localhost:8000/` (or another tenant URL) unauthenticated.
2. `index` redirects to `prahlad.localhost:8000/accounts/login/?next=/`.
3. User submits credentials.
4. `TenantLoginView.form_valid`: authenticate; check `UserProfile.school` == `request.school` (or superuser).
5. If mismatch → error “You do not belong to this school.”, no session, form re-displayed.
6. If match → login, redirect to `next` or `/` (tenant dashboard).

## Assumptions

- `TenantMiddleware` already sets `request.school` from subdomain and 404s on unknown subdomain or wrong-tenant authenticated user; no changes.
- Superusers may log in on any tenant and are exempt from `UserProfile.school` check in both login and middleware.
- `LOGIN_URL`, `LOGIN_REDIRECT_URL`, and `LOGOUT_REDIRECT_URL` remain as in settings (`/accounts/login/`, `/`, `/accounts/login/`).
- Marketing “Log in” link still points to `{% url 'login' %}`; on root, that hits `/accounts/login/` and redirects back to marketing.
- PWA, admin, debug toolbar, and static/media routing unchanged.
- `build_school_base_url` in `utils.domain` is unused after removing `login_redirect`; left in place for possible future use.
