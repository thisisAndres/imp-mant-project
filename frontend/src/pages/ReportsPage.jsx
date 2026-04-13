import { useState } from "react";
import Navbar from "../components/Navbar";
import { downloadSalesReport, downloadInventoryReport } from "../api/reports";

const triggerDownload = ({ blob, filename }) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
};

function ReportsPage() {
  const [salesForm, setSalesForm] = useState({
    start_date: "",
    end_date: "",
    status: "",
    format: "pdf",
  });
  const [salesLoading, setSalesLoading] = useState(false);
  const [salesError, setSalesError] = useState("");

  const [inventoryForm, setInventoryForm] = useState({
    status: "",
    format: "pdf",
  });
  const [inventoryLoading, setInventoryLoading] = useState(false);
  const [inventoryError, setInventoryError] = useState("");

  const handleSalesDownload = async (e) => {
    e.preventDefault();
    setSalesError("");
    setSalesLoading(true);
    try {
      const result = await downloadSalesReport(salesForm);
      triggerDownload(result);
    } catch (err) {
      setSalesError(err?.response?.data?.detail || "Error al descargar el reporte.");
    } finally {
      setSalesLoading(false);
    }
  };

  const handleInventoryDownload = async (e) => {
    e.preventDefault();
    setInventoryError("");
    setInventoryLoading(true);
    try {
      const result = await downloadInventoryReport(inventoryForm);
      triggerDownload(result);
    } catch (err) {
      setInventoryError(err?.response?.data?.detail || "Error al descargar el reporte.");
    } finally {
      setInventoryLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <Navbar />
      <div style={styles.content}>
        <h1 style={styles.pageTitle}>Reportes</h1>

        {/* Reporte de Ventas */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Reporte de Ventas</h2>
          <form onSubmit={handleSalesDownload}>
            <div style={styles.row}>
              <div style={styles.field}>
                <label style={styles.label}>Fecha inicio</label>
                <input
                  type="date"
                  style={styles.input}
                  value={salesForm.start_date}
                  onChange={(e) => setSalesForm({ ...salesForm, start_date: e.target.value })}
                />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Fecha fin</label>
                <input
                  type="date"
                  style={styles.input}
                  value={salesForm.end_date}
                  onChange={(e) => setSalesForm({ ...salesForm, end_date: e.target.value })}
                />
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Estado</label>
                <select
                  style={styles.input}
                  value={salesForm.status}
                  onChange={(e) => setSalesForm({ ...salesForm, status: e.target.value })}
                >
                  <option value="">Todos</option>
                  <option value="pending">Pendiente</option>
                  <option value="completed">Completado</option>
                  <option value="cancelled">Cancelado</option>
                </select>
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Formato</label>
                <select
                  style={styles.input}
                  value={salesForm.format}
                  onChange={(e) => setSalesForm({ ...salesForm, format: e.target.value })}
                >
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                </select>
              </div>
            </div>
            {salesError && <p style={styles.error}>{salesError}</p>}
            <button type="submit" style={styles.btn} disabled={salesLoading}>
              {salesLoading ? "Descargando..." : "Descargar"}
            </button>
          </form>
        </div>

        {/* Reporte de Inventario */}
        <div style={styles.card}>
          <h2 style={styles.cardTitle}>Reporte de Inventario</h2>
          <form onSubmit={handleInventoryDownload}>
            <div style={styles.row}>
              <div style={styles.field}>
                <label style={styles.label}>Estado de stock</label>
                <select
                  style={styles.input}
                  value={inventoryForm.status}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, status: e.target.value })}
                >
                  <option value="">Todos</option>
                  <option value="normal">Normal</option>
                  <option value="low">Bajo</option>
                  <option value="critical">Crítico</option>
                </select>
              </div>
              <div style={styles.field}>
                <label style={styles.label}>Formato</label>
                <select
                  style={styles.input}
                  value={inventoryForm.format}
                  onChange={(e) => setInventoryForm({ ...inventoryForm, format: e.target.value })}
                >
                  <option value="pdf">PDF</option>
                  <option value="excel">Excel</option>
                </select>
              </div>
            </div>
            {inventoryError && <p style={styles.error}>{inventoryError}</p>}
            <button type="submit" style={styles.btn} disabled={inventoryLoading}>
              {inventoryLoading ? "Descargando..." : "Descargar"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    backgroundColor: "#f3f4f6",
  },
  content: {
    padding: "2rem",
    maxWidth: "900px",
    margin: "0 auto",
  },
  pageTitle: {
    fontSize: "1.8rem",
    marginBottom: "1.5rem",
  },
  card: {
    backgroundColor: "#fff",
    padding: "1.5rem",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
    marginBottom: "1.5rem",
  },
  cardTitle: {
    fontSize: "1.2rem",
    marginBottom: "1rem",
  },
  row: {
    display: "flex",
    flexWrap: "wrap",
    gap: "1rem",
    marginBottom: "1rem",
  },
  field: {
    display: "flex",
    flexDirection: "column",
    minWidth: "160px",
    flex: "1",
  },
  label: {
    fontSize: "0.85rem",
    marginBottom: "0.3rem",
    color: "#374151",
    fontWeight: "500",
  },
  input: {
    padding: "0.6rem",
    borderRadius: "6px",
    border: "1px solid #d1d5db",
    fontSize: "0.9rem",
  },
  btn: {
    padding: "0.6rem 1.5rem",
    backgroundColor: "#111827",
    color: "#fff",
    border: "none",
    borderRadius: "8px",
    fontWeight: "bold",
    cursor: "pointer",
  },
  error: {
    color: "red",
    fontSize: "0.85rem",
    marginBottom: "0.5rem",
  },
};

export default ReportsPage;
