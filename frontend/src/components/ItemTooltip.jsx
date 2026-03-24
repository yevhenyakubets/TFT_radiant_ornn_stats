import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import "../styles/Tooltip.css";
import ItemDescription from "./ItemDescription";
import { apiClient } from '../api';

const cache = {};

export function ItemTooltip({ itemId, itemType, visible, position }) {
  const [data, setData] = useState(() => (itemId ? cache[itemId] : null) || null);

useEffect(() => {
  if (!visible || !itemId || cache[itemId]) return;

  const endpoint = itemType === 'artifact' ? 'artifacts' : 'radiant-items';

  apiClient.get(`/${endpoint}/${itemId}`)
    .then(json => {
      cache[itemId] = json;
      setData(json);
    })
    .catch(err => console.error(`Error fetching ${itemType}:`, err));

}, [visible, itemId, itemType]);

  if (!visible || !data || !itemId) return null;

  return createPortal(
    <div className="tooltip-container item-tooltip" style={{ top: position.y, left: position.x }}>
      <div className="tooltip-item-header">
        <img
          src={`/assets/${itemType === 'artifact' ? 'artifacts' : 'radiant_items'}/${itemId}.png`}
          alt={data.name}
          className="tooltip-item-icon"
          onError={(e) => e.target.style.display = "none"}
        />
        <div className="tooltip-item-header-text">
          <span className="tooltip-item-name">{data.name}</span>
          <ItemDescription data={data} showDescription={false} />
        </div>
      </div>
      <div className="tooltip-item-body">
        <ItemDescription data={data} showStats={false} />
      </div>
    </div>,
    document.body
  );
}