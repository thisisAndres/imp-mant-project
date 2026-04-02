from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.init_db import seed_initial_data
from app.db.session import AsyncSessionLocal

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.categories import router as categories_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.customers import router as customers_router
from app.api.v1.products import router as products_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.purchase_orders import router as purchase_orders_router
from app.api.v1.sales_orders import router as sales_orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.reports import router as reports_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)
    yield


app = FastAPI(
    title="SGIV API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# --- API v1 routers ---
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(categories_router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(suppliers_router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(purchase_orders_router, prefix="/api/v1/purchase-orders", tags=["Purchase Orders"])
app.include_router(sales_orders_router, prefix="/api/v1/sales-orders", tags=["Sales Orders"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
