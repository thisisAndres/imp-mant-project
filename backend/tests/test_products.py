"""
Tests for categories, suppliers, customers, products, and inventory endpoints.
Covers: app/api/v1/{categories,suppliers,customers,products,inventory}.py
        and their repositories + inventory_service.
"""


AUTH = lambda token: {"Authorization": f"Bearer {token}"}  # noqa: E731


# ── Categories ────────────────────────────────────────────────────────────────

async def test_list_categories_empty(client, admin_token):
    resp = await client.get("/api/v1/categories/", headers=AUTH(admin_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_category_as_admin(client, admin_token):
    resp = await client.post(
        "/api/v1/categories/",
        json={"name": "Electronics", "description": "Electronic goods"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Electronics"
    assert "id" in data


async def test_create_category_as_employee_forbidden(client, employee_token):
    resp = await client.post(
        "/api/v1/categories/",
        json={"name": "Electronics"},
        headers=AUTH(employee_token),
    )
    assert resp.status_code == 403


async def test_get_category_by_id(client, admin_token, test_category):
    resp = await client.get(
        f"/api/v1/categories/{test_category['id']}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == test_category["id"]


async def test_get_category_not_found(client, admin_token):
    resp = await client.get("/api/v1/categories/99999", headers=AUTH(admin_token))
    assert resp.status_code == 404


async def test_update_category(client, admin_token, test_category):
    resp = await client.put(
        f"/api/v1/categories/{test_category['id']}",
        json={"name": "Updated Category"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Category"


async def test_delete_category(client, admin_token, test_category):
    resp = await client.delete(
        f"/api/v1/categories/{test_category['id']}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 204

    # Confirm it's gone
    resp = await client.get(
        f"/api/v1/categories/{test_category['id']}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 404


# ── Suppliers ─────────────────────────────────────────────────────────────────

async def test_list_suppliers_empty(client, admin_token):
    resp = await client.get("/api/v1/suppliers/", headers=AUTH(admin_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_supplier(client, admin_token):
    resp = await client.post(
        "/api/v1/suppliers/",
        json={
            "company_name": "ACME Corp",
            "contact_name": "Wile E. Coyote",
            "email": "contact@acme.com",
        },
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 201
    assert resp.json()["company_name"] == "ACME Corp"


async def test_update_supplier(client, admin_token, test_supplier):
    resp = await client.put(
        f"/api/v1/suppliers/{test_supplier['id']}",
        json={"company_name": "Updated Supplier"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["company_name"] == "Updated Supplier"


async def test_deactivate_supplier(client, admin_token, test_supplier):
    resp = await client.delete(
        f"/api/v1/suppliers/{test_supplier['id']}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


# ── Customers ─────────────────────────────────────────────────────────────────

async def test_list_customers_empty(client, admin_token):
    resp = await client.get("/api/v1/customers/", headers=AUTH(admin_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_customer(client, admin_token):
    resp = await client.post(
        "/api/v1/customers/",
        json={"full_name": "Jane Doe", "email": "jane@example.com", "phone": "555-1234"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["full_name"] == "Jane Doe"
    assert data["is_active"] is True


async def test_update_customer(client, admin_token, test_customer):
    resp = await client.put(
        f"/api/v1/customers/{test_customer['id']}",
        json={"full_name": "Updated Customer"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Updated Customer"


async def test_deactivate_customer(client, admin_token, test_customer):
    resp = await client.delete(
        f"/api/v1/customers/{test_customer['id']}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


# ── Products ──────────────────────────────────────────────────────────────────

async def test_list_products_empty(client, employee_token):
    resp = await client.get("/api/v1/products/", headers=AUTH(employee_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_product_as_admin(client, admin_token):
    resp = await client.post(
        "/api/v1/products/",
        json={
            "sku": "PROD-001",
            "name": "Widget",
            "unit_price": "9.99",
            "cost_price": "4.99",
            "unit": "unit",
        },
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["sku"] == "PROD-001"
    assert data["is_active"] is True


async def test_create_product_as_manager(client, manager_token):
    resp = await client.post(
        "/api/v1/products/",
        json={"sku": "PROD-MGR", "name": "Manager Product", "unit_price": "5.00", "cost_price": "2.00"},
        headers=AUTH(manager_token),
    )
    assert resp.status_code == 201


async def test_create_product_as_employee_forbidden(client, employee_token):
    resp = await client.post(
        "/api/v1/products/",
        json={"sku": "PROD-EMP", "name": "Employee Product", "unit_price": "5.00", "cost_price": "2.00"},
        headers=AUTH(employee_token),
    )
    assert resp.status_code == 403


async def test_create_product_invalid_unit(client, admin_token):
    resp = await client.post(
        "/api/v1/products/",
        json={"sku": "PROD-BAD", "name": "Bad Unit", "unit_price": "5.00", "cost_price": "2.00", "unit": "gallon"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 422


async def test_get_product_by_id(client, employee_token, test_product):
    resp = await client.get(
        f"/api/v1/products/{test_product['id']}",
        headers=AUTH(employee_token),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == test_product["id"]


async def test_get_product_not_found(client, employee_token):
    resp = await client.get("/api/v1/products/99999", headers=AUTH(employee_token))
    assert resp.status_code == 404


async def test_update_product(client, admin_token, test_product):
    resp = await client.put(
        f"/api/v1/products/{test_product['id']}",
        json={"name": "Updated Product Name", "unit_price": "12.50"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Product Name"


async def test_deactivate_product(client, admin_token, test_product):
    resp = await client.delete(
        f"/api/v1/products/{test_product['id']}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_list_products_filter_active(client, admin_token, test_product):
    # Deactivate the product
    await client.delete(
        f"/api/v1/products/{test_product['id']}",
        headers=AUTH(admin_token),
    )

    # Filter active only — should be empty
    resp = await client.get(
        "/api/v1/products/?is_active=true",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert all(p["is_active"] for p in resp.json())

    # Filter inactive — should include our deactivated product
    resp = await client.get(
        "/api/v1/products/?is_active=false",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert any(p["id"] == test_product["id"] for p in resp.json())


# ── Inventory ─────────────────────────────────────────────────────────────────

async def test_list_inventory_empty(client, employee_token):
    resp = await client.get("/api/v1/inventory/", headers=AUTH(employee_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_inventory_with_data(client, employee_token, test_product_with_inventory):
    resp = await client.get("/api/v1/inventory/", headers=AUTH(employee_token))
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["product_id"] == test_product_with_inventory["id"]
    assert items[0]["quantity"] == 100
    assert items[0]["stock_status"] == "normal"


async def test_get_inventory_by_product(client, employee_token, test_product_with_inventory):
    pid = test_product_with_inventory["id"]
    resp = await client.get(f"/api/v1/inventory/{pid}", headers=AUTH(employee_token))
    assert resp.status_code == 200
    assert resp.json()["product_id"] == pid


async def test_get_inventory_not_found(client, employee_token):
    resp = await client.get("/api/v1/inventory/99999", headers=AUTH(employee_token))
    assert resp.status_code == 404


async def test_update_inventory(client, admin_token, test_product_with_inventory):
    pid = test_product_with_inventory["id"]
    resp = await client.put(
        f"/api/v1/inventory/{pid}",
        json={"quantity": 3, "min_stock": 5, "max_stock": 200},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["quantity"] == 3
    # quantity 3 <= min_stock 5 → "low"
    assert data["stock_status"] == "low"


async def test_update_inventory_critical_status(client, admin_token, test_product_with_inventory):
    pid = test_product_with_inventory["id"]
    resp = await client.put(
        f"/api/v1/inventory/{pid}",
        json={"quantity": 0, "min_stock": 5, "max_stock": 200},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["stock_status"] == "critical"


async def test_update_inventory_not_found(client, admin_token):
    resp = await client.put(
        "/api/v1/inventory/99999",
        json={"quantity": 10, "min_stock": 5, "max_stock": 100},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 404
