import { useEffect, useState } from "react";

function ArtifactListPage() {
  const [artifacts, setArtifacts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/artifacts")
      .then(res => res.json())
      .then(data => {
        setArtifacts(Object.values(data));
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading artifacts...</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Artifacts</h1>

<div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "12px" }}>
  {artifacts.map(artifact => (
    <div
      key={artifact.id}
      style={{
        border: "1px solid #78223c",
        padding: "12px",
        borderRadius: "8px",
        cursor: "pointer",
        backgroundColor: "#1a1a1a", // Added a dark bg to make the gold/red pop
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        textAlign: "center",
        transition: "transform 0.2s",
      }}
      onClick={() => {
        window.location.href = `/artifacts/${artifact.id}`;
      }}
    >
      {/* 1. The Icon */}
      <img 
        src={`/assets/artifacts/${artifact.id}.png`}
        alt={artifact.name}
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
      <strong style={{ color: "#f0e6d2", fontSize: "0.9rem" }}>{artifact.name}</strong>
    </div>
  ))}
</div>
    </div>
  );
}

export default ArtifactListPage;
