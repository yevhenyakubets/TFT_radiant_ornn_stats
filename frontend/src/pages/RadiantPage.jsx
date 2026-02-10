import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function RadiantPage() {
  const { radiantId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "#808080";
      case 2: return "#11b288";
      case 3: return "#207ac7";
      case 4: return "#c440da";
      case 5:
      case 7: return "#ffb93b";
      default: return "#31c1ca"; // Radiant Cyan/Blue
    }
  };

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/radiant-items/${radiantId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [radiantId]);

  if (loading) return <div style={{ color: "white", padding: "20px" }}>Loading...</div>;
  if (data.error) return <div style={{ color: "red", padding: "20px" }}>{data.error}</div>;

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh", color: "white", fontFamily: "sans-serif" }}>
      
      {/* --- Item Header --- */}
      <div style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: "24px", 
        marginBottom: "40px", 
        padding: "20px",
        borderRadius: "12px",
        background: `linear-gradient(90deg, #1c1c1f 0%, transparent 100%)`,
        borderLeft: `6px solid #31c1ca` // Radiant Cyan
      }}>
        <img 
          src={`/assets/radiant_items/${radiantId}.png`} 
          alt={data.name} 
          style={{ width: "100px", height: "100px", borderRadius: "12px", border: `2px solid #31c1ca`, padding: "5px", backgroundColor: "#000" }}
        />
        <div>
          <h1 style={{ margin: 0, fontSize: "2.5rem" }}>{data.name}</h1>
          <div style={{ color: "#31c1ca", fontWeight: "bold", textTransform: "uppercase", fontSize: "0.9rem", marginTop: "4px" }}>
            Radiant Item
          </div>
        </div>
      </div>

      <h2 style={{ marginBottom: "20px", fontSize: "1.5rem", borderBottom: "1px solid #2d2d31", paddingBottom: "10px" }}>Best Champions</h2>

      {/* --- Champions Grid --- */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", 
        gap: "16px" 
      }}>
        {Object.entries(data.champions).map(([champId, info]) => {
          const champColor = getRarityColor(info.cost);
          return (
            <div 
              key={champId}
              style={{
                backgroundColor: "#16161a",
                padding: "16px",
                borderRadius: "10px",
                display: "flex",
                alignItems: "center",
                gap: "16px",
                border: `1px solid #2d2d31`,
                transition: "transform 0.2s ease",
                cursor: "pointer"
              }}
              onClick={() => window.location.href = `/champions/${champId}`}
            >
              <img 
                src={`/assets/champ_logos/${champId}.png`} 
                alt={info.name}
                style={{ width: "56px", height: "56px", borderRadius: "50%", border: `2px solid ${champColor}` }}
              />
              
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: "bold", fontSize: "1.1rem" }}>{info.name}</div>
              </div>

              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#ffb93b" }}>
                  #{info.average_placement.toFixed(2)}
                </div>
                <div style={{ fontSize: "0.6rem", color: "#666" }}>AVG PLACE</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default RadiantPage;