import SearchBar from "../components/SearchBar";
import { useNavigate } from "react-router-dom";
import "../styles/HomePage.css";

function HomePage() {
  const navigate = useNavigate();

  const navButtons = [
    {
      name: "Champions",
      path: "/champions",
      icon: "champions.png", // Corrected filename
      description: "Find the best items for specified champions."
    },
    {
      name: "Artifacts",
      path: "/artifacts",
      icon: "artifacts.png", // Corrected filename
      description: "Find the best users for specified Artifacts."
    },
    {
      name: "Radiant Items",
      path: "/radiant-items",
      icon: "radiant-items.png", // Corrected filename
      description: "Find the best users for specified Radiant items."
    }
  ];

  return (
    <div className="home-container">
      <div className="hero-section">
        <h1 className="hero-title">
          TFT <span className="highlight">ARTIFACTS AND RADIANT ITEMS</span>
        </h1>
        <p className="hero-subtitle">Analyze placements and optimize your itemization.</p>
        <p className="hero-subtitle">Find the best items for champions, as well as best users for specific items</p>
      </div>

      <div className="search-bar-wrapper">
        <SearchBar customStyles={{ fontSize: "1.6rem" }} />
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

      <div className="footer-decoration">DATA POWERED BY RIOT GAMES API</div>
    </div>
  );
}

export default HomePage;