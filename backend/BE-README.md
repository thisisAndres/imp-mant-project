# SGIV — Sistema de Gestión de Inventario y Ventas

Full-stack inventory and sales management system for SMEs.

**Stack:** React + Vite (frontend) · FastAPI + PostgreSQL (backend) · Supabase (DB) · Render (API) · Vercel (UI)

---

## Running the Backend Locally

### Prerequisites
- Python 3.11+
- A Supabase project with the schema already applied

### Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

Create `backend/.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres.<ref>:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?ssl=require
SECRET_KEY=<random-string-at-least-32-chars>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_ENV=development
ALLOWED_ORIGINS=http://localhost:5173
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=YourStr0ng!Pass
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API runs at `http://127.0.0.1:8000`. On first startup the server seeds the 3 roles and the admin user automatically.

---

## API Testing Guide (Postman)

Import `SGIV.postman_collection.json` into Postman — the collection already has all endpoints, sample bodies, and an auto-save token script on Login.

Follow the steps below in order. Each step depends on data created in the previous one.

---

### Step 1 — Authenticate

**POST** `Auth / Login`

```json
{
    "email": "admin@yourdomain.com",
    "password": "YourStr0ng!Pass"
}
```

Expected: `200 OK` with `access_token` and `refresh_token`.
The collection script saves both tokens automatically — all following requests are authenticated.

---

### Step 2 — Create a Category

**POST** `Categories / Create Category`

```json
{
    "name": "Electronics",
    "description": "Electronic devices and accessories"
}
```

Expected: `201 Created`. Note the returned `id` (e.g. `1`).

---

### Step 3 — Create a Supplier

**POST** `Suppliers / Create Supplier`

```json
{
    "company_name": "TechCorp S.A.",
    "contact_name": "Ana García",
    "email": "ana@techcorp.com",
    "phone": "+1-555-0100",
    "address": "123 Main St, New York"
}
```

Expected: `201 Created`. Note the returned `id` (e.g. `1`).

---

### Step 4 — Create a Product

**POST** `Products / Create Product`

```json
{
    "sku": "PROD-001",
    "name": "Laptop Pro 15",
    "description": "High performance laptop",
    "unit_price": 1299.99,
    "cost_price": 950.00,
    "category_id": 1,
    "supplier_id": 1,
    "unit": "unit"
}
```

Expected: `201 Created`. Note the returned `id` (e.g. `1`).

---

### Step 5 — Stock the Inventory

**PUT** `Inventory / Update Inventory` — path param `product_id = 1`

```json
{
    "quantity": 50,
    "min_stock": 5,
    "max_stock": 200
}
```

Expected: `200 OK` with `stock_status: "normal"`.

---

### Step 6 — Create a Customer

**POST** `Customers / Create Customer`

```json
{
    "full_name": "María Rodríguez",
    "email": "maria@example.com",
    "phone": "+1-555-0200",
    "address": "456 Oak Ave",
    "id_number": "1234567890"
}
```

Expected: `201 Created`. Note the returned `id` (e.g. `1`).

---

### Step 7 — Create a Purchase Order

**POST** `Purchase Orders / Create Purchase Order`

```json
{
    "supplier_id": 1,
    "notes": "Initial restock",
    "details": [
        {
            "product_id": 1,
            "quantity": 20,
            "unit_cost": 950.00
        }
    ]
}
```

Expected: `201 Created` with `status: "pending"`. Note the returned `id` (e.g. `1`).

---

### Step 8 — Receive the Purchase Order

**PUT** `Purchase Orders / Update Status` — path param `order_id = 1`

```json
{
    "status": "received"
}
```

Expected: `200 OK` with `status: "received"`.
Inventory for product 1 increases by 20 automatically.

---

### Step 9 — Verify Inventory Increased

**GET** `Inventory / Get Inventory by Product` — path param `product_id = 1`

Expected: `200 OK` with `quantity: 70` (50 from step 5 + 20 from step 8).

---

### Step 10 — Create a Sales Order

**POST** `Sales Orders / Create Sales Order`

```json
{
    "customer_id": 1,
    "notes": "First sale",
    "details": [
        {
            "product_id": 1,
            "quantity": 3,
            "unit_price": 1299.99
        }
    ]
}
```

Expected: `201 Created` with `status: "pending"`. Note the returned `id` (e.g. `1`).

---

### Step 11 — Complete the Sale

**PUT** `Sales Orders / Update Status` — path param `order_id = 1`

```json
{
    "status": "completed"
}
```

Expected: `200 OK` with `status: "completed"`.
Inventory for product 1 decreases by 3 automatically.

---

### Step 12 — Register a Payment

**POST** `Payments / Create Payment`

```json
{
    "sales_order_id": 1,
    "amount": 3899.97,
    "method": "card"
}
```

Expected: `201 Created` with `status: "completed"`.

---

### Step 13 — Download Reports

**Sales Report PDF**
`GET Reports / Sales Report — PDF`
Enable the `start_date` and `end_date` query params to filter by date range.

**Sales Report Excel**
`GET Reports / Sales Report — Excel`

**Inventory Report PDF**
`GET Reports / Inventory Report — PDF`
Enable the `status` param and set it to `normal`, `low`, or `critical` to filter by stock level.

**Inventory Report Excel**
`GET Reports / Inventory Report — Excel`

> In Postman, click **Send and Download** instead of Send to save the file to disk.

---

### Additional Endpoints to Validate

| Action | Endpoint | What to verify |
|---|---|---|
| List all products | `GET /api/v1/products/` | Returns array |
| List all orders | `GET /api/v1/sales-orders/` | Returns array |
| Cancel a pending order | `DELETE /api/v1/sales-orders/1` | Returns `status: cancelled` |
| Refresh token | `POST /api/v1/auth/refresh` | Returns new `access_token` |
| List users (admin only) | `GET /api/v1/users/` | Returns user list |
| Create a manager user | `POST /api/v1/users/` with `role_id: 2` | Returns new user |

---

### Error Cases Worth Testing

| Case | How to trigger | Expected |
|---|---|---|
| Wrong password | Login with bad password | `401 Unauthorized` |
| Missing token | Remove `Authorization` header | `403 Forbidden` |
| Insufficient stock | Complete a sale for qty > available stock | `400 Bad Request` |
| Invalid status value | `status_filter=invalid` on list endpoint | `422 Unprocessable Entity` |
| Duplicate SKU | Create two products with the same SKU | `400 Bad Request` |
| Employee accessing users | Login as employee, hit `GET /api/v1/users/` | `403 Forbidden` |
| Invalid order transition | Set a completed order back to pending | `400 Bad Request` |

---

## Project Structure

```
sgiv/
├── backend/                        # FastAPI application
│   ├── app/
│   │   ├── api/v1/                 # Route handlers
│   │   ├── core/                   # Config, security, dependencies
│   │   ├── db/                     # Session, base, seed
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   ├── repositories/           # DB queries
│   │   ├── reports/                # PDF and Excel generators
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── services/               # Business logic
│   │   └── main.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                       # React + Vite (in progress)
├── supabase/migrations/            # Database schema
├── .github/workflows/              # CI/CD pipelines
├── docker-compose.yml
└── SGIV.postman_collection.json    # Postman collection
```

---

## Deployment

| Environment | Branch | Frontend | Backend |
|---|---|---|---|
| Development | `develop` | localhost:5173 | localhost:8000 |
| Production | `main` | Vercel | Render |

Merging to `main` triggers automatic deploy via GitHub Actions → Render (backend) and Vercel (frontend).
