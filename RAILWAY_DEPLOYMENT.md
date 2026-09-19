# Railway Deployment Guide

## Quick Start (5 minutes)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Deploy Backend on Railway
1. Go to [railway.app](https://railway.app) → "New Project" → "Deploy from GitHub repo"
2. Select your repo
3. Railway auto-detects `railway.toml` and uses `backend/Dockerfile`
4. Add **PostgreSQL** service: "New" → "Database" → "PostgreSQL"
5. Add **Redis** service: "New" → "Database" → "Redis"
6. Set environment variables (see below)

### 3. Deploy Frontend (Option A: Vercel - Recommended)
1. Go to [vercel.com](https://vercel.com) → "New Project" → Import from GitHub
2. Select `frontend-dashboard` folder as root
3. Build command: `npm run build` (auto-detected)
4. Output directory: `dist` (auto-detected)
5. Add environment variable: `VITE_API_URL=https://your-backend.railway.app`

### 4. Deploy Frontend (Option B: Railway)
1. In same Railway project: "New Service" → "GitHub Repo" → Select same repo
2. Set **Root Directory**: `frontend-dashboard`
3. Railway uses `frontend-dashboard/railway.toml` and `frontend-dashboard/Dockerfile`
4. Set `VITE_API_URL` to internal backend URL: `http://backend.railway.internal:8000`

---

## Required Environment Variables (Backend)

| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | Auto-provided by Railway PostgreSQL | Railway PostgreSQL service → "Connect" tab |
| `REDIS_URL` | Auto-provided by Railway Redis | Railway Redis service → "Connect" tab |
| `SECRET_KEY` | `openssl rand -hex 32` | Generate locally |
| `GEMINI_API_KEY` | Your Google AI Studio key | [aistudio.google.com](https://aistudio.google.com) |
| `DEBUG` | `false` | Production |
| `ALLOWED_ORIGINS` | `https://your-frontend.vercel.app` | Your frontend URL |

### To set in Railway:
1. Click your backend service → "Variables" tab
2. Add each variable
3. Railway auto-redeploys on change

---

## Database Setup

After backend deploys, run migrations:
```bash
# In Railway backend service shell:
alembic upgrade head
```

Or add to Dockerfile CMD:
```dockerfile
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## Frontend API Configuration

Update `frontend-dashboard/src/services/apiClient.js`:
```javascript
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

---

## Custom Domain

1. Railway: Service → Settings → "Custom Domain" → Add your domain
2. Vercel: Project → Settings → Domains → Add
3. Update `ALLOWED_ORIGINS` and `VITE_API_URL` accordingly

---

## Monitoring

- Railway: Metrics tab (CPU, Memory, Network)
- Logs: Railway service → "Logs" tab
- Health: `https://your-backend.railway.app/health`

---

## Troubleshooting

**Build fails**: Check logs, ensure `requirements.txt` has all deps
**DB connection error**: Verify `DATABASE_URL` format: `postgresql+asyncpg://user:pass@host:port/db`
**CORS error**: Update `ALLOWED_ORIGINS` in backend env vars
**Frontend can't reach API**: Check `VITE_API_URL` and CORS settings