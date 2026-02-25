import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/ItemListPage.css";

function ItemListPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  // Detect type from URL
  const isArtifact = location.pathname.includes("artifact");
  
  const config = isArtifact ? {
    title: "Artifacts",
    endpoint: "artifacts",
    assetFolder: "artifacts",
    themeColor: "#c8aa6e", // Gold
    linkPath: "artifacts"
  } : {
    title: "Radiant Items",
    endpoint: "radiant-items",
    assetFolder: "radiant_items",
    themeColor: "#31c1ca", // Cyan
    linkPath: "radiant-items"
  };



useEffect(() => {
  // 2. Remove setLoading(true) from here. 
  // It's already true on mount, and the dependency [config.endpoint] 
  // will handle the state transition during navigation.

  let isMounted = true;

  fetch(`http://127.0.0.1:8000/${config.endpoint}`)
    .then(res => res.json())
    .then(data => {
      if (isMounted) {
        setItems(Object.values(data));
        setLoading(false);
      }
    })
    .catch(err => {
      if (isMounted) {
        console.error("Fetch error:", err);
        setLoading(false);
      }
    });

  return () => { isMounted = false; };
}, [config.endpoint]);

  if (loading) {
    return <div className="list-loading">Loading {config.title.toLowerCase()}...</div>;
  }

  return (
    <div className="item-list-wrapper">
      <h1 
        className="list-title" 
        style={{ borderBottomColor: config.themeColor }}
      >
        {config.title}
      </h1>

      <div className="item-grid">
        {items.map(item => (
          <div
            key={item.id}
            className="item-card-link"
            style={{ "--hover-color": config.themeColor }}
            onClick={() => navigate(`/${config.linkPath}/${item.id}`)}
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
          </div>
        ))}
      </div>
    </div>
  );
}

export default ItemListPage;