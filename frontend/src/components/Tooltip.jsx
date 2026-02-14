import { useState } from "react";

function Tooltip({ text, children, color = "#ff4e4e" }) {
  const [visible, setVisible] = useState(false);

  return (
    <div 
      style={{ position: "relative", display: "inline-block" }}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
    >
      {children}
      {visible && (
        <div style={{
          position: "absolute",
          bottom: "110%",
          left: "50%",
          transform: "translateX(-50%)",
          backgroundColor: "#1c1c1f",
          color: "white",
          padding: "8px 12px",
          borderRadius: "6px",
          border: `1px solid ${color}`,
          fontSize: "12px",
          whiteSpace: "nowrap",
          zIndex: 100,
          boxShadow: "0 4px 10px rgba(0,0,0,0.5)"
        }}>
          {text}
          <div style={{
            position: "absolute",
            top: "100%",
            left: "50%",
            marginLeft: "-5px",
            borderWidth: "5px",
            borderStyle: "solid",
            borderColor: `${color} transparent transparent transparent`
          }} />
        </div>
      )}
    </div>
  );
}

export default Tooltip;