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

## Step 3b: Render CLI – Workspace Set (if using CLI)

Agar `render services` ya `render deploys create` pe "no workspace set" error aaye:

```bash
render workspace set
```

Phir interactive menu se apna workspace (e.g. "My Workspace") select karo – Enter dabao.

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

---

## Deploy Fail – Troubleshooting

### 1. Deploy logs kaise dekhein

**Render Dashboard:**
1. [dashboard.render.com](https://dashboard.render.com) → **school-erp**
2. **Logs** tab → Build / Deploy / Runtime logs
3. Red errors ya failed step pe click karke full traceback dekho

**Render CLI:**
```bash
render workspace set   # pehle workspace select karo
render deploys list srv-d63h5o7gi27c739g79f0 -o json   # latest deploy ID dekho
# Logs ke liye: Dashboard → school-erp → Logs (CLI me deploy logs command nahi hai)
```

### 2. Common failures aur fix

| Error / Symptom | Fix |
|----------------|-----|
| **Build fail** – `pip install` / `ModuleNotFoundError` | `requirements.txt` check karo; `runtime.txt` ya `nixpacks.toml` add karo agar Python version fix karni ho |
| **preDeploy fail** – `migrate` / `setup_login_users` | `DATABASE_URL` set karo (school-erp-db → Connect → External URL). Database expired ho to naya DB banao |
| **preDeploy fail** – `Unknown command` | Verify `members/management/commands/setup_login_users.py` exists; command name = filename without .py |
| **Health check timeout** | `startCommand` me sirf gunicorn hona chahiye; migrate/collectstatic `preDeployCommand` / `buildCommand` me hona chahiye |
| **Root directory** – `manage.py` not found | Agar repo me `mysite` subfolder hai: Dashboard → school-erp → Settings → **Root Directory** = `mysite` |
| **500 on /health/** | `ALLOWED_HOSTS` me `.onrender.com` hona chahiye; `DEBUG=False` production me |

### 3. Root Directory (agar project subfolder me hai)

Agar GitHub repo structure aisa hai:
```
student-system/
  mysite/           ← manage.py yahan hai
    manage.py
    mysite/
    members/
  render.yaml
```

To Render Dashboard → school-erp → **Settings** → **Root Directory** = `mysite` set karo.

---

## Render CLI Automation

### Local script (one command deploy)

```bash
cd /Users/prahalad/django_projects/mysite
chmod +x scripts/render_automate.sh

# Deploy (pehle: render login + render workspace set)
./scripts/render_automate.sh deploy

# Status dekho
./scripts/render_automate.sh status
```

**Non-interactive (API key):**
```bash
export RENDER_API_KEY=rnd_xxx   # Dashboard → Account Settings → API Keys
export RENDER_SERVICE_ID=srv-d63h5o7gi27c739g79f0
./scripts/render_automate.sh deploy
```

### GitHub Actions

| Workflow | Trigger | Use |
|----------|---------|-----|
| **Render CLI Deploy** | Manual (Run workflow) | One-click deploy |
| **Render Deploy on Push** | Push to `main` | Auto-deploy on every push |

**Secrets required:** `RENDER_API_KEY`, `RENDER_SERVICE_ID`

Agar Render Dashboard me Auto-Deploy already on hai, to **Render Deploy on Push** disable karo (ya Render Auto-Deploy off karo) — dono chalne se double deploy hoga.

### Auto seed (demo data)

`preDeployCommand` me `create_test_data --run-if-empty` add hai. **Pehli deploy** pe (jab DB empty ho) automatically students, transport, library, fees ka demo data ban jayega. Local jaisa dashboard Render pe bhi dikhega.
