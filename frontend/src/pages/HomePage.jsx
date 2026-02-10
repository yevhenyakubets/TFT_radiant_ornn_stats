import { useState } from "react";

function HomePage() {
  const [searchQuery, setSearchQuery] = useState("");

  const navButtons = [
    {
      name: "Champions",
      path: "/champions",
      color: "#c440da", // Purple rarity color
      description: "Find the best items for specified champions."
    },
    {
      name: "Artifacts",
      path: "/artifacts",
      color: "#c8aa6e", // Ornn Gold
      description: "Find the best users for specified Artifacts."
    },
    {
      name: "Radiant Items",
      path: "/radiant-items",
      color: "#31c1ca", // Radiant Cyan
      description: "Find the best users for specified Radiant items."
    }
  ];

  return (
    <div style={{
      backgroundColor: "#0a0a0c",
      minHeight: "100vh",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "20px",
      color: "white",
      fontFamily: "sans-serif"
    }}>
      {/* --- Hero Section --- */}
      <div style={{ textAlign: "center", marginBottom: "50px" }}>
        <h1 style={{ fontSize: "2.5rem", marginBottom: "10px", letterSpacing: "-2px" }}>
          TFT <span style={{ color: "#c8aa6e" }}>ARTIFACTS AND RADIANT ITEMS</span>
        </h1>
        <p style={{ color: "#888", fontSize: "1.1rem" }}>
          Analyze placements and optimize your itemization.
        </p>
        <p style={{ color: "#888", fontSize: "1.1rem" }}>
          Find the best items for champions, as well as best users for specific items
        </p>
      </div>

      {/* --- Search Bar (Visual Only) --- */}
      <div style={{ width: "100%", maxWidth: "600px", marginBottom: "60px" }}>
        <div style={{ position: "relative" }}>
          <input
            type="text"
            placeholder="Search for a champion or item..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: "100%",
              padding: "16px 20px",
              borderRadius: "12px",
              border: "2px solid #2d2d31",
              backgroundColor: "#16161a",
              color: "white",
              fontSize: "1.1rem",
              outline: "none",
              transition: "border-color 0.2s"
            }}
            onFocus={(e) => e.target.style.borderColor = "#c8aa6e"}
            onBlur={(e) => e.target.style.borderColor = "#2d2d31"}
          />
          <div style={{
            position: "absolute",
            right: "20px",
            top: "50%",
            transform: "translateY(-50%)",
            color: "#444"
          }}>
            Enter ↵
          </div>
        </div>
      </div>

      {/* --- Navigation Buttons --- */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
        gap: "20px",
        width: "100%",
        maxWidth: "900px"
      }}>
        {navButtons.map((btn) => (
          <div
            key={btn.name}
            onClick={() => window.location.href = btn.path}
            style={{
              backgroundColor: "#16161a",
              padding: "30px",
              borderRadius: "16px",
              border: "1px solid #2d2d31",
              textAlign: "center",
              cursor: "pointer",
              transition: "all 0.3s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = btn.color;
              e.currentTarget.style.transform = "translateY(-8px)";
              e.currentTarget.style.backgroundColor = "#1c1c22";
              e.currentTarget.style.boxShadow = `0 10px 30px ${btn.color}22`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = "#2d2d31";
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.backgroundColor = "#16161a";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <h2 style={{ color: btn.color, margin: "0 0 10px 0", fontSize: "1.5rem" }}>
              {btn.name}
            </h2>
            <p style={{ color: "#777", fontSize: "0.9rem", margin: 0 }}>
              {btn.description}
            </p>
          </div>
        ))}
      </div>

      {/* --- Footer Decoration --- */}
      <div style={{ marginTop: "80px", opacity: 0.3, fontSize: "0.8rem", letterSpacing: "2px" }}>
        DATA POWERED BY RIOT GAMES API
      </div>
    </div>
  );
}

export default HomePage;