from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import cm
from io import BytesIO


def generate_sales_pdf(data: list[dict], filters: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("Sales Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))

    # Filters summary
    filter_text = (
        f"Period: {filters.get('start_date', 'N/A')} to {filters.get('end_date', 'N/A')} "
        f"| Status: {filters.get('status', 'All')}"
    )
    elements.append(Paragraph(filter_text, styles["Normal"]))
    elements.append(Spacer(1, 0.5 * cm))

    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(h, "")) for h in headers])

        # Totals row
        total_amount = sum(row.get("Subtotal", 0) for row in data)
        totals_row = ["" for _ in headers]
        totals_row[0] = "TOTAL"
        if "Subtotal" in headers:
            totals_row[headers.index("Subtotal")] = f"{total_amount:.2f}"
        table_data.append(totals_row)

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#DCE6F1")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.whitesmoke),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No data found for the selected filters.", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()


def generate_inventory_pdf(data: list[dict]) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Inventory Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))

    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([str(row.get(h, "")) for h in headers])

        # Totals row
        total_value = sum(row.get("Total Value", 0) for row in data)
        total_qty = sum(row.get("Quantity", 0) for row in data)
        totals_row = ["" for _ in headers]
        totals_row[0] = "TOTAL"
        if "Quantity" in headers:
            totals_row[headers.index("Quantity")] = str(total_qty)
        if "Total Value" in headers:
            totals_row[headers.index("Total Value")] = f"{total_value:.2f}"
        table_data.append(totals_row)

        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#DCE6F1")]),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#4F81BD")),
            ("TEXTCOLOR", (0, -1), (-1, -1), colors.whitesmoke),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))
        elements.append(table)
    else:
        elements.append(Paragraph("No data found for the selected filters.", styles["Normal"]))

    doc.build(elements)
    return buffer.getvalue()
