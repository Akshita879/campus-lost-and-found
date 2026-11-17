# FindIt – Smart Campus Lost & Found (frontend)

```bash
npm install
npm run dev      # http://localhost:5173
npm run build
```

Routes: `/` · `/explore` · `/report` · `/matches` · `/verify/:id` · `/notifications`

## Backend connection

1. Copy `.env.example` to `.env`
2. Set `VITE_USE_MOCKS=false` and `VITE_API_URL=http://localhost:8000/api/v1`
3. Run the FastAPI backend on port 8000

API calls live in `src/services/`. Auth token is stored in `localStorage` and sent as Bearer.

| UI action | Backend |
|-----------|---------|
| Browse / search | `GET /reports/search` |
| Item detail | `GET /reports/{id}` |
| Submit report | `POST /reports` or `POST /reports/upload` |
| Claim found item | `POST /claims` |
| Suggested matches | `GET /matches` (auth) |
| Sign in / register | `POST /auth/login`, `POST /auth/register` |

Vite proxies `/api` → `/api/v1` and `/uploads` when using the local proxy in `vite.config.js`.

## Deploy on Vercel (multi-service)

Root `vercel.json` deploys **frontend** (Vite) + **backend** (FastAPI) as one project:

- `/` → frontend  
- `/api/*`, `/uploads/*`, `/docs`, `/health` → backend  

1. Push the repo to GitHub (includes root `vercel.json`).
2. Host **MySQL** somewhere public (Railway, etc.) and copy `DATABASE_URL`.
3. In [Vercel](https://vercel.com) → import the repo with Root Directory `./` (repo root).
4. Environment variables:

| Scope | Name | Value |
|-------|------|--------|
| Frontend | `VITE_USE_MOCKS` | `false` |
| Frontend | `VITE_API_URL` | `/api/v1` |
| Backend | `DATABASE_URL` | `mysql+pymysql://USER:PASS@HOST:PORT/DB` |
| Backend | `JWT_SECRET_KEY` | long random string |
| Backend | `CORS_ORIGINS` | `*` |

5. Against that MySQL, run once: `alembic upgrade head` (from `backend/`, with the same `DATABASE_URL`).
6. Deploy. Open the Vercel URL; API docs at `/docs`.

No service bindings are required — the browser calls same-origin `/api/v1`.
