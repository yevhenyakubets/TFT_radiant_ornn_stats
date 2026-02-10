import { useEffect, useState } from "react";

function RadiantListPage() {
  const [radiants, setRadiants] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/radiant-items")
      .then(res => res.json())
      .then(data => {
        setRadiants(Object.values(data));
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading radiant items...</div>;
  }

  return (
<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "12px" }}>
  {radiants.map(radiant => (
    <div
      key={radiant.id}
      style={{
        border: "1px solid #40101f",
        padding: "12px",
        borderRadius: "8px",
        cursor: "pointer",
        backgroundColor: "#09d509", // Added a dark bg to make the gold/red pop
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        transition: "transform 0.2s",
      }}
      onClick={() => {
        window.location.href = `/radiant-items/${radiant.id}`;
      }}
    >
      {/* 1. The Icon */}
      <img 
        src={`/assets/radiant_items/${radiant.id}.png`}
        alt={radiant.name}
        style={{ 
          width: "48px", 
          height: "48px", 
          marginBottom: "8px",
          borderRadius: "4px",
          border: "1px solid #c8aa6e" // Classic League-style gold border
        }}
        // Fallback in case the ID doesn't match the image path exactly
        onError={(e) => { e.target.style.display = 'none'; }}
      />

      {/* 2. The Name */}
      <strong style={{ color: "#f0e6d2", fontSize: "0.9rem" }}>{radiant.name}</strong>
    </div>
  ))}
</div>
  );
}

export default RadiantListPage;
