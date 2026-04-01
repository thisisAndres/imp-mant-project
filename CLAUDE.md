# CLAUDE.md — Sistema de Gestión de Inventario y Ventas (SGIV)

> Archivo de contexto del proyecto para asistencia con IA.  
> Este documento describe la arquitectura, estructura, convenciones y decisiones técnicas del proyecto.

---

## 📋 Descripción General

**SGIV** es una aplicación web full-stack de gestión de inventario y ventas para pequeñas y medianas empresas. Permite administrar productos, clientes, proveedores, órdenes de compra y venta, y generar reportes en PDF/Excel.

### Funcionalidades Principales
- Autenticación de usuarios con roles (Admin, Gerente, Empleado)
- CRUD completo de productos, clientes y proveedores
- Gestión de órdenes de compra y venta
- Control de inventario en tiempo real
- Generación de 2 reportes descargables (PDF y Excel)
- Dashboard con métricas clave
- CI/CD automatizado con GitHub Actions

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                        │
│                     React.js + Vite + TailwindCSS               │
│                     Deployed on: Vercel                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / REST API
┌──────────────────────────▼──────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
│              Python 3.11 · Pydantic · SQLAlchemy                │
│              ReportLab (PDF) · openpyxl (Excel)                 │
│              Deployed on: Render (Docker container)             │
└──────────────────────────┬──────────────────────────────────────┘
                           │ PostgreSQL (asyncpg)
┌──────────────────────────▼──────────────────────────────────────┐
│                     DATABASE (PostgreSQL)                       │
│                     Hosted on: Supabase                         │
│                     10+ tablas relacionadas                     │
└─────────────────────────────────────────────────────────────────┘
```

### Patrón de Arquitectura
- **Frontend:** SPA (Single Page Application) con React Router v6
- **Backend:** REST API siguiendo principios RESTful, capas: Router → Service → Repository → DB
- **Base de Datos:** Relacional (PostgreSQL) gestionada en Supabase
- **Contenedores:** Docker para el backend (imagen deployada en Render)
- **CI/CD:** GitHub Actions — pipeline de lint → test → build → deploy

---

## 🗂️ Estructura del Repositorio

```
sgiv/
├── .github/
│   └── workflows/
│       ├── frontend.yml          # CI/CD para React → Vercel
│       └── backend.yml           # CI/CD para FastAPI → Render
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── components/
│   │   │   ├── auth/             # Login, ProtectedRoute
│   │   │   ├── common/           # Navbar, Sidebar, Table, Modal
│   │   │   └── reports/          # ReportFilters, DownloadButton
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── ProductsPage.jsx
│   │   │   ├── CustomersPage.jsx
│   │   │   ├── SuppliersPage.jsx
│   │   │   ├── PurchaseOrdersPage.jsx
│   │   │   ├── SalesOrdersPage.jsx
│   │   │   ├── InventoryPage.jsx
│   │   │   └── ReportsPage.jsx
│   │   ├── services/             # axios instances + API calls
│   │   ├── store/                # Zustand global state
│   │   ├── hooks/                # Custom React hooks
│   │   ├── utils/                # formatters, validators
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── .env.example
│   ├── Dockerfile                # Para desarrollo local con Docker Compose
│   ├── vite.config.js
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── products.py
│   │   │   │   ├── customers.py
│   │   │   │   ├── suppliers.py
│   │   │   │   ├── categories.py
│   │   │   │   ├── inventory.py
│   │   │   │   ├── purchase_orders.py
│   │   │   │   ├── sales_orders.py
│   │   │   │   ├── payments.py
│   │   │   │   └── reports.py
│   │   ├── core/
│   │   │   ├── config.py         # Settings con pydantic-settings
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   └── dependencies.py   # FastAPI Depends()
│   │   ├── db/
│   │   │   ├── base.py           # SQLAlchemy Base
│   │   │   ├── session.py        # Async engine + session
│   │   │   └── init_db.py        # Seed inicial
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic schemas (request/response)
│   │   ├── services/             # Business logic
│   │   ├── repositories/         # DB queries
│   │   ├── reports/
│   │   │   ├── pdf_generator.py  # ReportLab
│   │   │   └── excel_generator.py # openpyxl
│   │   └── main.py
│   ├── alembic/                  # Migraciones de DB
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── test_auth.py
│   │   ├── test_products.py
│   │   └── test_reports.py
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── docker-compose.yml            # Para desarrollo local (frontend + backend + postgres local)
├── .gitignore
└── README.md
```

---

## 🗄️ Modelo de Base de Datos (10 Tablas)

```sql
-- 1. roles
CREATE TABLE roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50) UNIQUE NOT NULL,  -- 'admin', 'manager', 'employee'
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 2. users
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    role_id       INTEGER REFERENCES roles(id) ON DELETE SET NULL,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW(),
    updated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 3. categories
CREATE TABLE categories (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- 4. suppliers
CREATE TABLE suppliers (
    id           SERIAL PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(150),
    email        VARCHAR(255),
    phone        VARCHAR(30),
    address      TEXT,
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 5. products
CREATE TABLE products (
    id           SERIAL PRIMARY KEY,
    sku          VARCHAR(50) UNIQUE NOT NULL,
    name         VARCHAR(200) NOT NULL,
    description  TEXT,
    unit_price   NUMERIC(12,2) NOT NULL,
    cost_price   NUMERIC(12,2) NOT NULL,
    category_id  INTEGER REFERENCES categories(id),
    supplier_id  INTEGER REFERENCES suppliers(id),
    unit         VARCHAR(30) DEFAULT 'unit',  -- 'unit', 'kg', 'lt'
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 6. inventory
CREATE TABLE inventory (
    id              SERIAL PRIMARY KEY,
    product_id      INTEGER UNIQUE REFERENCES products(id) ON DELETE CASCADE,
    quantity        INTEGER NOT NULL DEFAULT 0,
    min_stock       INTEGER DEFAULT 5,
    max_stock       INTEGER DEFAULT 500,
    last_updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. customers
CREATE TABLE customers (
    id           SERIAL PRIMARY KEY,
    full_name    VARCHAR(200) NOT NULL,
    email        VARCHAR(255) UNIQUE,
    phone        VARCHAR(30),
    address      TEXT,
    id_number    VARCHAR(30),               -- cédula / RUC
    is_active    BOOLEAN DEFAULT TRUE,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 8. purchase_orders
CREATE TABLE purchase_orders (
    id           SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id  INTEGER REFERENCES suppliers(id),
    user_id      UUID REFERENCES users(id),
    status       VARCHAR(30) DEFAULT 'pending',  -- pending, received, cancelled
    total_amount NUMERIC(14,2) DEFAULT 0,
    notes        TEXT,
    ordered_at   TIMESTAMPTZ DEFAULT NOW(),
    received_at  TIMESTAMPTZ
);

-- 9. purchase_order_details
CREATE TABLE purchase_order_details (
    id                SERIAL PRIMARY KEY,
    purchase_order_id INTEGER REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id        INTEGER REFERENCES products(id),
    quantity          INTEGER NOT NULL,
    unit_cost         NUMERIC(12,2) NOT NULL,
    subtotal          NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED
);

-- 10. sales_orders
CREATE TABLE sales_orders (
    id           SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id  INTEGER REFERENCES customers(id),
    user_id      UUID REFERENCES users(id),
    status       VARCHAR(30) DEFAULT 'pending',  -- pending, completed, cancelled
    total_amount NUMERIC(14,2) DEFAULT 0,
    notes        TEXT,
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 11. sales_order_details
CREATE TABLE sales_order_details (
    id              SERIAL PRIMARY KEY,
    sales_order_id  INTEGER REFERENCES sales_orders(id) ON DELETE CASCADE,
    product_id      INTEGER REFERENCES products(id),
    quantity        INTEGER NOT NULL,
    unit_price      NUMERIC(12,2) NOT NULL,
    subtotal        NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- 12. payments
CREATE TABLE payments (
    id             SERIAL PRIMARY KEY,
    sales_order_id INTEGER REFERENCES sales_orders(id),
    amount         NUMERIC(14,2) NOT NULL,
    method         VARCHAR(30) NOT NULL,  -- cash, card, transfer
    status         VARCHAR(30) DEFAULT 'completed',
    paid_at        TIMESTAMPTZ DEFAULT NOW()
);
```

> **Total: 12 tablas** — todas relacionadas mediante llaves foráneas.

---

## 📊 Reportes

### Reporte 1 — Ventas por Período (PDF + Excel)
- **Descripción:** Listado de todas las órdenes de venta en un rango de fechas, con detalle de productos, cliente, vendedor, subtotales y total general.
- **Filtros:** fecha inicio, fecha fin, estado, cliente
- **Tablas involucradas:** `sales_orders`, `sales_order_details`, `products`, `customers`, `users`
- **Endpoint:** `GET /api/v1/reports/sales?start_date=&end_date=&format=pdf|excel`

### Reporte 2 — Estado de Inventario (PDF + Excel)
- **Descripción:** Listado de productos con su stock actual, stock mínimo, stock máximo, estado (normal/bajo/crítico) y valor total del inventario.
- **Filtros:** categoría, proveedor, estado de stock
- **Tablas involucradas:** `inventory`, `products`, `categories`, `suppliers`
- **Endpoint:** `GET /api/v1/reports/inventory?category_id=&status=&format=pdf|excel`

---

## 🔐 Autenticación

- **Método:** JWT (JSON Web Tokens) con `python-jose` + `passlib[bcrypt]`
- **Flujo:**
  1. `POST /api/v1/auth/login` → recibe `email` + `password` → retorna `access_token` (exp: 8h) + `refresh_token` (exp: 7d)
  2. Frontend guarda tokens en `localStorage` y los adjunta en el header `Authorization: Bearer <token>`
  3. Rutas protegidas usan `Depends(get_current_user)` en FastAPI
- **Roles:**
  - `admin` → acceso completo
  - `manager` → acceso a reportes, sin gestión de usuarios
  - `employee` → solo lectura en inventario y creación de ventas

---

## ⚙️ Variables de Entorno

### Backend (`backend/.env`)
```env
# Base de Datos
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/sgiv_db

# Seguridad JWT
SECRET_KEY=tu_clave_secreta_muy_larga
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# App
APP_ENV=production
ALLOWED_ORIGINS=https://sgiv.vercel.app

# Supabase (opcional para Storage)
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_anon_key
```

### Frontend (`frontend/.env`)
```env
VITE_API_BASE_URL=https://sgiv-api.onrender.com/api/v1
VITE_APP_NAME=SGIV
```

> ⚠️ Nunca commitear archivos `.env`. Usar `.env.example` como plantilla.

---

## 🐳 Docker

### `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### `docker-compose.yml` (desarrollo local)
```yaml
version: "3.9"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: ./backend/.env
    depends_on: [postgres]

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    env_file: ./frontend/.env

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: sgiv_db
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

volumes:
  pgdata:
```

---

## 🚀 CI/CD — GitHub Actions

### `.github/workflows/backend.yml`
```yaml
name: Backend CI/CD

on:
  push:
    branches: [main]
    paths: ["backend/**"]
  pull_request:
    branches: [main]
    paths: ["backend/**"]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ -v
        env:
          DATABASE_URL: ${{ secrets.TEST_DATABASE_URL }}
          SECRET_KEY: test_secret_key

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Render
        run: |
          curl -X POST "${{ secrets.RENDER_DEPLOY_HOOK_URL }}"
```

### `.github/workflows/frontend.yml`
```yaml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths: ["frontend/**"]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: cd frontend && npm ci && npm run build
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
```

### Secrets de GitHub Actions requeridos:
| Secret | Descripción |
|---|---|
| `TEST_DATABASE_URL` | URL de la DB de testing en Supabase |
| `RENDER_DEPLOY_HOOK_URL` | Webhook de deploy de Render |
| `VERCEL_TOKEN` | Token de API de Vercel |
| `VERCEL_ORG_ID` | ID de la organización en Vercel |
| `VERCEL_PROJECT_ID` | ID del proyecto en Vercel |

---

## 🛠️ Stack Tecnológico Completo

| Capa | Tecnología | Versión | Propósito |
|---|---|---|---|
| Frontend | React.js + Vite | 18 / 5 | SPA UI |
| Frontend Styling | TailwindCSS | 3 | Diseño |
| Frontend State | Zustand | 4 | Global state |
| Frontend HTTP | Axios | 1 | API calls |
| Backend | FastAPI | 0.111 | REST API |
| Backend ORM | SQLAlchemy | 2 (async) | DB queries |
| Backend Migrations | Alembic | 1.13 | DB versioning |
| Backend Reports PDF | ReportLab | 4 | Generación PDF |
| Backend Reports Excel | openpyxl | 3.1 | Generación Excel |
| Backend Auth | python-jose + passlib | latest | JWT + hashing |
| Base de Datos | PostgreSQL 15 | — | RDBMS |
| DB Hosting | Supabase | — | Managed Postgres |
| Frontend Hosting | Vercel | — | Static/SSR deploy |
| Backend Hosting | Render | — | Docker container |
| Contenedores | Docker + Compose | 24 / 2.24 | Dev environment |
| CI/CD | GitHub Actions | — | Automatización |
| Control de Versiones | Git + GitHub | — | Source control |

---

## 📐 Convenciones de Código

### Python / FastAPI
- Nombres de funciones y variables: `snake_case`
- Nombres de clases: `PascalCase`
- Schemas Pydantic: sufijo `Create`, `Update`, `Response` (ej: `ProductCreate`)
- Rutas API: siempre en plural y kebab-case (ej: `/purchase-orders`)
- Todo endpoint debe tener `response_model` definido

### React / JavaScript
- Componentes: `PascalCase.jsx`
- Hooks custom: prefijo `use` (ej: `useAuth.js`)
- Servicios API: sufijo `Service` (ej: `productService.js`)
- Variables y funciones: `camelCase`

### Git
- Branches: `feature/nombre-feature`, `fix/nombre-bug`, `hotfix/nombre`
- Commits: Conventional Commits — `feat:`, `fix:`, `docs:`, `chore:`, `test:`
- PRs obligatorios para mergear a `main`; requieren que el CI pase

---

## 🔄 Estrategia de Implementación y Mantenimiento

### Ambientes
| Ambiente | Branch | Frontend URL | Backend URL |
|---|---|---|---|
| Development | `develop` | localhost:5173 | localhost:8000 |
| Staging | `staging` | sgiv-staging.vercel.app | sgiv-api-staging.onrender.com |
| Production | `main` | sgiv.vercel.app | sgiv-api.onrender.com |

### Flujo GitFlow Simplificado
```
feature/* ──┐
             ├──→ develop ──→ staging ──→ main (producción)
fix/*     ──┘
```

### Estrategia de Release
- **Continuous Delivery:** cada merge a `main` dispara deploy automático via GitHub Actions
- **Blue-Green en Render:** Render maneja zero-downtime deploys automáticamente con el nuevo container
- **Rollback:** revertir el merge en GitHub re-dispara el deploy de la versión anterior

### Migraciones de DB
- Siempre usar Alembic: `alembic revision --autogenerate -m "descripcion"`
- Las migraciones corren automáticamente al iniciar el servidor en staging
- En producción, las migraciones se ejecutan manualmente antes del deploy

---

## 🧪 Testing

```bash
# Backend
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing

# Frontend
cd frontend
npm run test        # Vitest unit tests
npm run test:e2e    # Playwright E2E
```

- Cobertura mínima objetivo: **70%** en backend
- Tests de integración para los 2 endpoints de reportes

---

## 🚀 Comandos de Desarrollo Local

```bash
# Clonar y configurar
git clone https://github.com/tu-usuario/sgiv.git
cd sgiv
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Levantar todo con Docker Compose
docker-compose up --build

# Sin Docker — Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Sin Docker — Frontend
cd frontend
npm install
npm run dev
```

---

## 📁 Control de Versiones — Git + GitHub

**Herramienta seleccionada:** **Git** con repositorio en **GitHub**

**Justificación:**
- Integración nativa con GitHub Actions para CI/CD
- Pull Requests con code review antes de mergear a ramas protegidas
- Branch protection rules en `main`: requiere CI verde + 1 aprobación
- Tags de versión semántica (`v1.0.0`, `v1.1.0`) en cada release a producción
- GitHub Issues para tracking de bugs y features

---

*Última actualización: Marzo 2026*