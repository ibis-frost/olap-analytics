# Deploy Guide

Deploy the full stack (API + dashboard) on **Render free tier** in one service.

## Quick deploy (about 5 minutes)

### 1. Push to GitHub

```powershell
cd c:\Users\15cal\projects\helloworld
git init
git add .
git commit -m "OLAP analytics demo"
```

Create a new repo at https://github.com/new (name it `olap-analytics`), then:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/olap-analytics.git
git branch -M main
git push -u origin main
```

### 2. Deploy on Render

1. Go to https://dashboard.render.com
2. Click **New** → **Blueprint**
3. Connect your GitHub account and select the `olap-analytics` repo
4. Render reads `render.yaml` automatically
5. Click **Apply**

Optional: add `DATABASE_URL` in the Render dashboard with a [Neon](https://neon.tech) Postgres connection string. If omitted, the build uses the CSV fallback (still works for the demo).

Your live app will be at:

`https://olap-analytics.onrender.com` (or similar)

- Dashboard: `/`
- API docs: `/docs`
- Health: `/health`

> **Note:** Free tier sleeps after ~15 min idle. First load may take ~30s.

## Optional: split frontend + API

| Component | Service | Root directory | Env vars |
|-----------|---------|----------------|----------|
| API | Render Web Service | `.` | `DATABASE_URL`, `CORS_ORIGINS` |
| UI | Vercel | `web` | `VITE_API_URL=https://your-api.onrender.com` |

Use this if you want separate Vercel hosting for the React app.

## Verify after deploy

```powershell
curl https://YOUR-APP.onrender.com/health
curl https://YOUR-APP.onrender.com/api/metrics/summary
```

Then open `https://YOUR-APP.onrender.com` in your browser.
