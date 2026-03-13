import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Common.css";
import "../styles/ChampionListPage.css";
import { getRarityColor } from "../utils/helper";
import { ChampionTooltip } from "../components/ChampionTooltip";
import { useTooltip } from "../hooks/useTooltip";

const sortTraits = (traits) => {
  if (!traits) return [];
  return [...traits].sort((a, b) => {
    const order = { unique: 1, origin: 2, class: 3 };
    return (order[a.type] || 4) - (order[b.type] || 4);
  });
};

function ChampionCard({ champ }) {
  const { visible, position, handleMouseEnter,handleMouseMove, handleMouseLeave } = useTooltip(400);
  const navigate = useNavigate();
  const rarityColor = getRarityColor(champ.cost);
  const sortedTraits = sortTraits(champ.traits);

  return (
    <div
        className="shop-card"
        style={{ "--rarity-color": rarityColor }}
        onClick={() => navigate(`/champions/${champ.id}`)}
        onMouseEnter={handleMouseEnter}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
      >
      <div className="shop-splash-container">
        <img
          src={`/assets/champ_splashes/${champ.id}.png`}
          alt={champ.name}
          className="shop-splash-img"
          onError={(e) => { e.target.src = `/assets/champ_logos/${champ.id}.png`; }}
        />
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
      <div className="shop-info-stripe">
        <span className="shop-name">{champ.name}</span>
        <div className="shop-cost-wrapper">
          <span className="shop-cost-value">{champ.cost}</span>
          <img src="/assets/other/gold.png" className="shop-gold-icon" alt="" />
        </div>
      </div>
      <ChampionTooltip championId={champ.id} visible={visible} position={position} />
    </div>
  );
}

function ChampionsListPage() {
  const [champions, setChampions] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [loading, setLoading] = useState(true);

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

  if (loading) return <div className="list-loading-container">Loading Champions...</div>;

  return (
    <div className="list-page-wrapper">
      <div className="list-header-row">
        <h1 className="list-page-title">CHAMPIONS</h1>
        <input
          className="list-search-input"
          placeholder="Search..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="champions-shop-grid">
        {filteredChampions.map(champ => (
          <ChampionCard key={champ.id} champ={champ} />
        ))}
      </div>
    </div>
  );
}

export default ChampionsListPage;