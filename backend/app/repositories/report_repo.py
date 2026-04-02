from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sales_order import SalesOrder, SalesOrderDetail
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.category import Category
from app.models.supplier import Supplier


async def sales_report_data(
    db: AsyncSession,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: str | None = None,
    customer_id: int | None = None,
) -> list[dict]:
    stmt = (
        select(SalesOrder)
        .options(
            selectinload(SalesOrder.details).selectinload(SalesOrderDetail.product),
            selectinload(SalesOrder.customer),
            selectinload(SalesOrder.user),
        )
    )
    if start_date:
        stmt = stmt.where(SalesOrder.created_at >= start_date)
    if end_date:
        stmt = stmt.where(SalesOrder.created_at <= end_date)
    if status:
        stmt = stmt.where(SalesOrder.status == status)
    if customer_id is not None:
        stmt = stmt.where(SalesOrder.customer_id == customer_id)
    stmt = stmt.order_by(SalesOrder.created_at.desc())

    result = await db.execute(stmt)
    orders = result.scalars().all()

    rows = []
    for order in orders:
        for detail in order.details:
            rows.append({
                "Order #": order.order_number,
                "Date": order.created_at.strftime("%Y-%m-%d"),
                "Customer": order.customer.full_name if order.customer else "N/A",
                "Seller": order.user.full_name if order.user else "N/A",
                "Product": detail.product.name if detail.product else "N/A",
                "Qty": detail.quantity,
                "Unit Price": float(detail.unit_price),
                "Subtotal": float(detail.subtotal),
                "Status": order.status,
            })
    return rows


async def inventory_report_data(
    db: AsyncSession,
    category_id: int | None = None,
    stock_status: str | None = None,
    supplier_id: int | None = None,
) -> list[dict]:
    stmt = (
        select(Inventory)
        .options(
            selectinload(Inventory.product).selectinload(Product.category),
            selectinload(Inventory.product).selectinload(Product.supplier),
        )
    )
    if category_id is not None:
        stmt = stmt.join(Product, Inventory.product_id == Product.id).where(
            Product.category_id == category_id
        )
    if supplier_id is not None:
        if category_id is None:
            stmt = stmt.join(Product, Inventory.product_id == Product.id)
        stmt = stmt.where(Product.supplier_id == supplier_id)

    result = await db.execute(stmt)
    inventories = result.scalars().all()

    rows = []
    for inv in inventories:
        product = inv.product
        if inv.quantity <= 0:
            status = "critical"
        elif inv.quantity <= inv.min_stock:
            status = "low"
        else:
            status = "normal"

        if stock_status and status != stock_status:
            continue

        rows.append({
            "SKU": product.sku if product else "N/A",
            "Product": product.name if product else "N/A",
            "Category": product.category.name if product and product.category else "N/A",
            "Supplier": product.supplier.company_name if product and product.supplier else "N/A",
            "Quantity": inv.quantity,
            "Min Stock": inv.min_stock,
            "Max Stock": inv.max_stock,
            "Status": status,
            "Unit Cost": float(product.cost_price) if product else 0,
            "Total Value": float(product.cost_price * inv.quantity) if product else 0,
        })
    return rows
