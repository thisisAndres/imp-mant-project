from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from io import BytesIO


def generate_sales_excel(data: list[dict], filters: dict) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

    if data:
        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append([row.get(h) for h in headers])

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(fill_type="solid", fgColor="4F81BD")
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center")

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def generate_inventory_excel(data: list[dict]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventory Report"

    if data:
        headers = list(data[0].keys())
        ws.append(headers)
        for row in data:
            ws.append([row.get(h) for h in headers])

        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(fill_type="solid", fgColor="4F81BD")
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill

    buffer = BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
