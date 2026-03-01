# Render Post-Fix Steps (Manual)

After the `render.yaml` update (preDeployCommand + simplified startCommand), complete these steps in Render Dashboard and GitHub.

---

## Step 1: Push Code to GitHub

```bash
cd /Users/prahalad/django_projects/mysite
git add render.yaml
git commit -m "Fix: use preDeployCommand for migrate/collectstatic to fix health check timeout"
git push origin main
```

If your repo structure has `mysite` as a subfolder, push from the repo root and ensure `render.yaml` is included.

---

## Step 2: Switch Deploy Branch to main

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Open **school-erp** service
3. **Settings** → **Branch** → select `main`
4. **Save Changes**

---

## Step 3: Verify Database and DATABASE_URL

1. **school-erp-db** → Check status:
   - If **Expired** or **Unavailable**: Create new free Postgres or use [Neon](https://neon.tech) (see previous plan)
   - If **Available**: Proceed

2. **school-erp** → **Environment** → Verify `DATABASE_URL`:
   - Use **External** connection string from school-erp-db → Connect
   - Format: `postgresql://user:password@host:5432/dbname` (not `postgres://`)

---

## Step 4: Trigger Manual Deploy

1. **school-erp** → **Manual Deploy** → **Deploy latest commit**
2. Wait for build → pre-deploy (migrate) → start (gunicorn)
3. Check **Logs** for any errors

---

## Step 5: Enable GitHub Actions (Keep-Alive)

1. GitHub → **Prahalad37/student-system** → **Settings** → **Actions** → **General**
2. Ensure "Allow all actions and reusable workflows" is enabled
3. **Actions** tab → **Render Keep-Alive** workflow should run every 14 minutes

---

## Step 6: Verify Health Check

```bash
curl -w "\nTime: %{time_total}s\n" https://school-erp-51hd.onrender.com/health/
```

Expected: `OK` and response time ~1–3 seconds (or ~50s on cold start).
