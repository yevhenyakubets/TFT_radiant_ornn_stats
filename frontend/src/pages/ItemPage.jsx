import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import "../styles/common.css";
import "../styles/ItemPage.css";
import { ChampionTooltip } from "../components/ChampionTooltip";
import { useTooltip } from "../hooks/useTooltip";
import { useSortConfig } from "../hooks/useSortConfig";
import ItemDescription from "../components/ItemDescription";

function ChampionRow({ champId, info }) {
  const { visible, position, handleMouseEnter, handleMouseMove, handleMouseLeave } = useTooltip(400);

  return (
    <tr
      className="stats-table-row"
      onClick={() => window.location.href = `/champions/${champId}`}
    >
      <td className="champ-cell"
        onMouseEnter={handleMouseEnter}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
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

  const { sortConfig, requestSort, getSortIcon } = useSortConfig('average_placement');

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