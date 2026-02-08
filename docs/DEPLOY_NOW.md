# Deploy Now — Step by Step

Ye guide aapko **Render.com** pe deploy karne me help karegi (free tier available).

---

## Blueprint Deploy (render.yaml) — Manual DATABASE_URL Required

Agar aap **Blueprint** se deploy kar rahe ho (angcore, render.yaml):

1. Blueprint sync karo — database aur web service ban jayenge
2. **DATABASE_URL manually add karo:**
   - Render Dashboard → **school-erp** → **Environment**
   - **Add Environment Variable**: `DATABASE_URL`
   - Value: **External** connection string from **school-erp-db** → **Connect**
   - (Internal URL cross-region pe kaam nahi karta — web Oregon, DB Singapore)
3. **Save Changes** → Manual Deploy trigger karo

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

## Step 5: Demo users / Login (Render pe)

**Blueprint (render.yaml) use kar rahe ho:**  
Start command me `setup_login_users --run-if-empty` hai — **pehli deploy** pe jab DB empty hoti hai, tab automatically demo school + users (admin, teacher, staff, etc.) ban jate hain. Koi extra step nahi. Login: `/accounts/login/` — credentials plan me (admin / adminpass123, etc.).

**Agar manual Web Service bana rahe ho** (render.yaml nahi use kar rahe):

1. Web Service page → **Shell** tab
2. Run karo:

```bash
python manage.py migrate
python manage.py setup_login_users
```

Ya superuser se start karo: `python manage.py createsuperuser`, phir `/admin/` se School add karo.

**Password reset / demo users dubara chahiye:**  
Render Shell me run karo: `python manage.py setup_login_users` (bina `--run-if-empty` — sab passwords reset ho jayenge).

**Render Shell access nahi hai — local CMD/script se run karo:**  
Apne computer se Render DB pe command chalane ke liye:

1. Render Dashboard → **school-erp-db** → **Connect** → **External** connection string copy karo (postgresql://...)
2. Project root (mysite) pe terminal kholo aur run karo:

```bash
# Sab demo users create/reset (passwords reset)
DATABASE_URL='postgresql://user:pass@host:5432/dbname' python manage.py setup_login_users
```

Ya script use karo (same DATABASE_URL chahiye):

```bash
DATABASE_URL='postgresql://...' ./scripts/setup_render_login_users.sh
```

Pehli baar sirf jab koi user na ho tab run karna ho to: `... setup_login_users --run-if-empty` ya script ke saath `./scripts/setup_render_login_users.sh --run-if-empty`

---

## Step 6: First School Setup

1. Apna URL open karo: `https://school-erp-xxxx.onrender.com`
2. Login: `/accounts/login/` — Blueprint deploy me demo users pehle se bane honge (admin / adminpass123, etc.)
3. Agar chaho to `/admin/` se School edit karo ya nayi school add karo
4. UserProfile me school link karo (demo users pehli school se already linked hote hain)

---

## Demo users on Render (summary)

| Option | Kab use karein |
|--------|-----------------|
| **Option A — Render Shell** | Shell access ho to: Dashboard → school-erp → **Shell** → `python manage.py setup_login_users` |
| **Option B — Auto (startCommand)** | Blueprint (render.yaml) se deploy — pehli deploy pe `setup_login_users --run-if-empty` automatically chal jata hai |
| **Option C — Local CMD / script** | Shell access nahi ho to: Render se **External** DATABASE_URL copy karo, phir local terminal se `DATABASE_URL='...' python manage.py setup_login_users` ya `DATABASE_URL='...' ./scripts/setup_render_login_users.sh` |

---

## Common Issues

| Problem | Solution |
|---------|----------|
| 502 Bad Gateway | Wait 1–2 min, cold start |
| Static files nahi dikh rahe | `collectstatic` build command me hai — verify karo |
| CSRF error | Environment me add karo: `CSRF_TRUSTED_ORIGINS` = `https://school-erp-XXXX.onrender.com` (apna exact URL) |
| DB connection error | Use **External** connection string (web + DB different regions). `settings.py` converts internal host automatically. |
| Sync "id is empty" | Blueprint me `DATABASE_URL` fromDatabase hata diya — manually add karo (Blueprint section dekho) |

---

## Render CLI automatic workflow

Workspace/service select karne ka prompt na aaye — scripts se seedha deploy trigger (aur optional login users reset).

**One-time setup:**

1. **API key:** Render Dashboard → Account Settings → API Keys → Create. Export: `RENDER_API_KEY=rnd_xxx`
2. **Service ID:** school-erp ka ID chahiye. Get: `render services --output json --confirm` (after `render login`) ya Dashboard → school-erp → URL me `srv-xxxx`. Export: `RENDER_SERVICE_ID=srv-xxx`
3. (Optional) Pehli baar `render login` aur `render workspace set` chala lo — local config me workspace save ho jayega; uske baad scripts API key + service ID use karke bina prompt chalengi.

**Commands (project root = mysite):**

| Goal | Command |
|------|--------|
| Deploy only | `export RENDER_API_KEY=... RENDER_SERVICE_ID=...` then `./scripts/render_deploy.sh` |
| Deploy + reset demo users | Same env + `export DATABASE_URL=...` (Render External URL) then `./scripts/render_workflow.sh` |

`.env` me bhi ye vars daal sakte ho; scripts env se read karti hain.

---

## Custom Domain (Optional)

1. Render Dashboard → Your Service → **Settings** → **Custom Domains**
2. Add: `schoolsoft.in` (apna domain)
3. DNS me CNAME set karo: `schoolsoft.in` → `school-erp-xxxx.onrender.com`
4. `ALLOWED_HOST` me add karo: `schoolsoft.in,.schoolsoft.in`
