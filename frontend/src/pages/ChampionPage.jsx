import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

function ChampionPage() {
  const { championId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("artifact"); // 'artifact' or 'radiant'

  // Consistency: Rarity color logic
  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "#808080";
      case 2: return "#11b288";
      case 3: return "#207ac7";
      case 4: return "#c440da";
      case 5:
      case 7: return "#ffb93b";
      default: return "#ccc";
    }
  };

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/champions/${championId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [championId]);

  if (loading) return <div style={{ color: "white", padding: "20px" }}>Loading...</div>;
  if (data.error) return <div style={{ color: "red", padding: "20px" }}>{data.error}</div>;

  const rarityColor = getRarityColor(data.cost);
  
  // Choose the data slice based on the active tab
  const itemsToShow = activeTab === "artifact" ? data.artifacts : data.radiants;
  
  // Set the folder path based on the active tab
  const itemFolderPath = activeTab === "artifact" ? "/assets/artifacts" : "/assets/radiant_items";

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh", color: "white", fontFamily: "sans-serif" }}>
      
      {/* --- Champion Header --- */}
      <div style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: "24px", 
        marginBottom: "40px", 
        padding: "20px",
        borderRadius: "12px",
        background: `linear-gradient(90deg, #1c1c1f 0%, transparent 100%)`,
        borderLeft: `6px solid ${rarityColor}`
      }}>
        <img 
          src={`/assets/champ_logos/${championId}.png`} 
          alt={data.name} 
          style={{ width: "120px", height: "120px", borderRadius: "12px", border: `2px solid ${rarityColor}`, boxShadow: `0 0 15px ${rarityColor}44` }}
        />
        <div>
          <h1 style={{ margin: 0, fontSize: "2.8rem", letterSpacing: "-1px" }}>{data.name}</h1>
          <div style={{ color: rarityColor, fontWeight: "bold", fontSize: "1.2rem", marginTop: "4px" }}>
            {data.cost} Cost 
          </div>
        </div>
      </div>

      {/* --- Tab Switcher --- */}
      <div style={{ display: "flex", gap: "2px", marginBottom: "24px", backgroundColor: "#1c1c1f", width: "fit-content", padding: "4px", borderRadius: "8px" }}>
        {["artifact", "radiant"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: "12px 30px",
              cursor: "pointer",
              backgroundColor: activeTab === tab ? rarityColor : "transparent",
              color: activeTab === tab ? "black" : "white",
              border: "none",
              borderRadius: "6px",
              fontWeight: "bold",
              textTransform: "uppercase",
              fontSize: "0.85rem",
              transition: "all 0.2s ease"
            }}
          >
            {tab}s
          </button>
        ))}
      </div>

      {/* --- Items Grid --- */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", 
        gap: "16px" 
      }}>
        {Object.entries(itemsToShow).map(([itemId, info]) => (
          <div 
            key={itemId}
            style={{
              backgroundColor: "#16161a",
              padding: "16px",
              borderRadius: "10px",
              display: "flex",
              alignItems: "center",
              gap: "16px",
              border: "1px solid #2d2d31",
              transition: "transform 0.2s ease",
              cursor: "default"
            }}
            onMouseEnter={(e) => e.currentTarget.style.borderColor = rarityColor}
            onMouseLeave={(e) => e.currentTarget.style.borderColor = "#2d2d31"}
          >
            {/* Item Icon from specific folder */}
            <img 
              src={`${itemFolderPath}/${itemId}.png`} 
              alt={info.name}
              style={{ width: "56px", height: "56px", borderRadius: "6px", border: "1px solid #323232" }}
              onError={(e) => { e.target.src = null }}
            />
            
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: "bold", fontSize: "1.05rem", color: "#f0e6d2" }}>{info.name}</div>
              <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "2px" }}>
                Frequency: <span style={{ color: "#ddd" }}>{info.count}</span>
              </div>
            </div>

            <div style={{ textAlign: "right" }}>
              <div style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#ffb93b" }}>
                {info.average_placement.toFixed(2)}
              </div>
              <div style={{ fontSize: "0.65rem", color: "#666", textTransform: "uppercase", letterSpacing: "1px" }}>Avg Place</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ChampionPage;