import Navbar from "../components/Navbar";

function Dashboard() {
  return (
    <div style={styles.container}>
      <Navbar />
      <div style={styles.content}>
      <h1 style={styles.title}>Dashboard</h1>
      <p style={styles.subtitle}>Bienvenido al sistema SGIV</p>

      <div style={styles.cards}>
        <div style={styles.card}>
          <h2>Login</h2>
          <p>La autenticación ya está conectada con la API.</p>
        </div>

        <div style={styles.card}>
          <h2>Reportes</h2>
          <p>Desde aquí podrás descargar reportes de ventas e inventario.</p>
        </div>
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
  },
  title: {
    fontSize: "2rem",
    marginBottom: "0.5rem",
  },
  subtitle: {
    marginBottom: "2rem",
    color: "#555",
  },
  cards: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
    gap: "1rem",
  },
  card: {
    backgroundColor: "#fff",
    padding: "1.5rem",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
  },
};

export default Dashboard;