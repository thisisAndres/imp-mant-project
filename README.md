# SGIV — Sistema de Gestión de Inventario y Ventas

Full-stack web application for inventory and sales management for small and medium businesses.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 18 + Vite + TailwindCSS + Zustand |
| Backend | FastAPI + SQLAlchemy 2 (async) + Alembic |
| Database | PostgreSQL 15 (Supabase) |
| Reports | ReportLab (PDF) + openpyxl (Excel) |
| Auth | JWT (python-jose + passlib) |
| Deploy | Vercel (frontend) + Render (backend) |
| CI/CD | GitHub Actions |

## Features

- Role-based authentication (Admin, Manager, Employee)
- Full CRUD for products, customers, suppliers
- Purchase and sales order management
- Real-time inventory control
- Downloadable PDF and Excel reports
- Dashboard with key metrics

## Local Development

### With Docker Compose

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker-compose up --build
```

### Without Docker

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## Environments

| Environment | Branch | Frontend | Backend |
|---|---|---|---|
| Development | `develop` | localhost:5173 | localhost:8000 |
| Staging | `staging` | sgiv-staging.vercel.app | sgiv-api-staging.onrender.com |
| Production | `main` | sgiv.vercel.app | sgiv-api.onrender.com |

## API Docs

Available at `http://localhost:8000/docs` when running locally.
