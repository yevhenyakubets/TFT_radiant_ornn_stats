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
              padding: "10px",
              borderRadius: "6px",
              cursor: "pointer"
            }}
            onClick={() => {
              window.location.href = `/items/${artifact.name}`;
            }}
          >
            <strong>{artifact.name}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ArtifactListPage;
