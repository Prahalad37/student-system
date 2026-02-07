# Deploy Now — Step by Step

Ye guide aapko **Render.com** pe deploy karne me help karegi (free tier available).

---

## Step 1: GitHub pe Code Push karo

```bash
cd /Users/prahalad/django_projects/mysite
git add .
git commit -m "Ready for deployment"
git push origin main
```

> Agar repo nahi hai: `git init` → GitHub pe new repo banao → `git remote add origin <url>` → push

---

## Step 2: Render.com pe Account

1. https://render.com pe jao
2. **Sign Up** (GitHub se login best hai)
3. Dashboard open hoga

---

## Step 3: PostgreSQL Database Banao

1. Render Dashboard → **New** → **PostgreSQL**
2. Name: `school-erp-db`
3. Region: Singapore (nearest) ya Oregon
4. Plan: **Free**
5. **Create Database**
6. Database banne ke baad, **Internal Database URL** copy karo (ye `DATABASE_URL` hai)

---

## Step 4: Web Service Deploy karo

1. Dashboard → **New** → **Web Service**
2. **Connect** your GitHub repo (agar nahi hai toh "Build and deploy from an external repository" se URL daal sakte ho)
3. Repo select: `mysite` / aapka project
4. Settings:

| Field | Value |
|-------|-------|
| **Name** | school-erp |
| **Region** | Same as DB |
| **Branch** | main |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn mysite.wsgi:application --bind 0.0.0.0:$PORT` |

5. **Environment** section me add karo:

| Key | Value |
|-----|-------|
| `DJANGO_SECRET_KEY` | Generate: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DATABASE_URL` | PostgreSQL URL (Step 3 me copy kiya) |
| `DEBUG` | `False` |
| `ALLOWED_HOST` | `.onrender.com` (dot se start — sab subdomains allow) |

6. **Create Web Service**

---

## Step 5: Migrations Run karo

Deploy hone ke baad (2–3 min):

1. Web Service page → **Shell** tab (ya **Logs** ke paas)
2. Shell open karo aur run karo:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Superuser banao — ye aapka admin login hoga.

---

## Step 6: First School Setup

1. Apna URL open karo: `https://school-erp-xxxx.onrender.com`
2. Admin se login: `/admin/` ya created superuser
3. School add karo: `/schools/add/` (superuser only)
4. UserProfile me school link karo

---

## Common Issues

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Wait 1–2 min, cold start |
| Static files nahi dikh rahe | `collectstatic` build command me hai — verify karo |
| CSRF error | Environment me add karo: `CSRF_TRUSTED_ORIGINS` = `https://school-erp-XXXX.onrender.com` (apna exact URL) |
| DB connection error | `DATABASE_URL` sahi paste kiya? Internal URL use karo |

---

## Custom Domain (Optional)

1. Render Dashboard → Your Service → **Settings** → **Custom Domains**
2. Add: `schoolsoft.in` (apna domain)
3. DNS me CNAME set karo: `schoolsoft.in` → `school-erp-xxxx.onrender.com`
4. `ALLOWED_HOST` me add karo: `schoolsoft.in,.schoolsoft.in`
