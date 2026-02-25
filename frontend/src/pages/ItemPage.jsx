import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import Tooltip from "../components/Tooltip";
import "../styles/Table.css";
import "../styles/ItemPage.css";

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

const getSortIcon = (key) => {
  if (sortConfig.key !== key) return <span className="sort-arrow-placeholder"></span>;
  return sortConfig.direction === 'asc' ? ' ▲' : ' ▼';
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
      <div className="item-header">
        <img
          className="item-image" 
          src={`/assets/${config.assetFolder}/${itemId}.png`} 
          alt={data.name} 
        />
        
        {/* NEW WRAPPER DIV */}
        <div className="item-info-container">
          <h1 className="item-name">{data.name}</h1>
          
          <div className="stats-row">
            {data.stats && Object.entries(data.stats)
              .filter(([key]) => key in stat_map)
              .map(([key, val]) => (
                <div key={key}>
                  <img
                    className="stat-image" 
                    src={`/assets/stats/${stat_map[key]}.png`} 
                    alt={key} 
                  />
                  <span> {formatStatValue(val, key)} </span>
                </div>
              ))
            }
          </div>

          <div className="item-description">
            {data.description}
          </div>
        </div>
      </div>

      {/* --- Filter Bar --- */}
      <div className="filter-bar">
        <h2 className="filter-bar-title">Best users of {data.name}</h2>
        
        <div className="filter-options">
          <label className="filter-label">
            Show low sample size
            <input 
              type="checkbox" 
              checked={showLowSample} 
              onChange={() => setShowLowSample(!showLowSample)} 
            />
          </label>
          
          <label className="filter-label">
            Show niche units
            <input 
              type="checkbox" 
              checked={showInvalid} 
              onChange={() => setShowInvalid(!showInvalid)} 
            />
          </label>
        </div>
      </div>

      {/* --- Champions Table --- */}
      <div className="stats-table-container">
        <table className="stats-table">
          <thead>
                <tr>
                  <th onClick={() => requestSort('name')} className="champ-column-header">
                    Champion {getSortIcon('name')}
                  </th>
                  <th onClick={() => requestSort('count')}>
                    Frequency {getSortIcon('count')}
                  </th>
                  <th onClick={() => requestSort('average_placement')}>
                    Avg Place {getSortIcon('average_placement')}
                  </th>
                </tr>
              </thead>
          <tbody>
            {sortedData.map(([champId, info]) => (
              <tr 
                key={champId} 
                className="stats-table-row" 
                onClick={() => window.location.href=`/champions/${champId}`}
              >
                {/* Combined Icon and Name Cell */}
                <td className="champ-cell">
                  <img 
                    src={`/assets/champ_logos/${champId}.png`} 
                    className="table-icon" 
                    alt={info.name}
                  />
                  <span className="champ-name-text">{info.name}</span>
                </td>

                <td className="col-count">{info.count.toLocaleString()}</td>
                
                {/* Removed the # character here */}
                <td className="col-avg">
                  {info.average_placement.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ItemPage;