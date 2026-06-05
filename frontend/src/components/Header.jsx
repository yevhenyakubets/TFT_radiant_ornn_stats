import { useNavigate, useLocation } from "react-router-dom";
import SearchBar from "./SearchBar";
import "../styles/Header.css";

function Header() {
  const navigate = useNavigate();
  const location = useLocation();

  const navItems = [
    { name: "Home", path: "/" },
    { name: "Champions", path: "/champions" },
    { name: "Artifacts", path: "/artifacts" },
    { name: "Radiant Items", path: "/radiant-items" },
  ];

  return (
    <header className="header">
      <div className="header-nav">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.name}
              onClick={() => navigate(item.path)}
              className={`header-nav-button ${isActive ? "active" : ""}`}
            >
              {item.name}
            </button>
          );
        })}
      </div>

      <div className="header-search-wrapper">
        <SearchBar className="header-search-input-field" />
      </div>
    </header>
  );
}

export default Header;