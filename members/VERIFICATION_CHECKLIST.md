# Tenant Resolver Verification Checklist

Run after `python manage.py migrate` and with Django available.

## 1. School.code exists and is unique

- **Model:** `members.models.School` has `code = SlugField(max_length=64, unique=True)`.
- **Migration:** `0023_school_code_slug` adds and backfills `code`.
- **Test:** `members.tests_tenant.SchoolCodeTests.test_code_field_exists_and_unique`

```bash
python manage.py test members.tests_tenant.SchoolCodeTests -v 2
```

## 2. TenantMiddleware sets `request.school`

- **Middleware:** `members.middleware.tenant.TenantMiddleware` sets `request.school` when subdomain matches `School.code`; sets `request.school = None` when no subdomain.
- **Test:** `members.tests_tenant.TenantMiddlewareTests`

```bash
python manage.py test members.tests_tenant.TenantMiddlewareTests -v 2
```

## 3. `extract_subdomain` behaviour

| Host | Expected |
|------|----------|
| `school.domain.com` | `"school"` |
| `school.localhost` | `"school"` |
| `school.localhost:8000` | `"school"` |
| `www.domain.com` | `None` (no tenant) |
| `localhost`, `127.0.0.1`, `example.com` | `None` |

- **Code:** `members.utils.domain.extract_subdomain`
- **Test:** `members.tests_tenant.ExtractSubdomainTests`

```bash
python manage.py test members.tests_tenant.ExtractSubdomainTests -v 2
```

## 4. Public root does not bind a tenant

- **Middleware:** When `extract_subdomain` returns `None`, `request.school = None` and the request continues (no 404).
- **Test:** `TenantMiddlewareTests.test_no_subdomain_sets_school_none` (covers `localhost`, `example.com`, `www.domain.com`).

## 5. Root views must not break when `request.school` is missing

- **Index:** Uses `getattr(request, "school", None)`; if missing, renders `marketing.html` and never calls `get_current_school`.
- **login_redirect:** Uses `getattr(request, "school", None)` only; never `get_current_school`.
- **login / logout:** Django auth views; do not use `request.school`.
- **Test:** `members.tests_tenant.RootViewsNoSchoolTests`

```bash
python manage.py test members.tests_tenant.RootViewsNoSchoolTests -v 2
```

---

## Run all tenant verification tests

```bash
python manage.py test members.tests_tenant -v 2
```

## Quick `extract_subdomain` check

```bash
python manage.py shell -c "
from members.utils.domain import extract_subdomain
assert extract_subdomain('school.domain.com') == 'school'
assert extract_subdomain('school.localhost') == 'school'
assert extract_subdomain('www.domain.com') is None
print('extract_subdomain OK')
"
```
