import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tooltip from "../components/Tooltip"; 
import React from 'react';
import "../styles/common.css";
import "../styles/ChampionPage.css";

const ChampionAbility = ({ champion }) => {
  if (!champion || !champion.ability_description) return null;

  const getDamageColor = (sentencePart) => {
    const text = sentencePart.toLowerCase();
    if (text.includes("magic damage")) return "var(--magic-damage)"; 
    if (text.includes("physical damage")) return "var(--physical-damage)"; 
    if (text.includes("true damage")) return "var(--true-damage)"; 
    if (text.includes("shield") || text.includes("health")) return "var(--utility-green)"; 
    return "var(--text-main)"; 
  };

  const getStatFileName = (stat) => {
    const s = stat.toLowerCase().trim();
    const mapping = {
      'ad': 'AD', 'ap': 'AP', 'armor': 'Armor', 'as': 'AS',
      'crit': 'CritChance', 'health': 'Health', 'hp': 'Health',
      'mr': 'MR', 'dr': 'scaleDR', 'manaregen': 'scalemanaregen', 'sv': 'scaleSV'
    };
    return mapping[s] || stat;
  };

  const formatDescription = (text) => {
    const parts = text.split("<keyword>");
    const mainBody = parts[0];
    const keywords = parts.slice(1);
    const statRegex = /([\d./%]+)\s*\(([^)]+)\)/g;

    const renderLine = (line, lineIdx) => {
      return line.split(statRegex).map((part, i, arr) => {
        if (i % 3 === 1) {
          const contextText = arr[i + 2] || "";
          return (
            <span key={`val-${lineIdx}-${i}`} className="ability-stat-value" style={{ color: getDamageColor(contextText) }}>
              {part}
            </span>
          );
        }
        if (i % 3 === 2) {
          const individualStats = part.split(',').map(s => s.trim());
          return (
            <span key={`stats-${lineIdx}-${i}`} className="ability-stat-icons">
              {individualStats.map((stat, idx) => (
                <img
                  key={idx}
                  src={`/assets/stats/${encodeURIComponent(getStatFileName(stat))}.png`}
                  alt={stat}
                  className="description-stat-icon"
                  onError={(e) => (e.target.style.display = "none")}
                />
              ))}
            </span>
          );
        }
        return part;
      });
    };

    const lines = mainBody.split('\n').filter(line => line.trim() !== '');
    
    return (
      <>
        <div className="main-ability-text">
          {lines.map((line, lineIdx) => (
            <p key={lineIdx} className="ability-line">
              {renderLine(line, lineIdx)}
            </p>
          ))}
        </div>
        {keywords.length > 0 && (
          <div className="keywords-container">
            {keywords.map((kw, idx) => (
              <p key={idx} className="keyword-item">
                • {kw.replace("</keyword>", "").trim()}
              </p>
            ))}
          </div>
        )}
      </>
    );
  };

  return (
    <div className="ability-container">
      <div className="ability-header">
        <img 
          src={`/assets/ability_icons/${champion.champion.toLowerCase()}.png`} 
          className="ability-icon"
          alt={champion.ability_name}
          onError={(e) => (e.target.src = "/assets/ability_icons/default.png")}
        />
        <h3 className="ability-title">{champion.ability_name}</h3>
      </div>
      <div className="description-text">
        {formatDescription(champion.ability_description)}
      </div>
    </div>
  );
};

function ChampionPage() {
  const { championId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("artifact");
  const [showInvalid, setShowInvalid] = useState(false);
  const [showLowSample, setShowLowSample] = useState(false);
  const [sortConfig, setSortConfig] = useState({ key: 'average_placement', direction: 'asc' });

  const buttonColor = "rgb(5, 30, 41)";

  const requestSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return <span className="sort-arrow-placeholder"></span>;
    return sortConfig.direction === 'asc' ? ' ▲' : ' ▼';
  };

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

  if (loading) return <div className="loading-state">Loading...</div>;
  if (data.error) return <div className="error-state">{data.error}</div>;

  const rarityColor = getRarityColor(data.cost);
  const rawItems = activeTab === "artifact" ? data.artifacts : data.radiants;
  const itemFolderPath = activeTab === "artifact" ? "/assets/artifacts" : "/assets/radiant_items";

  const itemsToShow = Object.entries(rawItems).filter(([, info]) => {
    const matchesValid = info.valid || showInvalid;
    const matchesSample = !info.low_sample || showLowSample;
    return matchesValid && matchesSample;
  });

  return (
    <div className="champion-page-wrapper">
      
      {/* --- Header Section --- */}
      <div className="champion-header">
        <div
          className="shop-card"
          style={{ "--rarity-color": rarityColor, width: "220px", cursor: "default" }}
        >
          <div className="shop-splash-container">
            <img
              src={`/assets/champ_splashes/${championId}.png`}
              alt={data.name}
              className="shop-splash-img"
              onError={(e) => { e.target.src = `/assets/champ_logos/${championId}.png`; }}
            />
            <div className="shop-traits-overlay">
              {data.traits && data.traits.map((trait, idx) => (
                <div key={idx} className="shop-trait-item">
                  <img
                    src={`/assets/traits/${trait.name.toLowerCase()}.png`}
                    className="shop-trait-icon"
                    alt=""
                    onError={(e) => e.target.style.display = 'none'}
                  />
                  <span>{trait.name}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="shop-info-stripe">
            <span className="shop-name">{data.name}</span>
            <div className="shop-cost-wrapper">
              <span className="shop-cost-value">{data.cost}</span>
              <img src="/assets/other/gold.png" className="shop-gold-icon" alt="" />
            </div>
          </div>
        </div>

        <div className="champ-info-main">
          <ChampionAbility champion={data}/>
        </div>
      </div>

      {/* --- Filter Bar --- */}
      <div className="filter-bar">
        <div className="tab-switcher">
          {["artifact", "radiant"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`tab-button ${activeTab === tab ? 'active' : ''}`}
              style={{ backgroundColor: activeTab === tab ? buttonColor : 'transparent' }}
            >
              {tab}s
            </button>
          ))}
        </div>

        <div className="filter-options">
          <label className="filter-label">
            Show low sample size
            <input type="checkbox" checked={showLowSample} onChange={() => setShowLowSample(!showLowSample)} />
          </label>
          <label className="filter-label">
            Show niche items
            <input type="checkbox" checked={showInvalid} onChange={() => setShowInvalid(!showInvalid)} />
          </label>
        </div>
      </div>

      {/* --- Items Table --- */}
      <div className="stats-table-container">
        <table className="stats-table">
          <thead>
            <tr>
              <th onClick={() => requestSort('name')} className="champ-column-header">
                Item {getSortIcon('name')}
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
            {itemsToShow.sort((a, b) => {
              const valA = sortConfig.key === 'name' ? a[1].name : a[1][sortConfig.key];
              const valB = sortConfig.key === 'name' ? b[1].name : b[1][sortConfig.key];
              return sortConfig.direction === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
            }).map(([itemId, info]) => (
              <tr 
                key={itemId} 
                className={`stats-table-row ${!info.valid ? 'invalid-row' : ''}`}
                onClick={() => window.location.href=`/${activeTab === 'artifact' ? 'artifacts' : 'radiant'}/${itemId}`}
              >
                <td className="champ-cell">
                  <div className="table-icon-wrapper">
                    <img 
                      src={`${itemFolderPath}/${itemId}.png`} 
                      className="table-icon" 
                      alt={info.name}
                      onError={(e) => { e.target.src = "/assets/artifacts/tft_item_unknown.png" }}
                    />
                    {info.low_sample && <span className="low-sample-indicator">!</span>}
                  </div>
                  <span className="champ-name-text">{info.name}</span>
                </td>
                <td className="col-count">{info.count.toLocaleString()}</td>
                <td className="col-avg">{info.average_placement.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ChampionPage;