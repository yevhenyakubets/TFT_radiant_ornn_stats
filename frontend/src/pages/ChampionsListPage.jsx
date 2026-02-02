import { useEffect, useState } from "react";

function ChampionsListPage() {
  const [champions, setChampions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/champions")
      .then(res => res.json())
      .then(data => {
        setChampions(data.champions);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading champions...</div>;
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>Champions</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "12px" }}>
        {champions.map(champ => (
          <div
            key={champ.id}
            style={{
              border: "1px solid #ccc",
              padding: "10px",
              borderRadius: "6px",
              cursor: "pointer"
            }}
            onClick={() => {
              window.location.href = `/champions/${champ.name}`;
            }}
          >
            <strong>{champ.name}</strong>
            <div style={{ fontSize: "12px", opacity: 0.7 }}>
              Cost: {champ.cost}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChampionsListPage;
