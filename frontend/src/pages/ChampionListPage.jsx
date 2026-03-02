import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ChampionListPage.css";

function ChampionsListPage() {
  const [champions, setChampions] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "rgb(24, 36, 49)";
      case 2: return "rgb(20, 77, 29)";
      case 3: return "rgb(28, 52, 93)";
      case 4: return "rgb(102, 20, 79)";
      case 5:
      case 7: return "rgb(134, 84, 11)";
      default: return "#ccc";
    }
  };

  // Helper to sort traits: Unique -> Origin -> Class
  const sortTraits = (traits) => {
    if (!traits) return [];
    return [...traits].sort((a, b) => {
      const order = { unique: 1, origin: 2, class: 3 };
      return (order[a.type] || 4) - (order[b.type] || 4);
    });
  };

  useEffect(() => {
    fetch("http://127.0.0.1:8000/champions")
      .then(res => res.json())
      .then(data => {
        setChampions(data.champions);
        setLoading(false);
      });
  }, []);

  const filteredChampions = champions
    .filter(champ => {
      const query = searchTerm.toLowerCase().trim();
      if (!query) return true;
      if (query.startsWith("#")) {
        const tQ = query.substring(1);
        return champ.traits?.some(t => (typeof t === 'string' ? t : t.name).toLowerCase().includes(tQ));
      }
      return champ.name.toLowerCase().includes(query);
    })
    .sort((a, b) => {
      if (a.cost !== b.cost) return a.cost - b.cost;
      return a.name.localeCompare(b.name);
    });

  if (loading) return <div className="loading-container">Loading Shop...</div>;

  return (
    <div className="champions-list-wrapper">
      <div className="champions-header-row">
        <h1 className="champions-list-title">CHAMPIONS</h1>
        <input 
          className="champ-search-input"
          placeholder="Search..." 
          onChange={(e) => setSearchTerm(e.target.value)} 
        />
      </div>

      <div className="champions-shop-grid">
        {filteredChampions.map(champ => {
          const rarityColor = getRarityColor(champ.cost);
          const sortedTraits = sortTraits(champ.traits);

          return (
            <div
              key={champ.id}
              className="shop-card"
              style={{ "--rarity-color": rarityColor }}
              onClick={() => navigate(`/champions/${champ.id}`)}
            >
              {/* Top Section: Splash Art */}
              <div className="shop-splash-container">
                <img 
                  src={`/assets/champ_splashes/${champ.id}.png`} 
                  alt={champ.name}
                  className="shop-splash-img"
                  onError={(e) => { e.target.src = `/assets/champ_logos/${champ.id}.png`; }}
                />
                
                {/* Overlay: Traits at bottom left */}
                <div className="shop-traits-overlay">
                  {sortedTraits.map((trait, idx) => (
                    <div key={idx} className="shop-trait-item">
                      <img 
                        src={`/assets/traits/${trait.name.toLowerCase()}.png`} 
                        className="shop-trait-icon"
                        alt=""
                        onError={(e) => e.target.style.display = 'none'}
                      />
                      <span>{trait.name}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bottom Stripe: Name and Cost */}
              <div className="shop-info-stripe">
                <span className="shop-name">{champ.name}</span>
                <div className="shop-cost-wrapper">
                  <span className="shop-cost-value">{champ.cost}</span>
                  <img src="/assets/other/gold.png" className="shop-gold-icon" alt="" />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ChampionsListPage;