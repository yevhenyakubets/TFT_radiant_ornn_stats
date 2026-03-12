import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import "../styles/common.css";
import "../styles/ItemPage.css";
import { ChampionTooltip } from "../components/ChampionTooltip";
import { useTooltip } from "../hooks/useTooltip";

function ChampionRow({ champId, info }) {
  const { visible, position, handleMouseEnter, handleMouseLeave } = useTooltip(400);

  return (
    <tr
      className="stats-table-row"
      onClick={() => window.location.href = `/champions/${champId}`}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <td className="champ-cell">
        <div className="table-icon-wrapper">
          <img
            src={`/assets/champ_logos/${champId}.png`}
            className="table-icon"
            alt={info.name}
          />
          {info.low_sample && <span className="low-sample-indicator">!</span>}
        </div>
        <span className="champ-name-text">{info.name}</span>
      </td>
      <td className="col-count">{info.count.toLocaleString()}</td>
      <td className="col-avg">{info.average_placement.toFixed(2)}</td>
      <ChampionTooltip championId={champId} visible={visible} position={position} />
    </tr>
  );
}

function ItemPage() {
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

  const config = isArtifact ? {
    endpoint: "artifacts",
    assetFolder: "artifacts",
  } : {
    endpoint: "radiant-items",
    assetFolder: "radiant_items",
  };

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInvalid, setShowInvalid] = useState(false);
  const [showLowSample, setShowLowSample] = useState(false);

  const getSortIcon = (key) => {
    if (sortConfig.key !== key) return <span className="sort-arrow-placeholder"></span>;
    return sortConfig.direction === 'asc' ? ' ▲' : ' ▼';
  };

  const stat_map = {
    "AD": "AD", "AP": "AP", "AS": "AS", "Armor": "Armor",
    "Health": "Health", "MagicResist": "MR", "CritChance": "CritChance",
    "BuffDamageAmp": "scaleDA", "ManaRegen": "scalemanaregen",
    "{cd951938}": "scaleDR", "StatOmnivamp": "scaleSV",
    "DamageAmp": "scaleDA", "BonusDamage": "scaleDA"
  };

  const formatStatValue = (value, key) => {
    if (["BuffDamageAmp", "AD", "StatOmnivamp", "DamageAmp", "{cd951938}", "BonusDamage"].includes(key)) {
      return `+${Math.round(value * 100)}%`;
    }
    if (["AS", "CritChance"].includes(key)) return `+${Math.round(value)}%`;
    return `+${Math.round(value)}`;
  };

  const formatItemDescription = (text) => {
    if (!text) return null;
    const parts = text.split("<keyword>");
    const mainBody = parts[0];
    const keywords = parts.slice(1);

    return (
      <>
        <div className="main-description-text">
          {mainBody.split('\n').filter(l => l.trim()).map((line, i) => (
            <p key={i} style={{ margin: '4px 0' }}>{line}</p>
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

  useEffect(() => {
    let isMounted = true;
    fetch(`http://127.0.0.1:8000/${config.endpoint}/${itemId}`)
      .then((res) => res.json())
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
    return (info.valid || showInvalid) && (!info.low_sample || showLowSample);
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
          <div className="stats-row">
            {data.stats && Object.entries(data.stats)
              .filter(([key]) => key in stat_map)
              .map(([key, val]) => (
                <div key={key}>
                  <img className="stat-image" src={`/assets/stats/${stat_map[key]}.png`} alt={key} />
                  <span>{formatStatValue(val, key)}</span>
                </div>
              ))}
          </div>
        </div>
        <div className="item-description">
          {formatItemDescription(data.description)}
        </div>
      </div>

      <div className="filter-bar">
        <h2 className="filter-bar-title">Best users of {data.name}</h2>
        <div className="filter-options">
          <label className="filter-label">
            Show low sample size
            <input type="checkbox" checked={showLowSample} onChange={() => setShowLowSample(!showLowSample)} />
          </label>
          <label className="filter-label">
            Show niche units
            <input type="checkbox" checked={showInvalid} onChange={() => setShowInvalid(!showInvalid)} />
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