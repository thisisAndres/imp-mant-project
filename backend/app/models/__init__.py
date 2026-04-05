# Import all models so SQLAlchemy registers them with Base.metadata
# Required for Alembic autogenerate to detect all tables.
from app.models.role import Role
from app.models.user import User
from app.models.category import Category
from app.models.supplier import Supplier
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.customer import Customer
from app.models.purchase_order import PurchaseOrder, PurchaseOrderDetail
from app.models.sales_order import SalesOrder, SalesOrderDetail
from app.models.payment import Payment

__all__ = [
    "Role",
    "User",
    "Category",
    "Supplier",
    "Product",
    "Inventory",
    "Customer",
    "PurchaseOrder",
    "PurchaseOrderDetail",
    "SalesOrder",
    "SalesOrderDetail",
    "Payment",
]
