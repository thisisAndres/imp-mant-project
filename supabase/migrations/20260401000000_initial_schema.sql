-- ============================================================
-- SGIV — Initial Schema Migration
-- Generated from SQLAlchemy models
-- ============================================================

-- 1. roles
CREATE TABLE IF NOT EXISTS roles (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(50)  UNIQUE NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 2. users
CREATE TABLE IF NOT EXISTS users (
    id            UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    email         VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(150) NOT NULL,
    role_id       INTEGER      REFERENCES roles(id) ON DELETE SET NULL,
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 3. categories
CREATE TABLE IF NOT EXISTS categories (
    id          SERIAL       PRIMARY KEY,
    name        VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 4. suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id           SERIAL       PRIMARY KEY,
    company_name VARCHAR(200) NOT NULL,
    contact_name VARCHAR(150),
    email        VARCHAR(255),
    phone        VARCHAR(30),
    address      TEXT,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 5. products
CREATE TABLE IF NOT EXISTS products (
    id           SERIAL       PRIMARY KEY,
    sku          VARCHAR(50)  UNIQUE NOT NULL,
    name         VARCHAR(200) NOT NULL,
    description  TEXT,
    unit_price   NUMERIC(12,2) NOT NULL,
    cost_price   NUMERIC(12,2) NOT NULL,
    category_id  INTEGER      REFERENCES categories(id),
    supplier_id  INTEGER      REFERENCES suppliers(id),
    unit         VARCHAR(30)  NOT NULL DEFAULT 'unit',
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 6. inventory
CREATE TABLE IF NOT EXISTS inventory (
    id              SERIAL  PRIMARY KEY,
    product_id      INTEGER UNIQUE NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    quantity        INTEGER NOT NULL DEFAULT 0,
    min_stock       INTEGER NOT NULL DEFAULT 5,
    max_stock       INTEGER NOT NULL DEFAULT 500,
    last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 7. customers
CREATE TABLE IF NOT EXISTS customers (
    id        SERIAL       PRIMARY KEY,
    full_name VARCHAR(200) NOT NULL,
    email     VARCHAR(255) UNIQUE,
    phone     VARCHAR(30),
    address   TEXT,
    id_number VARCHAR(30),
    is_active BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 8. purchase_orders
CREATE TABLE IF NOT EXISTS purchase_orders (
    id           SERIAL       PRIMARY KEY,
    order_number VARCHAR(50)  UNIQUE NOT NULL,
    supplier_id  INTEGER      REFERENCES suppliers(id),
    user_id      UUID         REFERENCES users(id),
    status       VARCHAR(30)  NOT NULL DEFAULT 'pending',
    total_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    notes        TEXT,
    ordered_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    received_at  TIMESTAMPTZ
);

-- 9. purchase_order_details
CREATE TABLE IF NOT EXISTS purchase_order_details (
    id                SERIAL        PRIMARY KEY,
    purchase_order_id INTEGER       NOT NULL REFERENCES purchase_orders(id) ON DELETE CASCADE,
    product_id        INTEGER       REFERENCES products(id),
    quantity          INTEGER       NOT NULL,
    unit_cost         NUMERIC(12,2) NOT NULL,
    subtotal          NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_cost) STORED
);

-- 10. sales_orders
CREATE TABLE IF NOT EXISTS sales_orders (
    id           SERIAL        PRIMARY KEY,
    order_number VARCHAR(50)   UNIQUE NOT NULL,
    customer_id  INTEGER       REFERENCES customers(id),
    user_id      UUID          REFERENCES users(id),
    status       VARCHAR(30)   NOT NULL DEFAULT 'pending',
    total_amount NUMERIC(14,2) NOT NULL DEFAULT 0,
    notes        TEXT,
    created_at   TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- 11. sales_order_details
CREATE TABLE IF NOT EXISTS sales_order_details (
    id             SERIAL        PRIMARY KEY,
    sales_order_id INTEGER       NOT NULL REFERENCES sales_orders(id) ON DELETE CASCADE,
    product_id     INTEGER       REFERENCES products(id),
    quantity       INTEGER       NOT NULL,
    unit_price     NUMERIC(12,2) NOT NULL,
    subtotal       NUMERIC(14,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- 12. payments
CREATE TABLE IF NOT EXISTS payments (
    id             SERIAL        PRIMARY KEY,
    sales_order_id INTEGER       REFERENCES sales_orders(id),
    amount         NUMERIC(14,2) NOT NULL,
    method         VARCHAR(30)   NOT NULL,
    status         VARCHAR(30)   NOT NULL DEFAULT 'completed',
    paid_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

-- ============================================================
-- Indexes for common query patterns
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_products_category  ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_supplier  ON products(supplier_id);
CREATE INDEX IF NOT EXISTS idx_inventory_quantity ON inventory(quantity);
CREATE INDEX IF NOT EXISTS idx_po_status          ON purchase_orders(status);
CREATE INDEX IF NOT EXISTS idx_po_supplier        ON purchase_orders(supplier_id);
CREATE INDEX IF NOT EXISTS idx_so_status          ON sales_orders(status);
CREATE INDEX IF NOT EXISTS idx_so_customer        ON sales_orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_so_created_at      ON sales_orders(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_order     ON payments(sales_order_id);
