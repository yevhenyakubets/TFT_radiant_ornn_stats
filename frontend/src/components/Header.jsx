// components/Header.jsx
import { useNavigate, useLocation } from "react-router-dom";

function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: "Home", path: "/" },
    { name: "Champions", path: "/champions" },
    { name: "Artifacts", path: "/artifacts" },
    { name: "Radiant Items", path: "/radiant-items" },
  ];

  return (
    <header style={{
      backgroundColor: "#16161a",
      padding: "10px 30px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      borderBottom: "1px solid #2d2d31",
      position: "sticky",
      top: 0,
      zIndex: 1000
    }}>
      {/* Navigation Buttons */}
      <div style={{ display: "flex", gap: "10px" }}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.name}
              onClick={() => navigate(item.path)}
              style={{
                backgroundColor: isActive ? "#2d2d31" : "transparent",
                color: isActive ? "#c8aa6e" : "#888",
                border: "none",
                padding: "8px 16px",
                borderRadius: "6px",
                cursor: "pointer",
                fontWeight: "bold",
                transition: "0.2s"
              }}
            >
              {item.name}
            </button>
          );
        })}
      </div>

      {/* Inactive Search Bar */}
      <div style={{ width: "300px" }}>
        <input
          type="text"
          placeholder="Search..."
          disabled
          style={{
            width: "100%",
            padding: "8px 12px",
            borderRadius: "6px",
            border: "1px solid #2d2d31",
            backgroundColor: "#0a0a0c",
            color: "#444",
            cursor: "not-allowed"
          }}
        />
      </div>
    </header>
  );
}

export default Header;