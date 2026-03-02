import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import "../styles/ItemListPage.css";

function ItemListPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState(""); // New state for searching
  const location = useLocation();
  const navigate = useNavigate();

  const isArtifact = location.pathname.includes("artifact");
  
  const config = isArtifact ? {
    title: "Artifacts",
    endpoint: "artifacts",
    assetFolder: "artifacts",
    themeColor: "#c8aa6e",
    linkPath: "artifacts"
  } : {
    title: "Radiant Items",
    endpoint: "radiant-items",
    assetFolder: "radiant_items",
    themeColor: "#31c1ca",
    linkPath: "radiant-items"
  };

  useEffect(() => {
  let isMounted = true;
  // REMOVED: setLoading(true) from here to avoid cascading renders

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

  // Filter items based on the search term
  const filteredItems = items.filter((item) =>
    item.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <div className="list-loading">Loading {config.title.toLowerCase()}...</div>;
  }

  return (
    <div className="item-list-wrapper">
      <div className="list-header">
          <h1 
            className="list-title" 
            style={{ borderBottomColor: config.themeColor }}
          >
            {config.title}
          </h1>

          <div className="list-search-container">
            <input
              type="text"
              placeholder={`Search ${config.title.toLowerCase()}...`}
              className="list-search-input"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>


      <div className="item-grid">
        {filteredItems.length > 0 ? (
          filteredItems.map(item => (
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
          ))
        ) : (
          <div className="no-results">No {config.title.toLowerCase()} found matching "{searchTerm}"</div>
        )}
      </div>
    </div>
  );
}

export default ItemListPage;