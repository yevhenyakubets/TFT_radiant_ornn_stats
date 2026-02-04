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
    <div style={{ padding: "20px" }}>
      <h1>Radiant items</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "12px" }}>
        {radiants.map(radiant => (
          <div
            key={radiant.id}
            style={{
              border: "1px solid #8fed1d",
              padding: "10px",
              borderRadius: "6px",
              cursor: "pointer"
            }}
            onClick={() => {
              window.location.href = `/radiant-items/${radiant.id}`;
            }}
          >
            <strong>{radiant.name}</strong>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RadiantListPage;
