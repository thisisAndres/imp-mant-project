# Mock Data — SGIV

Use this data to manually test the API via Postman or Swagger.
All requests require a Bearer token except login.

---

## 1. Login

**POST** `/api/v1/auth/login`

```json
{
  "email": "p-adming@proyecto.com",
  "password": "d2J5Bxz2nM3agQ"
}
```

Save the `access_token` from the response — you'll need it for all other requests.

---

## 2. Categories

**POST** `/api/v1/categories/`

```json
{ "name": "Electronics", "description": "Electronic devices and accessories" }
```
```json
{ "name": "Office", "description": "Office supplies and furniture" }
```
```json
{ "name": "Cleaning", "description": "Cleaning products and supplies" }
```

---

## 3. Suppliers

**POST** `/api/v1/suppliers/`

```json
{ "company_name": "TechDist S.A.", "contact_name": "Carlos Méndez", "email": "carlos@techdist.com", "phone": "555-1001" }
```
```json
{ "company_name": "OfiSupplies Ltda.", "contact_name": "Ana Rodríguez", "email": "ana@ofisupplies.com", "phone": "555-1002" }
```
```json
{ "company_name": "CleanPro Corp.", "contact_name": "Luis Herrera", "email": "luis@cleanpro.com", "phone": "555-1003" }
```

---

## 4. Customers

**POST** `/api/v1/customers/`

```json
{ "full_name": "María García", "email": "maria@email.com", "phone": "555-2001", "id_number": "0101010101" }
```
```json
{ "full_name": "Pedro Jiménez", "email": "pedro@email.com", "phone": "555-2002", "id_number": "0202020202" }
```
```json
{ "full_name": "Lucía Vargas", "email": "lucia@email.com", "phone": "555-2003", "id_number": "0303030303" }
```
```json
{ "full_name": "Empresa XYZ", "email": "compras@xyz.com", "phone": "555-2004", "id_number": "1234567890001" }
```

---

## 5. Products

**POST** `/api/v1/products/`

> Replace `category_id` and `supplier_id` with the IDs returned in steps 2 and 3.

```json
{ "sku": "ELEC-001", "name": "Laptop 15\"", "unit_price": "899.99", "cost_price": "650.00", "unit": "unit", "category_id": <electronics_id>, "supplier_id": <techdist_id> }
```
```json
{ "sku": "ELEC-002", "name": "Wireless Mouse", "unit_price": "29.99", "cost_price": "12.00", "unit": "unit", "category_id": <electronics_id>, "supplier_id": <techdist_id> }
```
```json
{ "sku": "ELEC-003", "name": "USB-C Hub 7-in-1", "unit_price": "49.99", "cost_price": "22.00", "unit": "unit", "category_id": <electronics_id>, "supplier_id": <techdist_id> }
```
```json
{ "sku": "OFFI-001", "name": "Office Chair", "unit_price": "199.99", "cost_price": "110.00", "unit": "unit", "category_id": <office_id>, "supplier_id": <ofisupplies_id> }
```
```json
{ "sku": "OFFI-002", "name": "A4 Paper Ream 500pcs", "unit_price": "5.99", "cost_price": "3.00", "unit": "unit", "category_id": <office_id>, "supplier_id": <ofisupplies_id> }
```
```json
{ "sku": "OFFI-003", "name": "Ballpoint Pens 12pk", "unit_price": "4.49", "cost_price": "1.80", "unit": "unit", "category_id": <office_id>, "supplier_id": <ofisupplies_id> }
```
```json
{ "sku": "CLEA-001", "name": "Floor Cleaner 1L", "unit_price": "3.99", "cost_price": "1.50", "unit": "lt", "category_id": <cleaning_id>, "supplier_id": <cleanpro_id> }
```
```json
{ "sku": "CLEA-002", "name": "Disinfectant Spray", "unit_price": "6.99", "cost_price": "2.80", "unit": "unit", "category_id": <cleaning_id>, "supplier_id": <cleanpro_id> }
```

---

## 6. Purchase Orders

**POST** `/api/v1/purchase-orders/`

> Replace product IDs with the values returned in step 5.
> After creating each order, receive it with **PUT** `/api/v1/purchase-orders/{id}/status`
> to populate inventory.

### Order 1 — TechDist S.A.
```json
{
  "supplier_id": <techdist_id>,
  "details": [
    { "product_id": <elec001_id>, "quantity": 10, "unit_cost": "650.00" },
    { "product_id": <elec002_id>, "quantity": 50, "unit_cost": "12.00" },
    { "product_id": <elec003_id>, "quantity": 30, "unit_cost": "22.00" }
  ]
}
```

### Order 2 — OfiSupplies Ltda.
```json
{
  "supplier_id": <ofisupplies_id>,
  "details": [
    { "product_id": <offi001_id>, "quantity": 5,  "unit_cost": "110.00" },
    { "product_id": <offi002_id>, "quantity": 100, "unit_cost": "3.00" },
    { "product_id": <offi003_id>, "quantity": 80,  "unit_cost": "1.80" }
  ]
}
```

### Order 3 — CleanPro Corp.
```json
{
  "supplier_id": <cleanpro_id>,
  "details": [
    { "product_id": <clea001_id>, "quantity": 60, "unit_cost": "1.50" },
    { "product_id": <clea002_id>, "quantity": 40, "unit_cost": "2.80" }
  ]
}
```

### Receive each order

**PUT** `/api/v1/purchase-orders/{id}/status`
```json
{ "status": "received" }
```

---

## 7. Sales Orders

**POST** `/api/v1/sales-orders/`

### Order 1 — María García
```json
{
  "customer_id": <maria_id>,
  "details": [
    { "product_id": <elec002_id>, "quantity": 2, "unit_price": "29.99" },
    { "product_id": <offi003_id>, "quantity": 3, "unit_price": "4.49" }
  ]
}
```

### Order 2 — Empresa XYZ
```json
{
  "customer_id": <empresaxyz_id>,
  "details": [
    { "product_id": <elec001_id>, "quantity": 2, "unit_price": "899.99" },
    { "product_id": <elec003_id>, "quantity": 4, "unit_price": "49.99" }
  ]
}
```

### Order 3 — Pedro Jiménez
```json
{
  "customer_id": <pedro_id>,
  "details": [
    { "product_id": <offi001_id>, "quantity": 1, "unit_price": "199.99" },
    { "product_id": <offi002_id>, "quantity": 5, "unit_price": "5.99" }
  ]
}
```

### Order 4 — Lucía Vargas
```json
{
  "customer_id": <lucia_id>,
  "details": [
    { "product_id": <clea001_id>, "quantity": 3, "unit_price": "3.99" },
    { "product_id": <clea002_id>, "quantity": 2, "unit_price": "6.99" }
  ]
}
```

### Complete orders 1 and 2

**PUT** `/api/v1/sales-orders/{id}/status`
```json
{ "status": "completed" }
```

---

## 8. Payments

**POST** `/api/v1/payments/`

> Only for completed sales orders. Use the `total_amount` from the order response.

### Payment for Order 1
```json
{ "sales_order_id": <so1_id>, "amount": "59.45", "method": "card" }
```

### Payment for Order 2
```json
{ "sales_order_id": <so2_id>, "amount": "1999.94", "method": "transfer" }
```

---

## 9. Verify Reports

**GET** `/api/v1/reports/sales?format=pdf`

**GET** `/api/v1/reports/inventory?format=excel`
