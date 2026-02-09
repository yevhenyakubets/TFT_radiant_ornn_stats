import { useEffect, useState } from "react";

function ChampionsListPage() {
  const [champions, setChampions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Helper function to get TFT rarity colors
  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "#808080"; // Gray
      case 2: return "#11b288"; // Green
      case 3: return "#207ac7"; // Blue
      case 4: return "#c440da"; // Purple
      case 5:
      case 7: return "#ffb93b"; // Gold
      default: return "#ccc";
    }
  };

  useEffect(() => {
    fetch("http://127.0.0.1:8000/champions")
      .then(res => res.json())
      .then(data => {
        setChampions(data.champions);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div style={{ color: "white", padding: "20px" }}>Loading champions...</div>;
  }

  return (
    <div style={{ padding: "20px", backgroundColor: "#0a0a0c", minHeight: "100vh" }}>
      <h1 style={{ color: "white" }}>Champions</h1>

      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", 
        gap: "16px" 
      }}>
        {champions.map(champ => {
          const rarityColor = getRarityColor(champ.cost);
          
          return (
            <div
              key={champ.id}
              style={{
                border: `2px solid ${rarityColor}`, // Dynamic border based on cost
                padding: "12px",
                borderRadius: "8px",
                cursor: "pointer",
                backgroundColor: "#1c1c1f",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                transition: "transform 0.1s ease-in-out",
                boxShadow: "0 4px 6px rgba(0,0,0,0.3)"
              }}
              onClick={() => {
                window.location.href = `/champions/${champ.id}`;
              }}
              onMouseEnter={(e) => e.currentTarget.style.transform = "scale(1.05)"}
              onMouseLeave={(e) => e.currentTarget.style.transform = "scale(1)"}
            >
              {/* Champion Icon */}
              <img 
                src={`/assets/champ_logos/${champ.id}.png`} // Change path as needed
                alt={champ.name}
                style={{ 
                  width: "80px", 
                  height: "80px", 
                  borderRadius: "4px",
                  marginBottom: "8px",
                  border: `1px solid ${rarityColor}`
                }}
                onError={(e) => { e.target.style.display = 'none'; }}
              />

              <strong style={{ color: "white", textAlign: "center" }}>{champ.name}</strong>
              
              <div style={{ 
                fontSize: "12px", 
                fontWeight: "bold",
                color: rarityColor,
                marginTop: "4px"
              }}>
                {champ.cost} Gold
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ChampionsListPage;