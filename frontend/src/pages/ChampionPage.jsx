import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import React from 'react';
import "../styles/common.css";
import "../styles/ChampionPage.css";
import { ItemTooltip } from "../components/ItemTooltip";
import { useTooltip } from "../hooks/useTooltip";
import { getRarityColor } from "../utils/helper";
import ChampionAbility from "../components/ChampionAbility";
import { useSortConfig } from "../hooks/useSortConfig";
import { getDeltaColor } from '../utils/helper';
import { apiClient } from '../api';


function ItemRow({ itemId, info, itemFolderPath, activeTab, isValid }) {
  const { visible, position, handleMouseEnter, handleMouseMove, handleMouseLeave } = useTooltip(400);
  const isGrayedOut = info.low_sample && !info.valid;

  return (
    <tr
      className={`stats-table-row ${isGrayedOut ? 'invalid-row' : ''}`}
      onClick={() => window.location.href = `/${activeTab === 'artifact' ? 'artifacts' : 'radiant-items'}/${itemId}`}
    >
      <td className="champ-cell">
        <div className="table-icon-wrapper"
          onMouseEnter={handleMouseEnter}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          <img
            src={`${itemFolderPath}/${itemId}.png`}
            className="table-icon"
            alt={info.name}
            onError={(e) => { e.target.src = "/assets/artifacts/tft_item_unknown.png"; }}
          />
        </div>
        <span className="champ-name-text">
          {info.name}
          </span>
          {(info.low_sample || !info.valid) && (
            <span className="warning-icon-trigger">
              <img 
                src="/assets/other/warning.png" 
                alt="Warning" 
                className="warning-icon-img" 
              />
              <div className="warning-popup">
                {info.low_sample && !info.valid 
                  ? "Low sample size & Item is not recommended" 
                  : info.low_sample 
                    ? "Low sample size - data may be unreliable" 
                    : "Item not recommended - item does not match champions role"}
              </div>
            </span>
          )}
      </td>
      <td className="col-count">{info.count.toLocaleString()}</td>
      <td className="col-delta" style={{ color: getDeltaColor(info.delta) }}>
        {info.delta !== null ? (info.delta > 0 ? `+${info.delta}` : info.delta) : '—'}
      </td>
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
  const [showOnlyRecommended, setShowOnlyRecommended] = useState(true);
  const [hideLowSample, setHideLowSample] = useState(true);

  const { sortConfig, requestSort, getSortIcon } = useSortConfig('average_placement');

useEffect(() => {
    let isMounted = true;
    apiClient.get(`/champions/${championId}`)
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
    const matchesValid = showOnlyRecommended ? info.valid : true;
    const matchesSample = hideLowSample ? !info.low_sample : true;
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
              style={{ backgroundColor: activeTab === tab ? 'var(--border-muted)' : 'transparent' }}
            >
              {tab === 'artifact' ? 'Artifacts' : 'Radiant Items'}
            </button>
          ))}
        </div>
        <div className="filter-options">
          <label className="filter-label">
            Hide low sample size
            <input type="checkbox" checked={hideLowSample} onChange={() => setHideLowSample(!hideLowSample)} />
          </label>
          <label className="filter-label">
            Show only recommended items
            <input type="checkbox" checked={showOnlyRecommended} onChange={() => setShowOnlyRecommended(!showOnlyRecommended)} />
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
              <th onClick={() => requestSort('delta')}>
                <div className="table-header-content">
                  <div className="info-icon-wrapper delta-info">
                    <span className="info-icon-trigger">ⓘ</span>
                    <div className="search-tooltip">
                      <strong>WHAT IS DELTA?</strong>
                      <p>Delta is the <span>placement difference</span> compared to the average placement of the item. Lower (negative) values are better!</p>
                    </div>
                  </div>
                  
                  <span>Delta</span>
                  {getSortIcon('delta')}
                </div>
              </th>
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