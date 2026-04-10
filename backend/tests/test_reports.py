"""
Tests for purchase orders, sales orders, payments, and report endpoints.
Covers: app/api/v1/{purchase_orders,sales_orders,payments,reports}.py
        app/services/{purchase_order_service,sales_order_service,order_number_service}.py
        app/repositories/{purchase_order_repo,sales_order_repo,payment_repo,report_repo}.py
        app/reports/{pdf_generator,excel_generator}.py
"""


AUTH = lambda token: {"Authorization": f"Bearer {token}"}  # noqa: E731

PDF_CONTENT_TYPE = "application/pdf"
EXCEL_CONTENT_TYPE = (
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)


# ── Purchase Orders ───────────────────────────────────────────────────────────

async def test_list_purchase_orders_empty(client, admin_token):
    resp = await client.get("/api/v1/purchase-orders/", headers=AUTH(admin_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_list_purchase_orders_forbidden_employee(client, employee_token):
    resp = await client.get("/api/v1/purchase-orders/", headers=AUTH(employee_token))
    assert resp.status_code == 403


async def test_create_purchase_order(client, admin_token, test_product):
    resp = await client.post(
        "/api/v1/purchase-orders/",
        json={
            "details": [
                {"product_id": test_product["id"], "quantity": 10, "unit_cost": "5.00"}
            ]
        },
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["order_number"].startswith("PO-")
    assert len(data["details"]) == 1


async def test_get_purchase_order_by_id(client, admin_token, test_product):
    create_resp = await client.post(
        "/api/v1/purchase-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 5, "unit_cost": "3.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.get(f"/api/v1/purchase-orders/{order_id}", headers=AUTH(admin_token))
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


async def test_get_purchase_order_not_found(client, admin_token):
    resp = await client.get("/api/v1/purchase-orders/99999", headers=AUTH(admin_token))
    assert resp.status_code == 404


async def test_cancel_purchase_order(client, admin_token, test_product):
    create_resp = await client.post(
        "/api/v1/purchase-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 2, "unit_cost": "1.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/purchase-orders/{order_id}", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_receive_purchase_order(client, admin_token, test_product):
    create_resp = await client.post(
        "/api/v1/purchase-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 20, "unit_cost": "4.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/purchase-orders/{order_id}/status",
        json={"status": "received"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "received"
    assert data["received_at"] is not None


async def test_invalid_purchase_order_transition(client, admin_token, test_product):
    """Transitioning a received order back to pending must fail."""
    create_resp = await client.post(
        "/api/v1/purchase-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_cost": "1.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]
    # First receive it
    await client.put(
        f"/api/v1/purchase-orders/{order_id}/status",
        json={"status": "received"},
        headers=AUTH(admin_token),
    )
    # Attempt to cancel an already-received order
    resp = await client.put(
        f"/api/v1/purchase-orders/{order_id}/status",
        json={"status": "cancelled"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 400


# ── Sales Orders ──────────────────────────────────────────────────────────────

async def test_list_sales_orders_empty(client, employee_token):
    resp = await client.get("/api/v1/sales-orders/", headers=AUTH(employee_token))
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_sales_order(client, employee_token, test_product):
    resp = await client.post(
        "/api/v1/sales-orders/",
        json={
            "details": [
                {"product_id": test_product["id"], "quantity": 1, "unit_price": "10.00"}
            ]
        },
        headers=AUTH(employee_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["order_number"].startswith("SO-")
    assert len(data["details"]) == 1


async def test_get_sales_order_by_id(client, employee_token, test_product):
    create_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "9.99"}]},
        headers=AUTH(employee_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/sales-orders/{order_id}", headers=AUTH(employee_token)
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == order_id


async def test_get_sales_order_not_found(client, employee_token):
    resp = await client.get("/api/v1/sales-orders/99999", headers=AUTH(employee_token))
    assert resp.status_code == 404


async def test_cancel_sales_order(client, admin_token, test_product):
    create_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "8.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.delete(
        f"/api/v1/sales-orders/{order_id}", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


async def test_complete_sales_order_insufficient_stock(client, admin_token, test_product):
    """Completing an order when inventory is missing must return 400."""
    # test_product has no inventory record → get_by_product returns None → 400
    create_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "10.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/sales-orders/{order_id}/status",
        json={"status": "completed"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 400


async def test_complete_sales_order_success(client, admin_token, test_product_with_inventory):
    """Completing an order with sufficient stock decrements inventory."""
    pid = test_product_with_inventory["id"]
    create_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": pid, "quantity": 5, "unit_price": "20.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/sales-orders/{order_id}/status",
        json={"status": "completed"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"

    # Inventory should be 100 - 5 = 95
    inv_resp = await client.get(
        f"/api/v1/inventory/{pid}", headers=AUTH(admin_token)
    )
    assert inv_resp.json()["quantity"] == 95


async def test_list_sales_orders_with_date_filter(client, employee_token, test_product):
    await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "5.00"}]},
        headers=AUTH(employee_token),
    )
    resp = await client.get(
        "/api/v1/sales-orders/?start_date=2020-01-01T00:00:00",
        headers=AUTH(employee_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_invalid_sales_order_status_filter(client, employee_token):
    resp = await client.get(
        "/api/v1/sales-orders/?status_filter=invalid",
        headers=AUTH(employee_token),
    )
    assert resp.status_code == 422


# ── Payments ──────────────────────────────────────────────────────────────────

async def test_create_payment(client, admin_token, test_product):
    # Create a sales order first
    order_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "10.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = order_resp.json()["id"]

    resp = await client.post(
        "/api/v1/payments/",
        json={"sales_order_id": order_id, "amount": "10.00", "method": "cash"},
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["method"] == "cash"
    assert data["status"] == "completed"


async def test_list_payments(client, admin_token, test_product):
    order_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "10.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = order_resp.json()["id"]
    await client.post(
        "/api/v1/payments/",
        json={"sales_order_id": order_id, "amount": "10.00", "method": "card"},
        headers=AUTH(admin_token),
    )

    resp = await client.get("/api/v1/payments/", headers=AUTH(admin_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


async def test_list_payments_filter_by_order(client, admin_token, test_product):
    order_resp = await client.post(
        "/api/v1/sales-orders/",
        json={"details": [{"product_id": test_product["id"], "quantity": 1, "unit_price": "10.00"}]},
        headers=AUTH(admin_token),
    )
    order_id = order_resp.json()["id"]
    await client.post(
        "/api/v1/payments/",
        json={"sales_order_id": order_id, "amount": "10.00", "method": "transfer"},
        headers=AUTH(admin_token),
    )

    resp = await client.get(
        f"/api/v1/payments/?sales_order_id={order_id}",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert all(p["sales_order_id"] == order_id for p in resp.json())


# ── Reports ───────────────────────────────────────────────────────────────────

async def test_sales_report_pdf(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/sales?format=pdf", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert PDF_CONTENT_TYPE in resp.headers["content-type"]
    assert len(resp.content) > 0


async def test_sales_report_excel(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/sales?format=excel", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert EXCEL_CONTENT_TYPE in resp.headers["content-type"]
    assert len(resp.content) > 0


async def test_inventory_report_pdf(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/inventory?format=pdf", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert PDF_CONTENT_TYPE in resp.headers["content-type"]
    assert len(resp.content) > 0


async def test_inventory_report_excel(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/inventory?format=excel", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert EXCEL_CONTENT_TYPE in resp.headers["content-type"]
    assert len(resp.content) > 0


async def test_reports_forbidden_as_employee(client, employee_token):
    for url in ["/api/v1/reports/sales", "/api/v1/reports/inventory"]:
        resp = await client.get(url, headers=AUTH(employee_token))
        assert resp.status_code == 403


async def test_sales_report_invalid_status(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/sales?status=invalid", headers=AUTH(admin_token)
    )
    assert resp.status_code == 422


async def test_inventory_report_invalid_status(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/inventory?status=invalid", headers=AUTH(admin_token)
    )
    assert resp.status_code == 422


async def test_sales_report_with_date_filters(client, admin_token):
    resp = await client.get(
        "/api/v1/reports/sales?start_date=2020-01-01T00:00:00&end_date=2099-12-31T23:59:59&format=pdf",
        headers=AUTH(admin_token),
    )
    assert resp.status_code == 200
    assert PDF_CONTENT_TYPE in resp.headers["content-type"]


async def test_inventory_report_with_data(client, admin_token, test_product_with_inventory):
    """Report generation works correctly when inventory data exists."""
    resp = await client.get(
        "/api/v1/reports/inventory?format=excel", headers=AUTH(admin_token)
    )
    assert resp.status_code == 200
    assert EXCEL_CONTENT_TYPE in resp.headers["content-type"]
    # Excel files start with the PK ZIP magic bytes
    assert resp.content[:4] == b"PK\x03\x04"
