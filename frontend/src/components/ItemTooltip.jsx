import { useState, useEffect } from "react";
import { createPortal } from "react-dom";  // missing
import "../styles/Tooltip.css";

const cache = {};

const stat_map = {
  "AD": "AD", "AP": "AP", "AS": "AS", "Armor": "Armor",
  "Health": "Health", "MagicResist": "MR", "CritChance": "CritChance",
  "BuffDamageAmp": "scaleDA", "ManaRegen": "scalemanaregen",
  "{cd951938}": "scaleDR", "StatOmnivamp": "scaleSV", "DamageAmp": "scaleDA"
};

const formatStatValue = (value, key) => {
  if (["BuffDamageAmp", "AD", "StatOmnivamp", "DamageAmp", "{cd951938}"].includes(key)) {
    return `+${Math.round(value * 100)}%`;
  }
  if (["AS", "CritChance"].includes(key)) return `+${Math.round(value)}%`;
  return `+${Math.round(value)}`;
};

export function ItemTooltip({ itemId, itemType, visible, position }) {
  const [data, setData] = useState(() => cache[itemId] || null);

  useEffect(() => {
    if (!visible || !itemId || cache[itemId]) return;
    const endpoint = itemType === 'artifact' ? 'artifacts' : 'radiant-items';
    fetch(`http://127.0.0.1:8000/${endpoint}/${itemId}`)
      .then(res => res.json())
      .then(json => {
        cache[itemId] = json;
        setData(json);
      })
      .catch(() => {});
  }, [visible, itemId, itemType]);

  if (!visible || !data) return null;

  return createPortal(
    <div className="tooltip-container item-tooltip" style={{ top: position.y, left: position.x }}>
      <div className="tooltip-item-header">
        <img
          src={`/assets/${itemType === 'artifact' ? 'artifacts' : 'radiant_items'}/${itemId}.png`}
          alt={data.name}
          className="tooltip-item-icon"
          onError={(e) => e.target.style.display = "none"}
        />
        <span className="tooltip-item-name">{data.name}</span>
      </div>

      {data.stats && Object.keys(data.stats).some(k => k in stat_map) && (
        <div className="tooltip-stats-row">
          {Object.entries(data.stats)
            .filter(([key]) => key in stat_map)
            .map(([key, val]) => (
              <div key={key} className="tooltip-stat-pill">
                <img src={`/assets/stats/${stat_map[key]}.png`} alt={key} className="tooltip-stat-icon" />
                <span>{formatStatValue(val, key)}</span>
              </div>
            ))}
        </div>
      )}

      {data.description && (
        <p className="tooltip-description">
          {data.description.split("<keyword>")[0].split("\n").filter(l => l.trim()).map((line, i) => (
            <span key={i} style={{ display: "block" }}>{line}</span>
          ))}
        </p>
      )}
    </div>,
    document.body
  );
}