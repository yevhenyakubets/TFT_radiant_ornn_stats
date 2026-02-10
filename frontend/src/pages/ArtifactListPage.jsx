import { useEffect, useState } from "react";

function ArtifactListPage() {
  const [artifacts, setArtifacts] = useState([]);
  const [loading, setLoading] = useState(true);

  const ARTIFACT_COLOR = "#c8aa6e"; // The Artifact Gold accent

  useEffect(() => {
    fetch("http://127.0.0.1:8000/artifacts")
      .then(res => res.json())
      .then(data => {
        setArtifacts(Object.values(data));
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ color: "white", padding: "20px" }}>Loading artifacts...</div>;
  }

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh" }}>
      <h1 style={{ color: "white", marginBottom: "30px", borderBottom: `2px solid ${ARTIFACT_COLOR}`, paddingBottom: "10px", width: "fit-content" }}>
        Artifacts
      </h1>

      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", 
        gap: "16px" 
      }}>
        {artifacts.map(artifact => (
          <div
            key={artifact.id}
            style={{
              border: "1px solid #2d2d31",
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
              window.location.href = `/artifacts/${artifact.id}`;
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-5px)";
              e.currentTarget.style.borderColor = ARTIFACT_COLOR;
              e.currentTarget.style.boxShadow = `0 5px 15px ${ARTIFACT_COLOR}33`;
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.borderColor = "#2d2d31";
              e.currentTarget.style.boxShadow = "none";
            }}
          >
            <img 
              src={`/assets/artifacts/${artifact.id}.png`}
              alt={artifact.name}
              style={{ 
                width: "64px", 
                height: "64px", 
                marginBottom: "12px",
                borderRadius: "6px",
                border: `1px solid ${ARTIFACT_COLOR}`,
                backgroundColor: "#000"
              }}
              onError={(e) => { e.target.style.display = 'none'; }}
            />
            <strong style={{ color: "#f0e6d2", fontSize: "0.95rem" }}>{artifact.name}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ArtifactListPage;