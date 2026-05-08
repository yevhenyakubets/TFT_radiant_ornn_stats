import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import React from 'react';
import "../styles/common.css";
import "../styles/ItemPage.css";
import { ChampionTooltip } from "../components/ChampionTooltip";
import { useTooltip } from "../hooks/useTooltip";
import { useSortConfig } from "../hooks/useSortConfig";
import { getDeltaColor, getRarityColor } from "../utils/helper";
import ItemDescription from "../components/ItemDescription";
import { apiClient } from '../api';

function ChampionRow({ champId, info }) {
  const { visible, position, handleMouseEnter, handleMouseMove, handleMouseLeave } = useTooltip(400);
  const borderColor = getRarityColor(info.cost);
  // Matches the logic in ChampionPage: gray out if both low sample and not valid
  const isGrayedOut = info.low_sample && !info.valid;

  return (
    <tr
      className={`stats-table-row ${isGrayedOut ? 'invalid-row' : ''}`}
      onClick={() => window.location.href = `/champions/${champId}`}
    >
      <td className="champ-cell">
        <div 
          className="table-icon-wrapper"
          onMouseEnter={handleMouseEnter}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          <img
            src={`/assets/champ_logos/${champId}.png`}
            style={{ borderColor: borderColor, borderStyle: 'solid' }}
            className="table-icon champion-cost-border"
            alt={info.name}
          />
        </div>
        <span className="champ-name-text">{info.name}</span>
        
        {(info.low_sample || !info.valid) && (
          <span className="warning-icon-trigger">
            <img 
              src="/assets/other/warning.png" 
              alt="Warning" 
              className="warning-icon-img" 
            />
            <div className="warning-popup">
              {info.low_sample && !info.valid 
                ? "Low sample size & Champion is not recommended" 
                : info.low_sample 
                  ? "Low sample size - data may be unreliable" 
                  : "Champion not recommended - champion does not match champions role"}
            </div>
          </span>
        )}
      </td>
      <td className="col-count">{info.count.toLocaleString()}</td>
      <td className="col-delta" style={{ color: getDeltaColor(info.delta) }}>
        {info.delta !== null ? (info.delta > 0 ? `+${info.delta}` : info.delta) : '—'}
      </td>
      <td className="col-avg">{info.average_placement.toFixed(2)}</td>
      <ChampionTooltip championId={champId} visible={visible} position={position} />
    </tr>
  );
}

function ItemPage() {
  const { itemId } = useParams();
  const location = useLocation();
  const isArtifact = location.pathname.includes("artifact");

  const { sortConfig, requestSort, getSortIcon } = useSortConfig('delta');

  const config = isArtifact ? {
    endpoint: "artifacts",
    assetFolder: "artifacts",
  } : {
    endpoint: "radiant-items",
    assetFolder: "radiant_items",
  };

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOnlyRecommended, setShowOnlyRecommended] = useState(true);
  const [hideLowSample, setHideLowSample] = useState(true);

  useEffect(() => {
    let isMounted = true;
    apiClient.get(`/${config.endpoint}/${itemId}`)
      .then((json) => {
        if (isMounted) { setData(json); setLoading(false); }
      })
      .catch(() => {
        if (isMounted) { setData({ error: "Failed to fetch data" }); setLoading(false); }
      });
    return () => { isMounted = false; };
  }, [itemId, config.endpoint]);

  if (loading) return <div className="loading-state">Loading...</div>;
  if (data.error) return <div className="error-state">{data.error}</div>;

  const championsToShow = Object.entries(data.champions || {}).filter(([, info]) => {
    const matchesValid = showOnlyRecommended ? info.valid : true;
    const matchesSample = hideLowSample ? !info.low_sample : true;
    return matchesValid && matchesSample;
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
      <div className="item-header">
        <img
          className="item-image"
          src={`/assets/${config.assetFolder}/${itemId}.png`}
          alt={data.name}
        />
        <div className="item-info-container">
          <h1 className="item-name">{data.name}</h1>
          <ItemDescription data={data} showDescription={false} />
        </div>
        <div className="item-description">
          <ItemDescription data={data} showStats={false} />
        </div>
      </div>

      <div className="filter-bar">
        <h2 className="filter-bar-title">Best users of {data.name}</h2>
        <div className="filter-options">
          <label className="filter-label">
            <input type="checkbox" checked={hideLowSample} onChange={() => setHideLowSample(!hideLowSample)} />
            Hide low sample size
          </label>
          <label className="filter-label">
            <input type="checkbox" checked={showOnlyRecommended} onChange={() => setShowOnlyRecommended(!showOnlyRecommended)} />
            Show only recommended champions
          </label>
        </div>
      </div>

      <div className="stats-table-container">
        <table className="stats-table">
          <thead>
            <tr>
              <th onClick={() => requestSort('name')} className="champ-column-header">
                Champion {getSortIcon('name')}
              </th>
              <th onClick={() => requestSort('count')}>Frequency {getSortIcon('count')}</th>
              <th onClick={() => requestSort('delta')}>
                <div className="table-header-content">
                  <div className="info-icon-wrapper delta-info">
                    <span className="info-icon-trigger">ⓘ</span>
                    <div className="search-tooltip">
                      <strong>WHAT IS DELTA?</strong>
                      <p>Delta is the <span>placement difference</span> compared to the average placement of the champion. Lower (negative) values are better!</p>
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
            {sortedData.map(([champId, info]) => (
              <ChampionRow key={champId} champId={champId} info={info} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default ItemPage;