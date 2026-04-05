from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import require_role
from app.db.session import get_db
from app.models.user import User
from app.repositories import report_repo
from app.reports.pdf_generator import generate_sales_pdf, generate_inventory_pdf
from app.reports.excel_generator import generate_sales_excel, generate_inventory_excel

router = APIRouter()

admin_manager = require_role("admin", "manager")

_VALID_SALES_STATUSES = {"pending", "completed", "cancelled"}
_VALID_STOCK_STATUSES = {"normal", "low", "critical"}


@router.get("/sales")
async def sales_report(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    status: str | None = None,
    customer_id: int | None = None,
    format: str = Query("pdf", pattern="^(pdf|excel)$"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    if status is not None and status not in _VALID_SALES_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"status must be one of {_VALID_SALES_STATUSES}",
        )
    data = await report_repo.sales_report_data(
        db, start_date=start_date, end_date=end_date,
        status=status, customer_id=customer_id,
    )
    filters = {
        "start_date": str(start_date) if start_date else "N/A",
        "end_date": str(end_date) if end_date else "N/A",
        "status": status or "All",
    }

    if format == "pdf":
        content = generate_sales_pdf(data, filters)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=sales_report.pdf"},
        )
    else:
        content = generate_sales_excel(data, filters)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=sales_report.xlsx"},
        )


@router.get("/inventory")
async def inventory_report(
    category_id: int | None = None,
    status: str | None = None,
    supplier_id: int | None = None,
    format: str = Query("pdf", pattern="^(pdf|excel)$"),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(admin_manager),
):
    if status is not None and status not in _VALID_STOCK_STATUSES:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"status must be one of {_VALID_STOCK_STATUSES}",
        )
    data = await report_repo.inventory_report_data(
        db, category_id=category_id, stock_status=status, supplier_id=supplier_id,
    )

    if format == "pdf":
        content = generate_inventory_pdf(data)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=inventory_report.pdf"},
        )
    else:
        content = generate_inventory_excel(data)
        return StreamingResponse(
            BytesIO(content),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=inventory_report.xlsx"},
        )
