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
