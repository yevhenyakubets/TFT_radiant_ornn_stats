import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import Tooltip from "../components/Tooltip";
import "../Table.css";

function ItemPage() {
  // 1. Determine type based on the URL (e.g., /artifacts/:id vs /radiant/:id)
  const { itemId } = useParams();
  const location = useLocation();
  const isArtifact = location.pathname.includes("artifact");
  const [sortConfig, setSortConfig] = useState({ key: 'average_placement', direction: 'asc' });

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

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
  

//   const getRarityColor = (cost) => {
//     switch (cost) {
//       case 1: return "#808080";
//       case 2: return "#11b288";
//       case 3: return "#207ac7";
//       case 4: return "#c440da";
//       case 5:
//       case 7: return "#ffb93b";
//       default: return config.themeColor;
//     }
//   };


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
  const sortedData = [...championsToShow].sort((a, b) => {
    const valA = sortConfig.key === 'name' ? a[1].name : a[1][sortConfig.key];
    const valB = sortConfig.key === 'name' ? b[1].name : b[1][sortConfig.key];
    
    if (valA < valB) return sortConfig.direction === 'asc' ? -1 : 1;
    if (valA > valB) return sortConfig.direction === 'asc' ? 1 : -1;
    return 0;
  });

  return (
    <div className="item-page-wrapper">
      
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
      <div className="stats-table-container">
        <table className="stats-table">
          <thead>
            <tr>
              <th>Icon</th>
              <th onClick={() => requestSort('name')}>Name</th>
              <th onClick={() => requestSort('count')}>Frequency</th>
              <th onClick={() => requestSort('average_placement')}>Avg Place</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map(([champId, info]) => (
              <tr key={champId} className="stats-table-row" onClick={() => window.location.href=`/champions/${champId}`}>
                <td><img src={`/assets/champ_logos/${champId}.png`} className="table-icon" /></td>
                <td>{info.name}</td>
                <td>{info.count}</td>
                <td className="col-avg">#{info.average_placement.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ItemPage;