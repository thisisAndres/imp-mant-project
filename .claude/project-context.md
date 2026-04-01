# SGIV — Project Context for AI Sessions

> This file captures all architectural decisions, answered questions, and implementation notes
> accumulated across development sessions. Keep it updated as decisions evolve.

---

## Infrastructure Status

| Resource | Status | Notes |
|---|---|---|
| Supabase project | Created | Tables do NOT exist yet — must be created via Alembic migrations |
| Render account | Created | Backend will be deployed as Docker container |
| Vercel account | Created | Frontend will be deployed there |
| GitHub repo | Active | `thisisAndres/imp-mant-project` |

---

## Answered Design Questions

### Authentication & Users
- Login page is the app entry point — unauthenticated users are always redirected to `/login`
- First admin user is seeded automatically on first run (`init_db.py`)
- **Role visibility:** employees do NOT see restricted sidebar items at all (completely hidden, not grayed out)
  - Admin/Manager: full sidebar
  - Employee: only Inventory (read-only) + Sales Orders (create only)

### Frontend / UI
- Design: clean, neutral TailwindCSS — no external wireframes or brand colors provided
- **Dashboard metrics (4 cards/charts):**
  1. Total sales today (monetary value)
  2. Revenue this month (monetary value)
  3. Top products (by quantity sold this month)
  4. Low-stock alerts (products below `min_stock`)

### Business Logic
- **Sales order → `completed`:** automatically decrement inventory for each line item
- **Purchase order → `received`:** automatically increment inventory for each line item
- **Order number format:** auto-generated, never entered manually
  - Sales orders: `SO-YYYY-NNNN` (e.g., `SO-2026-0001`)
  - Purchase orders: `PO-YYYY-NNNN` (e.g., `PO-2026-0001`)
  - Sequence resets per year; padded to 4 digits

### Reports
- PDF header: plain title only (no company logo for now)
- PDF and Excel are both available; user picks one at a time via a download button
- Report endpoints:
  - `GET /api/v1/reports/sales?start_date=&end_date=&status=&customer_id=&format=pdf|excel`
  - `GET /api/v1/reports/inventory?category_id=&status=&supplier_id=&format=pdf|excel`

---

## Implementation Order (Backend-First)

### Phase 1 — Database (current focus)
1. Write all 12 SQLAlchemy ORM models in `backend/app/models/`
2. Create initial Alembic migration (`alembic revision --autogenerate -m "initial schema"`)
3. Run `alembic upgrade head` against Supabase to create tables
4. Seed: roles + first admin user in `init_db.py`

### Phase 2 — Core Backend
5. `core/config.py` — Settings via pydantic-settings
6. `core/security.py` — JWT creation/validation, bcrypt hashing
7. `core/dependencies.py` — `get_current_user`, `require_role` dependencies
8. `db/session.py` — async SQLAlchemy engine + session factory

### Phase 3 — API Routers + Services + Repositories
Order (dependencies first):
- auth → users → categories → suppliers → products → inventory → customers → purchase_orders → sales_orders → payments → reports

Each module follows: `router → service → repository` layering.

### Phase 4 — Reports
- `reports/pdf_generator.py` — ReportLab, plain title
- `reports/excel_generator.py` — openpyxl

### Phase 5 — Tests
- `tests/test_auth.py`, `tests/test_products.py`, `tests/test_reports.py`
- Minimum 70% coverage target

### Phase 6 — Frontend (after backend is complete and deployed)

---

## Key Business Rules to Encode

```
inventory.quantity -= line.quantity   when sales_order.status → "completed"
inventory.quantity += line.quantity   when purchase_order.status → "received"

order_number = f"SO-{year}-{seq:04d}"   # sales
order_number = f"PO-{year}-{seq:04d}"   # purchases
```

---

## Environment Variables Reference

### Backend (`backend/.env`) — never commit
```
DATABASE_URL=postgresql+asyncpg://<user>:<pass>@<supabase-host>:5432/sgiv_db
SECRET_KEY=<long random string>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
APP_ENV=production
ALLOWED_ORIGINS=https://sgiv.vercel.app
```

### Root (`.env`) — docker-compose local postgres
```
POSTGRES_DB=sgiv_db
POSTGRES_USER=dev
POSTGRES_PASSWORD=<set locally, never commit>
```

---

## Active Branches

| Branch | Purpose |
|---|---|
| `main` | Production-ready merged code |
| `feature/backend-implementation` | Current — backend build |
| `fix/remove-hardcoded-postgres-password` | Open PR — GitGuardian fix |

---

## Known Issues / Pending Actions

- [ ] PR #fix/remove-hardcoded-postgres-password needs to be merged to main (GitGuardian fix)
- [ ] GitHub Actions secrets need to be configured: `TEST_DATABASE_URL`, `RENDER_DEPLOY_HOOK_URL`, `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`
- [ ] `gh` CLI not installed on this machine — PRs must be opened manually via GitHub web UI

---

*Last updated: 2026-04-01*
