# SaaS Deployment Guide — Option A (Multi-School Cloud)

Aapka School ERP already **SaaS-ready** hai. Ye guide production deploy karne ke liye hai.

---

## ✅ Already In Place

- **Single shared database** — sab schools ka data ek DB me, `school_id` se isolated
- **Subdomain-based tenancy** — `abc.yoursite.com` → School with `code = "abc"`
- **TenantMiddleware** — request pe `request.school` set karta hai
- **All views** — `get_current_school(request)` use karte hain, data leak nahi
- **extract_subdomain()** — localhost + production dono support

---

## Production Checklist

### 1. Domain & DNS

- Apna domain lo: e.g. `schoolsoft.in` ya `yourapp.com`
- **Wildcard DNS** set karo:
  ```
  A    *.schoolsoft.in    →    YOUR_SERVER_IP
  A    schoolsoft.in      →    YOUR_SERVER_IP
  ```

### 2. Environment Variables (.env)

```bash
DEBUG=False
DJANGO_SECRET_KEY=your-long-random-secret-key
ALLOWED_HOST=schoolsoft.in,.schoolsoft.in
# CSRF: Add each subdomain or use https://schoolsoft.in for root
CSRF_TRUSTED_ORIGINS=https://schoolsoft.in,https://abc.schoolsoft.in,https://xyz.schoolsoft.in
DATABASE_URL=postgresql://user:pass@localhost:5432/schoolerp
```

### 3. Database Migration (SQLite → PostgreSQL)

```bash
# Install
pip install psycopg2-binary dj-database-url

# .env me add
DATABASE_URL=postgresql://user:password@localhost:5432/schoolerp

# Migrate
python manage.py migrate
python manage.py collectstatic --noinput
```

Settings automatically use PostgreSQL when `DATABASE_URL` is set.

### 4. Server Setup (Ubuntu VPS example)

```bash
# Nginx reverse proxy (wildcard subdomain support)
server {
    server_name schoolsoft.in *.schoolsoft.in;
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    location /static/ { alias /path/to/staticfiles/; }
    location /media/  { alias /path/to/media/; }
}
```

### 5. SSL (Let's Encrypt)

```bash
sudo certbot certonly --nginx -d schoolsoft.in -d "*.schoolsoft.in"
```

### 6. Add New School (Superuser)

1. Login as superuser
2. `/schools/` → "Add New School"
3. Fill: Name, Address, School Code, **Subdomain Code** (e.g. `abc` for abc.schoolsoft.in)
4. Create Owner user and link `UserProfile.school` to new school

---

## URL Structure

| URL | Purpose |
|-----|---------|
| `https://schoolsoft.in` | Marketing / Login (no subdomain → first school or marketing) |
| `https://abc.schoolsoft.in` | ABC School ka ERP |
| `https://xyz.schoolsoft.in` | XYZ School ka ERP |

---

## Important Notes

- **Localhost dev:** Subdomain nahi hone pe first school auto-select (already working)
- **Production:** Subdomain **required** — `schoolsoft.in` pe directly login pe first school assume hoga (TenantMiddleware logic)
- **Marketing page:** Root domain pe marketing template show kar sakte ho (index view already checks `request.school`)

---

## Quick Deploy (Railway / Render / Fly.io)

1. Connect your repo to Railway/Render
2. Set env vars:
   - `DATABASE_URL` (PostgreSQL - usually auto-provisioned)
   - `DJANGO_SECRET_KEY`
   - `ALLOWED_HOST` = `yourdomain.com,.yourdomain.com`
   - `DEBUG` = `False`
3. Build: uses `Procfile` → `gunicorn mysite.wsgi:application`
4. Health check: `GET /health/` returns `200 OK`
5. Run migrations: `python manage.py migrate` (add as release command if supported)
