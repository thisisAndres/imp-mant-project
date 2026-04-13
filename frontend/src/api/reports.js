import axiosInstance from "./axiosInstance";

const getFilenameFromHeader = (contentDisposition, fallback) => {
  if (contentDisposition) {
    const match = contentDisposition.match(/filename="?([^"]+)"?/);
    if (match) return match[1];
  }
  return fallback;
};

export const downloadSalesReport = async ({ start_date, end_date, status, customer_id, format }) => {
  const params = { format };
  if (start_date) params.start_date = start_date;
  if (end_date) params.end_date = end_date;
  if (status) params.status = status;
  if (customer_id) params.customer_id = customer_id;

  const response = await axiosInstance.get("/reports/sales", {
    params,
    responseType: "blob",
  });

  const fallback = format === "pdf" ? "reporte_ventas.pdf" : "reporte_ventas.xlsx";
  const filename = getFilenameFromHeader(response.headers["content-disposition"], fallback);
  return { blob: response.data, filename };
};

export const downloadInventoryReport = async ({ category_id, status, supplier_id, format }) => {
  const params = { format };
  if (category_id) params.category_id = category_id;
  if (status) params.status = status;
  if (supplier_id) params.supplier_id = supplier_id;

  const response = await axiosInstance.get("/reports/inventory", {
    params,
    responseType: "blob",
  });

  const fallback = format === "pdf" ? "reporte_inventario.pdf" : "reporte_inventario.xlsx";
  const filename = getFilenameFromHeader(response.headers["content-disposition"], fallback);
  return { blob: response.data, filename };
};
