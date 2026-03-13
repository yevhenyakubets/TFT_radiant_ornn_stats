import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import React from 'react';
import "../styles/common.css";
import "../styles/ChampionPage.css";
import { ItemTooltip } from "../components/ItemTooltip";
import { useTooltip } from "../hooks/useTooltip";
import { getRarityColor } from "../utils/helper";
import { ChampionAbility } from "../components/ChampionAbility";
import { useSortConfig } from "../hooks/useSortConfig";


function ItemRow({ itemId, info, itemFolderPath, activeTab, isValid }) {
  const { visible, position, handleMouseEnter, handleMouseLeave } = useTooltip(400);

  return (
    <tr
      className={`stats-table-row ${!isValid ? 'invalid-row' : ''}`}
      onClick={() => window.location.href = `/${activeTab === 'artifact' ? 'artifacts' : 'radiant-items'}/${itemId}`}
    >
      <td className="champ-cell"
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <div className="table-icon-wrapper">
          <img
            src={`${itemFolderPath}/${itemId}.png`}
            className="table-icon"
            alt={info.name}
            onError={(e) => { e.target.src = "/assets/artifacts/tft_item_unknown.png"; }}
          />
          {info.low_sample && <span className="low-sample-indicator">!</span>}
        </div>
        <span className="champ-name-text">{info.name}</span>
      </td>
      <td className="col-count">{info.count.toLocaleString()}</td>
      <td className="col-avg">{info.average_placement.toFixed(2)}</td>
      <ItemTooltip itemId={itemId} itemType={activeTab === 'artifact' ? 'artifact' : 'radiant'} visible={visible} position={position} />
    </tr>
  );
}

function ChampionPage() {
  const { championId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("artifact");
  const [showInvalid, setShowInvalid] = useState(false);
  const [showLowSample, setShowLowSample] = useState(false);

  const buttonColor = "rgb(5, 30, 41)";

  const { sortConfig, requestSort, getSortIcon } = useSortConfig('average_placement');

  useEffect(() => {
    let isMounted = true;
    fetch(`http://127.0.0.1:8000/champions/${championId}`)
      .then(res => res.json())
      .then(json => {
        if (isMounted) { setData(json); setLoading(false); }
      })
      .catch(() => {
        if (isMounted) { setData({ error: "Failed to load champion data" }); setLoading(false); }
      });
    return () => { isMounted = false; };
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

      <div className="champion-header">
        <div className="shop-card" style={{ "--rarity-color": rarityColor, width: "220px", cursor: "default" }}>
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
          <ChampionAbility champion={data} />
        </div>
      </div>

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

      <div className="stats-table-container">
        <table className="stats-table">
          <thead>
            <tr>
              <th onClick={() => requestSort('name')} className="champ-column-header">
                Item {getSortIcon('name')}
              </th>
              <th onClick={() => requestSort('count')}>Frequency {getSortIcon('count')}</th>
              <th onClick={() => requestSort('average_placement')}>Avg Place {getSortIcon('average_placement')}</th>
            </tr>
          </thead>
          <tbody>
            {itemsToShow.sort((a, b) => {
              const valA = sortConfig.key === 'name' ? a[1].name : a[1][sortConfig.key];
              const valB = sortConfig.key === 'name' ? b[1].name : b[1][sortConfig.key];
              return sortConfig.direction === 'asc' ? (valA > valB ? 1 : -1) : (valA < valB ? 1 : -1);
            }).map(([itemId, info]) => (
              <ItemRow
                key={itemId}
                itemId={itemId}
                info={info}
                itemFolderPath={itemFolderPath}
                activeTab={activeTab}
                isValid={info.valid}
              />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ChampionPage;