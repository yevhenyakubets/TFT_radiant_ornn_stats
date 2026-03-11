// components/SearchBar.jsx
import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSearchData } from "../hooks/useSearchData";

function SearchBar({ customStyles = {}, inputStyles = {} }) {
  const [query, setQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const searchPool = useSearchData();
  const navigate = useNavigate();
  const wrapperRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

// inside SearchBar.jsx logic
const results = query.length > 1 
  ? searchPool
      .filter(item => item.name?.toLowerCase().includes(query.toLowerCase()))
      .sort((a, b) => {
        const q = query.toLowerCase();
        const aName = a.name.toLowerCase();
        const bName = b.name.toLowerCase();

        const aStarts = aName.startsWith(q);
        const bStarts = bName.startsWith(q);

        // If one starts with the query and the other doesn't, put the starter first
        if (aStarts && !bStarts) return -1;
        if (!aStarts && bStarts) return 1;

        // Otherwise, sort alphabetically
        return aName.localeCompare(bName);
      })
      .slice(0, 8)
  : [];

  return (
    <div ref={wrapperRef} style={{ position: "relative", width: "100%", ...customStyles }}>
      <input
        type="text"
        placeholder="Search champions or items..."
        value={query}
        onFocus={() => setIsOpen(true)}
        onChange={(e) => {
          setQuery(e.target.value);
          setIsOpen(true);
        }}
        style={{
          width: "100%",
          padding: "12px 16px",
          borderRadius: "8px",
          border: "1px solid #2d2d31",
          backgroundColor: "#0a0a0c",
          color: "white",
          outline: "none",
          fontFamily: "Beaufort W01 Regular",
          fontSize: "1.3rem",
          ...inputStyles   // <-- add this
        }}
      />

      {isOpen && results.length > 0 && (
        <div style={{
          position: "absolute",
          top: "110%",
          left: 0,
          right: 0,
          backgroundColor: "#16161a",
          border: "1px solid #2d2d31",
          borderRadius: "8px",
          zIndex: 2000,
          overflow: "hidden",
          boxShadow: "0 10px 25px rgba(0,0,0,0.5)"
        }}>
          {results.map(item => (
            <div
              key={`${item.type}-${item.id}`}
                onClick={() => {
                  navigate(item.route);
                  setIsOpen(false);
                  setQuery("");
                }}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "12px",
                  padding: "8px 15px", // Slightly tighter vertical padding
                  cursor: "pointer",
                  borderBottom: "1px solid #2d2d31",
                  transition: "background 0.2s"
                }}
                onMouseEnter={(e) => e.currentTarget.style.backgroundColor = "#2d2d31"}
                onMouseLeave={(e) => e.currentTarget.style.backgroundColor = "transparent"}
            >
              <img src={item.icon} alt="" style={{ width: "32px", height: "32px", borderRadius: "4px" }} />
              <div style={{ 
                display: "flex", 
                  flexDirection: "column", 
                  justifyContent: "center",
                  alignItems: "flex-start", // <--- Forces children to the left
                  lineHeight: "1.2",
                  textAlign: "left"
              }}>
                <div style={{ 
                  color: "white", 
                  fontSize: "1.1rem", 
                  fontWeight: "600",
                  margin: 0,
                  padding : 0,
                }}>
                  {item.name}
                </div>
                <div style={{ 
                  color: "#888", // Brightened slightly for readability
                  fontSize: "0.7rem", 
                  textTransform: "uppercase",
                  letterSpacing: "0.5px", // Cleaner "Beaufort" look
                  marginTop: "2px", // Precise control over the gap
                  marginLeft: 0,
                  marginRight: 0,
                  width: "100%",
                }}>
                  {item.type}
                </div>
              </div>  
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default SearchBar;