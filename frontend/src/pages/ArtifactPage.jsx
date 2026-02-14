import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tooltip from "../components/Tooltip";

function ArtifactPage() {
  const { artifactId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showInvalid, setShowInvalid] = useState(false);
  const [showLowSample, setShowLowSample] = useState(false); 

  const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "#808080";
      case 2: return "#11b288";
      case 3: return "#207ac7";
      case 4: return "#c440da";
      case 5:
      case 7: return "#ffb93b";
      default: return "#c8aa6e"; 
    }
  };

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/artifacts/${artifactId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [artifactId]);

  if (loading) return <div style={{ color: "white", padding: "20px" }}>Loading...</div>;
  if (data.error) return <div style={{ color: "red", padding: "20px" }}>{data.error}</div>;

const championsToShow = Object.entries(data.champions).filter(([, info]) => {
  // Logic: Must pass both validity and sample size checks unless toggled
  const isCorrectValidity = info.valid || showInvalid;
  const isCorrectSample = !info.low_sample || showLowSample;
  return isCorrectValidity && isCorrectSample;
});

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh", color: "white", fontFamily: "sans-serif" }}>
      
      {/* --- Item Header --- */}
      <div style={{ 
        display: "flex", 
        alignItems: "center", 
        gap: "24px", 
        marginBottom: "40px", 
        padding: "20px",
        borderRadius: "12px",
        background: `linear-gradient(90deg, #1c1c1f 0%, transparent 100%)`,
        borderLeft: `6px solid #c8aa6e` 
      }}>
        <img 
          src={`/assets/artifacts/${artifactId}.png`} 
          alt={data.name} 
          style={{ width: "100px", height: "100px", borderRadius: "12px", border: `2px solid #c8aa6e`, padding: "5px", backgroundColor: "#000" }}
        />
        <div>
          <h1 style={{ margin: 0, fontSize: "2.5rem" }}>{data.name}</h1>
          <div style={{ color: "#c8aa6e", fontWeight: "bold", textTransform: "uppercase", fontSize: "0.9rem", marginTop: "4px" }}>
            Ornn Artifact
          </div>
        </div>
      </div>

<div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", borderBottom: "1px solid #2d2d31", paddingBottom: "10px" }}>
    <h2 style={{ margin: 0, fontSize: "1.5rem" }}>Best Champions</h2>
    
    <div style={{ display: "flex", gap: "20px" }}>
      <label style={{ color: "#888", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
        Show low sample size
        <input type="checkbox" checked={showLowSample} onChange={() => setShowLowSample(!showLowSample)} />
      </label>
      <label style={{ color: "#888", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
        Show niche units
        <input type="checkbox" checked={showInvalid} onChange={() => setShowInvalid(!showInvalid)} />
      </label>
    </div>
  </div>

      {/* --- Champions Grid --- */}
      <div style={{ 
        display: "grid", 
        gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", 
        gap: "16px" 
      }}>
        {championsToShow.map(([champId, info]) => {
          const champColor = getRarityColor(info.cost);
          
          // ADDED: Card content defined as a variable to wrap in Tooltip conditionally
          const champCard = (
            <div 
              style={{
                backgroundColor: "#16161a",
                padding: "16px",
                borderRadius: "10px",
                display: "flex",
                alignItems: "center",
                gap: "16px",
                // ADDED: Red dashed border for low sample size
                border: info.low_sample ? "1px dashed #ff4e4e" : `1px solid #2d2d31`,
                // ADDED: Lower opacity for invalid items
                opacity: info.valid ? 1 : 0.5,
                transition: "transform 0.2s ease",
                cursor: "pointer"
              }}
              onClick={() => window.location.href = `/champions/${champId}`}
            >
              <img 
                src={`/assets/champ_logos/${champId}.png`} 
                alt={info.name}
                style={{ width: "56px", height: "56px", borderRadius: "50%", border: `2px solid ${champColor}` }}
              />
              
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: "bold", fontSize: "1.1rem" }}>{info.name}</div>
              </div >
                            <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "2px" }}>
                Frequency: <span style={{ color: "#ddd" }}>{info.count}</span>
              </div>

              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#ffb93b" }}>
                  #{info.average_placement.toFixed(2)}
                </div>
                <div style={{ fontSize: "0.6rem", color: "#666" }}>AVG PLACE</div>
              </div>
            </div>
          );

          // ADDED: Conditional Tooltip wrapping
          if (info.low_sample) {
            return <Tooltip key={champId} text="Low sample size">{champCard}</Tooltip>;
          }
          if (!info.valid) {
            return <Tooltip key={champId} text="Invalid/Niche combination" color="#888">{champCard}</Tooltip>;
          }

          return <div key={champId}>{champCard}</div>;
        })}
      </div>
    </div>
  );
}

export default ArtifactPage;