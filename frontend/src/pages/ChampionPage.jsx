import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import Tooltip from "../components/Tooltip"; 
import React from 'react';

const ChampionAbility = ({ champion }) => {
  if (!champion || !champion.ability_description) return null;

  const getDamageColor = (sentencePart) => {
    const text = sentencePart.toLowerCase();
    if (text.includes("magic damage")) return "#4e98ff"; 
    if (text.includes("physical damage")) return "#ff4e4e"; 
    if (text.includes("true damage")) return "#ffffff"; 
    if (text.includes("shield") || text.includes("health")) return "#6bff82"; 
    return "#f0e6d2"; 
  };

  const getStatFileName = (stat) => {
    const s = stat.toLowerCase().trim();
    const mapping = {
      'ad': 'AD', 'ap': 'AP', 'armor': 'Armor', 'as': 'AS',
      'crit': 'CritChance', 'health': 'Health', 'hp': 'Health',
      'mr': 'MR', 'dr': 'scaleDR', 'manaregen': 'scalemanaregen', 'sv': 'scaleSV'
    };
    return mapping[s] || stat;
  };

  const formatDescription = (text) => {
    const parts = text.split("<keyword>");
    const mainBody = parts[0];
    const keywords = parts.slice(1);
    const statRegex = /([\d./%]+)\s*\(([^)]+)\)/g;

    const renderedBody = mainBody.split(statRegex).map((part, i, arr) => {
      if (i % 3 === 1) {
        const contextText = arr[i + 2] || ""; 
        return (
          <span key={`val-${i}`} style={{ color: getDamageColor(contextText), fontWeight: "bold" }}>
            {part}
          </span>
        );
      }
      if (i % 3 === 2) {
        const individualStats = part.split(',').map(s => s.trim());
        return (
          <span key={`stats-${i}`} style={{ whiteSpace: "nowrap", marginLeft: "4px" }}>
            {individualStats.map((stat, idx) => (
              <img
                key={idx}
                src={`/assets/stats/${getStatFileName(stat)}.png`}
                alt={stat}
                title={stat}
                style={{ width: "18px", height: "18px", margin: "0 2px", verticalAlign: "middle" }}
                onError={(e) => (e.target.style.display = "none")}
              />
            ))}
          </span>
        );
      }
      return part;
    });

    return (
      <>
        <div className="main-ability-text" style={{ lineHeight: "1.6", fontSize: "1rem" }}>
          {renderedBody}
        </div>
        {keywords.length > 0 && (
          <div className="keywords-container" style={{ marginTop: "12px", borderTop: "1px solid #2d2d31", paddingTop: "8px" }}>
            {keywords.map((kw, idx) => (
              <p key={idx} style={{ margin: "4px 0", fontSize: "0.85rem", color: "#a0a0a8", fontStyle: "italic", display: "block" }}>
                • {kw.replace("</keyword>", "").trim()}
              </p>
            ))}
          </div>
        )}
      </>
    );
  };

  return (
    <div className="ability-container" style={{ marginTop: "15px" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "8px" }}>
        <img 
          src={`/assets/ability_icons/${champion.champion.toLowerCase()}.png`} 
          alt={champion.ability_name}
          style={{ width: "32px", height: "32px", borderRadius: "4px", border: "1px solid #444" }}
          onError={(e) => (e.target.src = "/assets/ability_icons/default.png")}
        />
        <h3 style={{ margin: 0, color: "#f0e6d2", fontSize: "1.2rem" }}>{champion.ability_name}</h3>
      </div>
      <div className="description-text" style={{ color: "#ccc" }}>
        {formatDescription(champion.ability_description)}
      </div>
    </div>
  );
};

function ChampionPage() {
  const { championId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("artifact");
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
      default: return "#ccc";
    }
  };

  useEffect(() => {
    fetch(`http://127.0.0.1:8000/champions/${championId}`)
      .then(res => res.json())
      .then(json => {
        setData(json);
        setLoading(false);
      });
  }, [championId]);

  if (loading) return <div style={{ color: "white", padding: "20px" }}>Loading...</div>;
  if (data.error) return <div style={{ color: "red", padding: "20px" }}>{data.error}</div>;

  const rarityColor = getRarityColor(data.cost);
  const rawItems = activeTab === "artifact" ? data.artifacts : data.radiants;
  const itemFolderPath = activeTab === "artifact" ? "/assets/artifacts" : "/assets/radiant_items";

  const itemsToShow = Object.entries(rawItems).filter(([, info]) => {
    const matchesValid = info.valid || showInvalid;
    const matchesSample = !info.low_sample || showLowSample;
    return matchesValid && matchesSample;
  });

  return (
    <div style={{ padding: "30px", backgroundColor: "#0a0a0c", minHeight: "100vh", color: "white", fontFamily: "sans-serif" }}>
      
      {/* --- Champion Header UPDATED --- */}
      <div style={{ 
        display: "flex", alignItems: "flex-start", gap: "32px", marginBottom: "40px", padding: "20px",
        borderRadius: "12px", background: `linear-gradient(90deg, #1c1c1f 0%, transparent 100%)`,
        borderLeft: `6px solid ${rarityColor}`
      }}>
        {/* Splash Image Container with Trait Overlay */}
        <div style={{ position: "relative", minWidth: "220px" }}>
          <img 
            src={`/assets/champ_splashes/${championId}.png`} 
            alt={data.name} 
            style={{ 
              width: "400px", 
              height: "auto", 
              borderRadius: "8px", 
              border: `3px solid ${rarityColor}`, 
              boxShadow: `0 0 20px ${rarityColor}33` 
            }}
          />
          {/* Traits Overlay */}
          <div style={{ 
            position: "absolute", 
            top: "8px", 
            left: "8px", 
            display: "flex", 
            flexDirection: "column", 
            gap: "6px" 
          }}>
            {data.traits && data.traits.map((trait, index) => (
              <Tooltip key={index} text={trait.name}>
                <div style={{ 
                  backgroundColor: "rgba(0,0,0,0.7)", 
                  padding: "4px", 
                  borderRadius: "4px", 
                  display: "flex", 
                  alignItems: "center", 
                  justifyContent: "center",
                  border: "1px solid rgba(255,255,255,0.2)"
                }}>
                  <img 
                    src={`/assets/traits/${trait.name}.png`} 
                    alt={trait.name} 
                    style={{ width: "24px", height: "24px" }} 
                    onError={(e) => (e.target.style.display = "none")}
                  />
                  {trait.name}
                </div>
              </Tooltip>
            ))}
          </div>
        </div>

        <div style={{ flex: 1 }}>
          <h1 style={{ margin: 0, fontSize: "3.2rem", letterSpacing: "-1px", lineHeight: "1" }}>{data.name}</h1>
          <div style={{ color: rarityColor, fontWeight: "bold", fontSize: "1.4rem", marginTop: "8px", textTransform: "uppercase", letterSpacing: "1px" }}>
            {data.cost} Cost 
          </div>
          <ChampionAbility champion={data}/>
        </div>
      </div>

      {/* --- Tab Switcher & Toggles --- */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div style={{ display: "flex", gap: "2px", backgroundColor: "#1c1c1f", padding: "4px", borderRadius: "8px" }}>
          {["artifact", "radiant"].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              style={{
                padding: "12px 30px", cursor: "pointer",
                backgroundColor: activeTab === tab ? rarityColor : "transparent",
                color: activeTab === tab ? "black" : "white",
                border: "none", borderRadius: "6px", fontWeight: "bold",
                textTransform: "uppercase", fontSize: "0.85rem", transition: "all 0.2s ease"
              }}
            >
              {tab}s
            </button>
          ))}
        </div>

        <div style={{ display: "flex", gap: "20px" }}>
          <label style={{ color: "#888", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
            Show low sample size
            <input type="checkbox" checked={showLowSample} onChange={() => setShowLowSample(!showLowSample)} />
          </label>
          <label style={{ color: "#888", fontSize: "0.85rem", display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
            Show niche items
            <input type="checkbox" checked={showInvalid} onChange={() => setShowInvalid(!showInvalid)} />
          </label>
        </div>
      </div>

      {/* --- Items Grid --- */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "16px" }}>
        {itemsToShow.map(([itemId, info]) => {
          const card = (
            <div 
              style={{
                backgroundColor: "#16161a", padding: "16px", borderRadius: "10px",
                display: "flex", alignItems: "center", gap: "16px",
                border: info.low_sample ? "1px dashed #ff4e4e" : "1px solid #2d2d31",
                opacity: info.valid ? 1 : 0.5,
                transition: "transform 0.2s ease", cursor: "default"
              }}
              onMouseEnter={(e) => e.currentTarget.style.borderColor = info.low_sample ? "#ff4e4e" : rarityColor}
              onMouseLeave={(e) => e.currentTarget.style.borderColor = info.low_sample ? "#ff4e4e" : "#2d2d31"}
            >
              <img 
                src={`${itemFolderPath}/${itemId}.png`} 
                alt={info.name}
                style={{ width: "56px", height: "56px", borderRadius: "6px", border: "1px solid #323232" }}
                onError={(e) => { e.target.src = "/assets/artifacts/tft_item_unknown.png" }}
              />
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: "bold", fontSize: "1.05rem", color: "#f0e6d2" }}>{info.name}</div>
                <div style={{ fontSize: "0.85rem", color: "#888", marginTop: "2px" }}>
                  Frequency: <span style={{ color: "#ddd" }}>{info.count}</span>
                </div>
              </div>
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: "1.3rem", fontWeight: "bold", color: "#ffb93b" }}>
                  {info.average_placement.toFixed(2)}
                </div>
                <div style={{ fontSize: "0.65rem", color: "#666", textTransform: "uppercase" }}>Avg Place</div>
              </div>
            </div>
          );

          if (info.low_sample) return <Tooltip key={itemId} text="Low sample size">{card}</Tooltip>;
          if (!info.valid) return <Tooltip key={itemId} text="Experimental/Invalid" color="#888">{card}</Tooltip>;
          return <div key={itemId}>{card}</div>;
        })}
      </div>
    </div>
  );
}

export default ChampionPage;