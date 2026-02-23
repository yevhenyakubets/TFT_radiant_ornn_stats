import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import Tooltip from "../components/Tooltip";

function ItemPage() {
  // 1. Determine type based on the URL (e.g., /artifacts/:id vs /radiant/:id)
  const { itemId } = useParams();
  const location = useLocation();
  const isArtifact = location.pathname.includes("artifact");

  // 2. Configuration based on item type
  const config = isArtifact ? {
    endpoint: "artifacts",
    assetFolder: "artifacts",
    themeColor: "#e65d08cd" // Gold-ish for artifacts
  } : {
    endpoint: "radiant-items",
    assetFolder: "radiant_items",
    themeColor: "#9cca31" // Cyan-ish for radiants
  };

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInvalid, setShowInvalid] = useState(false);
  const [showLowSample, setShowLowSample] = useState(false);
  

  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "#808080";
      case 2: return "#11b288";
      case 3: return "#207ac7";
      case 4: return "#c440da";
      case 5:
      case 7: return "#ffb93b";
      default: return config.themeColor;
    }
  };


const stat_map = {
    "AD": "AD",
    "AP": "AP",
    "AS": "AS",
    "Armor": "Armor",
    "Health": "Health",
    "MagicResist": "MR", // Maps MagicResist to your MR.png
    "CritChance": "CritChance",
    "BuffDamageAmp": "scaleDA",
    "ManaRegen":"scalemanaregen",
    "{cd951938}":"scaleDR",
    "StatOmnivamp":"scaleSV",
    "DamageAmp": "scaleDA"
}


  const formatStatValue = (value, key) => {
    if (key === "BuffDamageAmp" || key === "AD" || key == "StatOmnivamp" || key == "DamageAmp" || key == "{cd951938}") {
      return `+${Math.round(value * 100)}%`;
    }
    if (key === "AS" || key === "CritChance") {
    return `+${Math.round(value)}%`; 
  } 
    return `+${Math.round(value)}`;
  };

useEffect(() => {
  let isMounted = true;

  // REMOVED: setLoading(true) and setData(null) 
  // Because 'key' on the Route handles the reset for us!

  fetch(`http://127.0.0.1:8000/${config.endpoint}/${itemId}`)
    .then((res) => res.json())
    .then((json) => {
      if (isMounted) {
        setData(json);
        setLoading(false);
      }
    })
    .catch(() => {
      if (isMounted) {
        setData({ error: "Failed to fetch data" });
        setLoading(false);
      }
    });

  return () => {
    isMounted = false;
  };
}, [itemId, config.endpoint]);

  if (loading) return <div style={{ color: "white", padding: "20px" }}>Loading...</div>;
  if (data.error) return <div style={{ color: "red", padding: "20px" }}>{data.error}</div>;

  const championsToShow = Object.entries(data.champions || {}).filter(([, info]) => {
    const isCorrectValidity = info.valid || showInvalid;
    const isCorrectSample = !info.low_sample || showLowSample;
    return isCorrectValidity && isCorrectSample;
  });

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh", color: "white", fontFamily: "sans-serif" }}>
      
      {/* --- Item Header --- */}
      <div style={{ 
        display: "flex", alignItems: "center", gap: "24px", marginBottom: "40px", padding: "20px",
        borderRadius: "12px", background: `linear-gradient(90deg, #1c1c1f 0%, transparent 100%)`,
        borderLeft: `6px solid ${config.themeColor}` 
      }}>
        <img 
          src={`/assets/${config.assetFolder}/${itemId}.png`} 
          alt={data.name} 
          style={{ width: "100px", height: "100px", borderRadius: "12px", border: `2px solid ${config.themeColor}`, padding: "5px", backgroundColor: "#000" }}
        />
        <div>
          <h1 style={{ margin: 0, fontSize: "2.5rem" }}>{data.name}</h1>
                {/* NEW: Stats Row */}
          <div style={{ display: "flex", gap: "7px", flexWrap: "wrap", alignItems: "center" }}>
            {data.stats && Object.entries(data.stats)
            .filter(([key]) => key in stat_map)
            .map(([key, val]) => (
            <div key={key} style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <img 
                src={`/assets/stats/${stat_map[key]}.png`} 
                alt={key} 
                style={{ width: "20px", height: "20px" }}
                />
                <span style={{ fontSize: "1rem", fontWeight: "bold", color: "#ddd" }}>
                {formatStatValue(val, key)}
                </span>
            </div>
            ))
            }
            </div>
          <div style={{ color: config.themeColor, fontWeight: "bold", textTransform: "uppercase", fontSize: "0.9rem", marginTop: "4px" }}>
            {data.description}
          </div>
        </div>
      </div>

      {/* --- Filter Bar --- */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", borderBottom: "1px solid #2d2d31", paddingBottom: "10px" }}>
        <h2 style={{ margin: 0, fontSize: "1.5rem" }}>Best Champions</h2>
        <div style={{ display: "flex", gap: "20px" }}>
          <label style={{ color: "#888", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
            Show low sample size
            <input type="checkbox" checked={showLowSample} onChange={() => setShowLowSample(!showLowSample)} />
          </label>
          <label style={{ color: "#888", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
            Show niche units
            <input type="checkbox" checked={showInvalid} onChange={() => setShowInvalid(!showInvalid)} />
          </label>
        </div>
      </div>

      {/* --- Champions Grid --- */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "16px" }}>
        {championsToShow.map(([champId, info]) => {
          const champColor = getRarityColor(info.cost);
          
          const champCard = (
            <div 
              style={{
                backgroundColor: "#16161a", padding: "16px", borderRadius: "10px",
                display: "flex", alignItems: "center", gap: "16px",
                border: info.low_sample ? "1px dashed #ff4e4e" : `1px solid #2d2d31`,
                opacity: info.valid ? 1 : 0.5,
                transition: "transform 0.2s ease", cursor: "pointer"
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
                <div style={{ fontSize: "0.85rem", color: "#888" }}>
                  Freq: <span style={{ color: "#ddd" }}>{info.count}</span>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#ffb93b" }}>
                  #{info.average_placement.toFixed(2)}
                </div>
                <div style={{ fontSize: "0.6rem", color: "#666" }}>AVG PLACE</div>
              </div>
            </div>
          );

          if (info.low_sample) return <Tooltip key={champId} text="Low sample size">{champCard}</Tooltip>;
          if (!info.valid) return <Tooltip key={champId} text="Invalid/Niche combination" color="#888">{champCard}</Tooltip>;
          return <div key={champId}>{champCard}</div>;
        })}
      </div>
    </div>
  );
}

export default ItemPage;