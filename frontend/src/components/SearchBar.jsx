import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSearchData } from "../hooks/useSearchData.js";
import "../styles/SearchBar.css";

function SearchBar({ customStyles = {}, inputStyles = {} }) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const searchPool = useSearchData();
  const navigate = useNavigate();
  const wrapperRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const results = query.length > 1
    ? searchPool
        .filter(item => item.name?.toLowerCase().includes(query.toLowerCase()))
        .sort((a, b) => {
          const q = query.toLowerCase();
          const aName = a.name.toLowerCase();
          const bName = b.name.toLowerCase();
          const aStarts = aName.startsWith(q);
          const bStarts = bName.startsWith(q);
          if (aStarts && !bStarts) return -1;
          if (!aStarts && bStarts) return 1;
          return aName.localeCompare(bName);
        })
        .slice(0, 8)
    : [];

  const handleKeyDown = (e) => {
    if (!isOpen || results.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex(prev => (prev < results.length - 1 ? prev + 1 : 0));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex(prev => (prev > 0 ? prev - 1 : results.length - 1));
    } else if (e.key === "Enter") {
      if (activeIndex >= 0) {
        const item = results[activeIndex];
        navigate(item.route);
        setIsOpen(false);
        setQuery("");
      }
    } else if (e.key === "Escape") {
      setIsOpen(false);
    }
  };

  return (
    <div ref={wrapperRef} className="searchbar-wrapper" style={customStyles}>
      <input
        type="text"
        placeholder="Search champions or items..."
        value={query}
        onFocus={() => setIsOpen(true)}
        onChange={(e) => {
          setQuery(e.target.value);
          setIsOpen(true);
          setActiveIndex(-1);
        }}
        onKeyDown={handleKeyDown}
        className="searchbar-input"
        style={inputStyles}
      />

      {isOpen && results.length > 0 && (
        <div className="searchbar-dropdown">
          {results.map((item, index) => (
            <div
              key={`${item.type}-${item.id}`}
              className={`searchbar-result-item ${index === activeIndex ? "active" : ""}`}
              onMouseEnter={() => setActiveIndex(index)}
              onClick={() => {
                navigate(item.route);
                setIsOpen(false);
                setQuery("");
              }}
            >
              <img src={item.icon} alt="" className="searchbar-result-icon" />
              <div className="searchbar-result-text">
                <div className="searchbar-result-name">{item.name}</div>
                <div className="searchbar-result-type">{item.type}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchBar;