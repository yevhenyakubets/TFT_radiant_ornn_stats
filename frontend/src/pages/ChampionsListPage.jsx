import { Link } from "react-router-dom";

const CHAMPIONS = [
  "Ornn",
  "Yunara",
  "Lux",
  "Sona",
  "Lissandra",
  "Kaisa"
];

function ChampionsListPage() {
  return (
    <div style={{ padding: "20px" }}>
      <h1>Champions</h1>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(150px, 1fr))", gap: "16px" }}>
        {CHAMPIONS.map(champ => (
          <Link
            key={champ}
            to={`/champions/${champ}`}
            style={{
              textDecoration: "none",
              border: "1px solid #ccc",
              padding: "12px",
              borderRadius: "8px",
              textAlign: "center",
              color: "black"
            }}
          >
            <strong>{champ}</strong>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default ChampionsListPage;
