"""
Shared pytest fixtures for SGIV backend tests.

Key design
----------
The root cause of "Future attached to a different loop" errors in async
SQLAlchemy + asyncpg is that connection pools bind asyncpg connections to the
event loop they were created on.  pytest-asyncio 0.23.x gives every test its
own function-scoped event loop by default, so pooled connections from a
previous test cannot be reused.

The canonical fix (recommended in SQLAlchemy's own async docs) is NullPool:
every DB call gets a brand-new asyncpg connection on the *current* event loop
and discards it immediately after use.  No pooling = no loop-binding issues.

We also patch the production engine/session-factory *before* importing app.main
so that the FastAPI lifespan and every get_db() call also use NullPool.
No event_loop fixture override, no deprecated hacks.
"""

import os
from pathlib import Path

import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

_env_test = Path(__file__).parent.parent / ".env.test"
_env_default = Path(__file__).parent.parent / ".env"
load_dotenv(_env_test if _env_test.exists() else _env_default)

# ── Test DB URL ───────────────────────────────────────────────────────────────

_RAW_URL = os.environ["DATABASE_URL"]
TEST_DB_URL = (
    _RAW_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    if _RAW_URL.startswith("postgresql://")
    else _RAW_URL
)

# ── Patch production engine with NullPool BEFORE importing the app ────────────
# This must happen before `from app.main import app` so the lifespan and every
# get_db() call use the patched engine (NullPool, no loop-binding).

import app.db.session as _db_module  # noqa: E402

_test_engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)
_test_sf = async_sessionmaker(_test_engine, class_=AsyncSession, expire_on_commit=False)

_db_module.engine = _test_engine
_db_module.AsyncSessionLocal = _test_sf

# ── Now it is safe to import the rest of the app ─────────────────────────────

from app.core.security import hash_password  # noqa: E402
from app.db.init_db import seed_initial_data  # noqa: E402
from app.main import app  # noqa: E402
from app.models.role import Role  # noqa: E402
from app.models.user import User  # noqa: E402

# ── Truncate SQL (roles are intentionally excluded — they are static seed data) ─

_TRUNCATE_SQL = text("""
    TRUNCATE TABLE
        payments,
        sales_order_details, sales_orders,
        purchase_order_details, purchase_orders,
        inventory, products,
        customers, suppliers, categories,
        users
    RESTART IDENTITY CASCADE
""")


# ── One-time schema creation ──────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables():
    """Create all tables once before the test session (idempotent via checkfirst)."""
    import app.models  # noqa: F401 — registers all models with Base.metadata
    from app.db.base import Base

    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
    yield
    # Tables are intentionally left intact after the session for inspection.


# ── Per-test cleanup ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    """Seed roles (idempotent) then truncate all business tables before each test."""
    async with _test_sf() as session:
        await seed_initial_data(session)
    async with _test_engine.begin() as conn:
        await conn.execute(_TRUNCATE_SQL)
    yield


# ── HTTP test client ──────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def client(clean_db):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── DB helper (importable in test modules) ────────────────────────────────────

async def create_user_in_db(email: str, password: str, role_name: str) -> User:
    """Insert a user directly into the DB without going through the HTTP API."""
    from sqlalchemy import select

    async with _test_sf() as session:
        role = (
            await session.execute(select(Role).where(Role.name == role_name))
        ).scalar_one()
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=f"Test {role_name.title()}",
            role_id=role.id,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


# ── Token fixtures ────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def admin_token(client):
    await create_user_in_db("admin@example.com", "TestAdmin1!", "admin")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "admin@example.com", "password": "TestAdmin1!"},
    )
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def manager_token(client):
    await create_user_in_db("manager@example.com", "TestManager1!", "manager")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "manager@example.com", "password": "TestManager1!"},
    )
    return resp.json()["access_token"]


@pytest_asyncio.fixture
async def employee_token(client):
    await create_user_in_db("employee@example.com", "TestEmployee1!", "employee")
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "employee@example.com", "password": "TestEmployee1!"},
    )
    return resp.json()["access_token"]


# ── Data fixtures ─────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def test_category(admin_token, client):
    resp = await client.post(
        "/api/v1/categories/",
        json={"name": "Test Category"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    return resp.json()


@pytest_asyncio.fixture
async def test_supplier(admin_token, client):
    resp = await client.post(
        "/api/v1/suppliers/",
        json={"company_name": "Test Supplier Co"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    return resp.json()


@pytest_asyncio.fixture
async def test_customer(admin_token, client):
    resp = await client.post(
        "/api/v1/customers/",
        json={"full_name": "Test Customer", "email": "customer@example.com"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    return resp.json()


@pytest_asyncio.fixture
async def test_product(admin_token, client, test_category, test_supplier):
    resp = await client.post(
        "/api/v1/products/",
        json={
            "sku": "TEST-001",
            "name": "Test Product",
            "unit_price": "10.00",
            "cost_price": "5.00",
            "category_id": test_category["id"],
            "supplier_id": test_supplier["id"],
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    return resp.json()


@pytest_asyncio.fixture
async def test_product_with_inventory(admin_token, client, test_category, test_supplier):
    """Creates a product and seeds an inventory record with 100 units."""
    resp = await client.post(
        "/api/v1/products/",
        json={
            "sku": "INV-001",
            "name": "Stocked Product",
            "unit_price": "20.00",
            "cost_price": "10.00",
            "category_id": test_category["id"],
            "supplier_id": test_supplier["id"],
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    product = resp.json()

    # No POST /inventory endpoint exists — seed the record directly
    from app.repositories import inventory_repo

    async with _test_sf() as session:
        await inventory_repo.create_inventory(session, product["id"], quantity=100)

    return product
