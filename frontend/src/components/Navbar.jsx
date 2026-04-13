import { Link, useNavigate } from "react-router-dom";

function Navbar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  };

  return (
    <header style={styles.header}>
      <span style={styles.brand}>SGIV</span>
      <nav style={styles.nav}>
        <Link to="/reports" style={styles.link}>Reportes</Link>
        <button onClick={handleLogout} style={styles.logoutBtn}>Logout</button>
      </nav>
    </header>
  );
}

const styles = {
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "0.8rem 2rem",
    backgroundColor: "#111827",
    color: "#fff",
  },
  brand: {
    fontSize: "1.2rem",
    fontWeight: "bold",
    letterSpacing: "0.05em",
  },
  nav: {
    display: "flex",
    alignItems: "center",
    gap: "1.5rem",
  },
  link: {
    color: "#d1d5db",
    textDecoration: "none",
    fontWeight: "500",
  },
  logoutBtn: {
    padding: "0.4rem 1rem",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    backgroundColor: "transparent",
    color: "#d1d5db",
    cursor: "pointer",
    fontWeight: "500",
  },
};

export default Navbar;
