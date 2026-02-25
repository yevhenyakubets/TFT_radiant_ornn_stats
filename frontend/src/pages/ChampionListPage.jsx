import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ChampionListPage.css";

function ChampionsListPage() {
  const [champions, setChampions] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "#808080";
      case 2: return "#11b288";
      case 3: return "#207ac7";
      case 4: return "#c440da";
      case 5:
      case 7: return "#ffb93b";
      default: return "#ccc";
    }
  };

  useEffect(() => {
    let isMounted = true;
    fetch("http://127.0.0.1:8000/champions")
      .then(res => res.json())
      .then(data => {
        if (isMounted) {
          setChampions(data.champions);
          setLoading(false);
        }
      });
    return () => { isMounted = false; };
  }, []);

  if (loading) {
    return <div className="loading-container">Loading champions...</div>;
  }

  return (
    <div className="champions-list-wrapper">
      <h1 className="champions-list-title">Champions</h1>

      <div className="champions-grid">
        {champions.map(champ => {
          const rarityColor = getRarityColor(champ.cost);
          
          return (
            <div
              key={champ.id}
              className="champion-card"
              style={{ "--rarity-color": rarityColor }}
              onClick={() => navigate(`/champions/${champ.id}`)}
            >
              <div className="champ-icon-container">
                <img 
                  src={`/assets/champ_logos/${champ.id}.png`} 
                  alt={champ.name}
                  className="champ-list-icon"
                  onError={(e) => { e.target.style.display = 'none'; }}
                />
              </div>

              <strong className="champ-list-name">{champ.name}</strong>
              
              <div className="champ-list-cost">
                {champ.cost} Gold
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

export default ChampionsListPage;