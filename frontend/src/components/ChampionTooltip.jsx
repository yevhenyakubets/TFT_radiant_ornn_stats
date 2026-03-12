import { useState, useEffect } from "react";
import "../styles/Tooltip.css";

const cache = {};

export function ChampionTooltip({ championId, visible, position }) {
  const [data, setData] = useState(() => cache[championId] || null);

useEffect(() => {
  if (!visible || !championId || cache[championId]) return;
  fetch(`http://127.0.0.1:8000/champions/${championId}`)
    .then(res => res.json())
    .then(json => {
      cache[championId] = json;
      setData(json);
    })
    .catch(() => {});
}, [visible, championId]);

  if (!visible || !data) return null;

  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "rgb(24, 36, 49)";
      case 2: return "rgb(20, 77, 29)";
      case 3: return "rgb(28, 52, 93)";
      case 4: return "rgb(102, 20, 79)";
      case 5:
      case 7: return "rgb(134, 84, 11)";
      default: return "#1a1a1a";
    }
  };

  const rarityColor = getRarityColor(data.cost);

  return (
    <div
      className="tooltip-container champion-tooltip"
      style={{ top: position.y, left: position.x }}
    >
      {/* Shop Card */}
      <div className="shop-card" style={{ "--rarity-color": rarityColor, cursor: "default", width: "100%" }}>
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
                  onError={(e) => e.target.style.display = "none"}
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

      {/* Ability Section */}
      {data.ability_name && (
        <div className="tooltip-ability">
          <div className="tooltip-ability-header">
            <img
              src={`/assets/ability_icons/${championId}.png`}
              alt={data.ability_name}
              className="tooltip-ability-icon"
              onError={(e) => e.target.style.display = "none"}
            />
            <span className="tooltip-ability-name">{data.ability_name}</span>
          </div>
          {data.ability_description && (
            <p className="tooltip-ability-desc">
              {data.ability_description.split("<keyword>")[0].split("\n").filter(l => l.trim()).map((line, i) => (
                <span key={i} style={{ display: "block" }}>{line}</span>
              ))}
            </p>
          )}
        </div>
      )}
    </div>
  );
}