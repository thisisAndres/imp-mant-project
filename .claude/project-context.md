# SGIV — Project Context for AI Sessions

> This file captures all architectural decisions, answered questions, and implementation notes
> accumulated across development sessions. Keep it updated as decisions evolve.

---

## Infrastructure Status

| Resource | Status | Notes |
|---|---|---|
| Supabase project | ✅ Active | All 12 tables created and verified in sync with SQLAlchemy models |
| Render account | ✅ Deployed | Backend running as Docker container — env vars configured |
| Vercel account | Created | Frontend not yet started |
| GitHub repo | Active | `thisisAndres/imp-mant-project` |
| `gh` CLI | Not installed | PRs must be opened manually via GitHub web UI |

---

## Backend Implementation Status

### ✅ Completed

| Area | Files |
|---|---|
| ORM Models | `models/` — all 12 tables (roles, users, categories, suppliers, products, inventory, customers, purchase_orders, purchase_order_details, sales_orders, sales_order_details, payments) |
| Schemas | `schemas/` — all Pydantic models with full input validation (Field constraints, allowlist validators) |
| Repositories | `repositories/` — user, product, category, supplier, customer, inventory, purchase_order, sales_order, payment, report |
| Services | `services/` — auth, sales_order, purchase_order, inventory, order_number |
| API Routers | `api/v1/` — auth, users, products, categories, suppliers, customers, inventory, purchase_orders, sales_orders, payments, reports |
| Reports | `reports/pdf_generator.py` (ReportLab) + `reports/excel_generator.py` (openpyxl) |
| Auth | JWT access + refresh tokens, role-based access control (admin / manager / employee) |
| Security hardening | PyJWT migration (CVE-2024-33664/33663 fixed), CSP headers, UUID validation, allowlist validators, extra="ignore" in Settings |
| DB Seed | Roles + admin user seeded on first startup via ADMIN_EMAIL/ADMIN_PASSWORD from Settings |
| CI/CD | `.github/workflows/backend.yml` — lint → test → deploy to Render on push to main |
| Docker | `backend/Dockerfile` + `docker-compose.yml` |
| Postman collection | `SGIV.postman_collection.json` — all endpoints, auto-save token on login |
| README | Project README with local setup and 13-step API testing guide |

### ❌ Still Missing

| Item | Priority | Notes |
|---|---|---|
| `backend/.env.example` | Medium | Deleted from repo; devs must use README as reference |
| `pytest.ini` / `pyproject.toml` | High | `asyncio_mode = auto` required for pytest-asyncio to work |
| `tests/conftest.py` | High | No fixtures yet — async DB session, test client, seeded users |
| `tests/test_auth.py` | High | Stub only (`import pytest`) — CI workaround in place (`|| [ $? -eq 5 ]`) |
| `tests/test_products.py` | High | Stub only |
| `tests/test_reports.py` | High | Stub only |
| Frontend | Next phase | React + Vite — not started yet |

---

## Open Pull Requests (as of 2026-04-05)

| Branch | Target | Description | Status |
|---|---|---|---|
| `fix/security-vulnerabilities` | `develop` | CVE fixes, CSP headers, input validation hardening | Open — not merged |
| `feat/postman-collection-and-seed-fix` | `develop` | Postman collection + admin seed fix | Open — not merged |

---

## Answered Design Questions

### Authentication & Users
- Login page is the app entry point — unauthenticated users are always redirected to `/login`
- First admin user is seeded automatically on first run via `ADMIN_EMAIL` + `ADMIN_PASSWORD` env vars (reads from `settings`, not `os.environ`)
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
- PDF header: plain title only (no company logo)
- PDF and Excel both available; user picks one at a time via a download button
- Report endpoints:
  - `GET /api/v1/reports/sales?start_date=&end_date=&status=&customer_id=&format=pdf|excel`
  - `GET /api/v1/reports/inventory?category_id=&status=&supplier_id=&format=pdf|excel`

---

## Environment Variables Reference

### Backend (`backend/.env`) — never commit
```
DATABASE_URL=postgresql+asyncpg://postgres.<ref>:<pass>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
SECRET_KEY=<random string, min 32 chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173
ADMIN_EMAIL=<admin email>
ADMIN_PASSWORD=<min 12 chars>
```

### Render env vars (production)
Same as above with:
```
APP_ENV=production
ALLOWED_ORIGINS=https://sgiv.vercel.app
```

### GitHub Actions secrets required
| Secret | Status |
|---|---|
| `TEST_DATABASE_URL` | ⚠️ Not confirmed set |
| `RENDER_DEPLOY_HOOK_URL` | ⚠️ Not confirmed set |
| `VERCEL_TOKEN` | ⚠️ Not set (frontend not deployed) |
| `VERCEL_ORG_ID` | ⚠️ Not set |
| `VERCEL_PROJECT_ID` | ⚠️ Not set |

---

## Active Branches

| Branch | Purpose | Status |
|---|---|---|
| `main` | Production | Clean |
| `develop` | Active development | Up to date |
| `fix/security-vulnerabilities` | CVE + hardening fixes | Open PR → develop |
| `feat/postman-collection-and-seed-fix` | Postman + seed fix | Open PR → develop |

---

## Key Business Rules Implemented

```
inventory.quantity -= line.quantity   when sales_order.status → "completed"
inventory.quantity += line.quantity   when purchase_order.status → "received"

order_number = f"SO-{year}-{seq:04d}"   # sales
order_number = f"PO-{year}-{seq:04d}"   # purchases
```

---

## Known Issues / Pending Actions

- [ ] Merge open PRs: `fix/security-vulnerabilities` and `feat/postman-collection-and-seed-fix` → develop
- [ ] Write actual tests (currently stubs) + add `pytest.ini` + `conftest.py`
- [ ] Configure GitHub Actions secrets: `TEST_DATABASE_URL`, `RENDER_DEPLOY_HOOK_URL`
- [ ] Start frontend (Phase 6)
- [ ] Supabase `updated_at` triggers optional — currently relies on SQLAlchemy `onupdate` only

---

## What To Do Next Session

1. **Merge the two open PRs** into develop via GitHub web UI
2. **Write tests** — `conftest.py` with async fixtures, then `test_auth.py`, `test_products.py`, `test_reports.py`
3. **Add `pytest.ini`** with `asyncio_mode = auto`
4. **Start frontend** — scaffold React + Vite + TailwindCSS + Zustand, then implement pages in this order:
   - LoginPage → DashboardPage → ProductsPage → CustomersPage → SuppliersPage → InventoryPage → PurchaseOrdersPage → SalesOrdersPage → ReportsPage

---

*Last updated: 2026-04-05*
