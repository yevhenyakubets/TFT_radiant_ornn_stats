import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/common.css";
import { ItemTooltip } from "../components/ItemTooltip";
import { useTooltip } from "../hooks/useTooltip";

function ItemCard({ item, config }) {
  const { visible, position, handleMouseEnter, handleMouseMove, handleMouseLeave } = useTooltip(400);
  const navigate = useNavigate();

  return (
    <div
      className="item-card-link"
      style={{ "--hover-color": config.themeColor, position: "relative" }}
      onClick={() => navigate(`/${config.linkPath}/${item.id}`)}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div className="image-container">
        <img
          src={`/assets/${config.assetFolder}/${item.id}.png`}
          alt={item.name}
          className="list-item-icon"
          style={{ borderColor: config.themeColor }}
          onError={(e) => { e.target.style.display = 'none'; }}
        />
      </div>
      <strong className="list-item-name">{item.name}</strong>
      <ItemTooltip
        itemId={item.id}
        itemType={config.linkPath === 'artifacts' ? 'artifact' : 'radiant'}
        visible={visible}
        position={position}
      />
    </div>
  );
}

function ItemListPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const location = useLocation();

  const isArtifact = location.pathname.includes("artifact");

  const config = isArtifact ? {
    title: "Artifacts",
    endpoint: "artifacts",
    assetFolder: "artifacts",
    themeColor: "#e65d08",
    linkPath: "artifacts"
  } : {
    title: "Radiant Items",
    endpoint: "radiant-items",
    assetFolder: "radiant_items",
    themeColor: "#c8aa6e",
    linkPath: "radiant-items"
  };

  useEffect(() => {
    let isMounted = true;
    fetch(`http://127.0.0.1:8000/${config.endpoint}`)
      .then(res => res.json())
      .then(data => {
        if (isMounted) { setItems(Object.values(data)); setLoading(false); }
      })
      .catch(err => {
        if (isMounted) { console.error("Fetch error:", err); setLoading(false); }
      });
    return () => { isMounted = false; };
  }, [config.endpoint]);

  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <div className="list-loading-container">Loading {config.title.toLowerCase()}...</div>;

  return (
    <div className="list-page-wrapper">
      <div className="list-header-row">
        <h1 className="list-page-title">{config.title}</h1>
        <input
          type="text"
          placeholder={`Search ${config.title.toLowerCase()}...`}
          className="list-search-input"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="item-grid">
        {filteredItems.length > 0 ? (
          filteredItems.map(item => (
            <ItemCard key={item.id} item={item} config={config} />
          ))
        ) : (
          <div className="no-results">No {config.title.toLowerCase()} found matching "{searchTerm}"</div>
        )}
      </div>
    </div>
  );
}

export default ItemListPage;