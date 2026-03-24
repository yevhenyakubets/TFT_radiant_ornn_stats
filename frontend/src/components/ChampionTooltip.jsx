import { useState, useEffect } from "react";
import "../styles/Tooltip.css";
import { getRarityColor } from "../utils/helper";
import ChampionAbility from "./ChampionAbility";
import { createPortal } from "react-dom";
import { apiClient } from '../api';

const cache = {};

export function ChampionTooltip({ championId, visible, position }) {
  const [data, setData] = useState(() => cache[championId] || null);

useEffect(() => {
  if (!visible || !championId || cache[championId]) return;

  apiClient.get(`/champions/${championId}`)
    .then(json => {
      cache[championId] = json;
      setData(json);
    })
    .catch((error) => {
      console.error("Failed to fetch champion:", error);
    });
    
}, [visible, championId]);

  if (!visible || !data) return null;

  const rarityColor = getRarityColor(data.cost);

  return createPortal(
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
          <ChampionAbility champion={data} />
        </div>
      )}
    </div>,
    document.body
  );
}