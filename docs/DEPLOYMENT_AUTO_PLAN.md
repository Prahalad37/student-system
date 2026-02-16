# Automatic Deployment Plan — school-erp (Render)

Screenshot ke hisaab se tumhara service **school-erp** pehle se Render pe hai. Ye plan automatic deploy ko ensure karega.

---

## Current Setup (Screenshot se)

| Item | Value |
|------|-------|
| Service | school-erp |
| Type | Web Service, Python 3 |
| Instance | Free (inactivity pe spin down) |
| Source | Prahalad37/student-system |
| Live URL | https://school-erp-51hd.onrender.com |
| Service ID | srv-d63h5o7gi27c739g79f0 |
| Management | Blueprint managed |

---

## Step 1: Render Auto-Deploy Verify/Enable

Render by default GitHub push pe auto-deploy karta hai. Ensure karo:

1. Render Dashboard → **school-erp** → **Settings**
2. **Build & Deploy** section me jao
3. **Auto-Deploy** → **Yes** hona chahiye
4. **Branch** → `main` (ya jo production branch hai)

**Flow:** `git push origin main` → Render automatically naya deploy trigger karega.

---

## Step 2: GitHub Branch Setup

Agar tum `main` branch pe push karte ho, Render automatically deploy karega.

```bash
# Local se deploy trigger karne ke liye:
git add .
git commit -m "Your changes"
git push origin main
```

Push ke 1–2 min baad Render pe "Deploy started" → "Deploy live" dikhega.

---

## Step 3: (Optional) GitHub Actions — Test Before Deploy

Agar tum chahte ho ki **sirf tests pass hone pe hi deploy ho**, toh ye workflow use karo:

- Push → GitHub Actions tests chalate hain
- Tests pass → Render deploy trigger hota hai
- Tests fail → Deploy nahi hota

Iske liye:
1. Render **Auto-Deploy = No** kar dena (Settings me)
2. GitHub repo → Settings → Secrets:
   - `RENDER_API_KEY` — Render Dashboard → Account → API Keys se
   - `RENDER_SERVICE_ID` — `srv-d63h5o7gi27c739g79f0`

File already exists: `.github/workflows/deploy-on-tests-pass.yml` — sirf secrets add karo.

---

## Step 4: Quick Reference — Deploy Commands

| Goal | Command |
|------|---------|
| Normal deploy | `git push origin main` (Render auto-deploy) |
| Manual deploy | Render Dashboard → Manual Deploy |
| Rollback | Render Dashboard → Events → Rollback |
| Shell / migrate | Render → school-erp → Shell → `python manage.py migrate` |

---

## Checklist

- [ ] Render Auto-Deploy = **Yes**
- [ ] Branch = **main**
- [ ] `DATABASE_URL` Environment me set hai (External URL)
- [ ] `DJANGO_SECRET_KEY` strong value (dashboard me change karo)
- [ ] Push to main → Deploy events dikhne chahiye

---

## Free Instance Note

Free instance **inactivity** pe spin down ho jata hai. Pehli request pe 1–2 min lag sakte hain (cold start). Agar production use hai toh **Paid** plan consider karo.
