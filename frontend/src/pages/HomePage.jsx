import SearchBar from "../components/SearchBar";
import { useNavigate } from "react-router-dom";
import "../styles/HomePage.css";

function HomePage() {
  const navigate = useNavigate();

  const navButtons = [
    {
      name: "Champions",
      path: "/champions",
      icon: "champions.png",
      description: "Find the best items for specified champions."
    },
    {
      name: "Artifacts",
      path: "/artifacts",
      icon: "artifacts.png",
      description: "Find the best users for specified Artifacts."
    },
    {
      name: "Radiant Items",
      path: "/radiant-items",
      icon: "radiant-items.png",
      description: "Find the best users for specified Radiant items."
    }
  ];

  return (
    <div className="home-container">
      <div className="header-section">
        <h1 className="header-title">
          TFT <span className="highlight">ARTIFACTS AND RADIANT ITEMS</span>
        </h1>
        <p className="header-subtitle">Analyze placements and optimize your itemization.</p>
        <p className="header-subtitle">Find the best items for champions, as well as best users for specific items</p>
      </div>

      <div className="search-bar-wrapper" style={{ maxWidth: "800px" }}> {/* Changed from 600px */}
        <SearchBar inputStyles={{ fontSize: "1.6rem", padding: "18px 24px", borderRadius: "12px" }} />
      </div>

      <div className="nav-grid">
        {navButtons.map((btn) => (
          <div
            key={btn.name}
            className="nav-card"
            onClick={() => navigate(btn.path)}
          >
            <div className="nav-card-header">
              <div className="icon-box">
                 <img 
                  src={`/assets/other/${btn.icon}`} 
                  alt="" 
                  className="nav-icon"
                  onError={(e) => e.target.style.display = 'none'}
                />
              </div>
              <h2 className="nav-card-title">
                {btn.name}
              </h2>
            </div>
            <p className="nav-card-description">
              {btn.description}
            </p>
          </div>
        ))}
      </div>
    </div>
    
  );
}

export default HomePage;