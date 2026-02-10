import { useEffect, useState } from "react";

function RadiantListPage() {
  const [radiants, setRadiants] = useState([]);
  const [loading, setLoading] = useState(true);

  const RADIANT_COLOR = "#31c1ca"; // The Radiant Cyan accent

  useEffect(() => {
    fetch("http://127.0.0.1:8000/radiant-items")
      .then(res => res.json())
      .then(data => {
        setRadiants(Object.values(data));
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ color: "white", padding: "20px" }}>Loading radiant items...</div>;
  }

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh" }}>
      <h1 style={{ color: "white", marginBottom: "30px", borderBottom: `2px solid ${RADIANT_COLOR}`, paddingBottom: "10px", width: "fit-content" }}>
        Radiant Items
      </h1>

      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", 
        gap: "16px" 
      }}>
        {radiants.map(radiant => (
          <div
            key={radiant.id}
            style={{
              border: `1px solid #2d2d31`,
              padding: "20px",
              borderRadius: "10px",
              cursor: "pointer",
              backgroundColor: "#16161a",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              textAlign: "center",
              transition: "all 0.2s ease-in-out",
            }}
            onClick={() => {
              window.location.href = `/radiant-items/${radiant.id}`;
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-5px)";
              e.currentTarget.style.borderColor = RADIANT_COLOR;
              e.currentTarget.style.boxShadow = `0 5px 15px ${RADIANT_COLOR}33`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "#2d2d31";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <img 
              src={`/assets/radiant_items/${radiant.id}.png`}
              alt={radiant.name}
              style={{ 
                width: "64px", 
                height: "64px", 
                marginBottom: "12px",
                borderRadius: "6px",
                border: `1px solid ${RADIANT_COLOR}`,
                backgroundColor: "#000"
              }}
              onError={(e) => { e.target.style.display = 'none'; }}
            />
            <strong style={{ color: "#f0e6d2", fontSize: "0.95rem" }}>{radiant.name}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RadiantListPage;