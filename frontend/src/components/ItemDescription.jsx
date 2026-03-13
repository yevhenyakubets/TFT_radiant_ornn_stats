import { formatItemDescription, stat_map, formatStatValue } from "../utils/helper";

function ItemDescription({ data, showStats = true, showDescription = true }) {
  const parsed = formatItemDescription(data.description);

  return (
    <>
      {showStats && data.stats && Object.keys(data.stats).some(k => k in stat_map) && (
        <div className="stats-row">
          {Object.entries(data.stats)
            .filter(([key]) => key in stat_map)
            .map(([key, val]) => (
              <div key={key}>
                <img className="stat-image" src={`/assets/stats/${stat_map[key]}.png`} alt={key} />
                <span>{formatStatValue(val, key)}</span>
              </div>
            ))}
        </div>
      )}

      {showDescription && parsed && (
        <div className="item-description">
          <div className="main-description-text">
            {parsed.mainBody.map((line, i) => (
              <p key={i} style={{ margin: '4px 0' }}>{line}</p>
            ))}
          </div>
          {parsed.keywords.length > 0 && (
            <div className="keywords-container">
              {parsed.keywords.map((kw, idx) => (
                <p key={idx} className="keyword-item"> {kw}</p>
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
}

export default ItemDescription;