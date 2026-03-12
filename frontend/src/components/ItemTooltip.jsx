import "../styles/Tooltip.css";

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

export function ItemTooltip({ item, assetFolder, visible, position }) {
  if (!visible || !item) return null;

  return (
    <div
      className="tooltip-container item-tooltip"
      style={{ top: position.y, left: position.x }}
    >
      <div className="tooltip-item-header">
        <img
          src={`/assets/${assetFolder}/${item.id}.png`}
          alt={item.name}
          className="tooltip-item-icon"
          onError={(e) => e.target.style.display = "none"}
        />
        <span className="tooltip-item-name">{item.name}</span>
      </div>

      {item.stats && Object.keys(item.stats).some(k => k in stat_map) && (
        <div className="tooltip-stats-row">
          {Object.entries(item.stats)
            .filter(([key]) => key in stat_map)
            .map(([key, val]) => (
              <div key={key} className="tooltip-stat-pill">
                <img
                  src={`/assets/stats/${stat_map[key]}.png`}
                  alt={key}
                  className="tooltip-stat-icon"
                />
                <span>{formatStatValue(val, key)}</span>
              </div>
            ))}
        </div>
      )}

      {item.description && (
        <p className="tooltip-description">{item.description}</p>
      )}
    </div>
  );
}