const ChampionAbility = ({ champion }) => {
  if (!champion || !champion.ability_description) return null;

  const getDamageColor = (sentencePart) => {
    const text = sentencePart.toLowerCase();
    if (text.includes("magic damage")) return "var(--magic-damage)";
    if (text.includes("physical damage")) return "var(--physical-damage)";
    if (text.includes("true damage")) return "var(--true-damage)";
    if (text.includes("shield") || text.includes("health")) return "var(--utility-green)";
    return "var(--text-main)";
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

    const renderLine = (line, lineIdx) => {
      return line.split(statRegex).map((part, i, arr) => {
        if (i % 3 === 1) {
          const contextText = arr[i + 2] || "";
          return (
            <span key={`val-${lineIdx}-${i}`} className="ability-stat-value" style={{ color: getDamageColor(contextText) }}>
              {part}
            </span>
          );
        }
        if (i % 3 === 2) {
          const individualStats = part.split(',').map(s => s.trim());
          return (
            <span key={`stats-${lineIdx}-${i}`} className="ability-stat-icons">
              {individualStats.map((stat, idx) => (
                <img
                  key={idx}
                  src={`/assets/stats/${encodeURIComponent(getStatFileName(stat))}.png`}
                  alt={stat}
                  className="description-stat-icon"
                  onError={(e) => (e.target.style.display = "none")}
                />
              ))}
            </span>
          );
        }
        return part;
      });
    };

    const lines = mainBody.split('\n').filter(line => line.trim() !== '');

    return (
      <>
        <div className="main-ability-text">
          {lines.map((line, lineIdx) => (
            <p key={lineIdx} className="ability-line">{renderLine(line, lineIdx)}</p>
          ))}
        </div>
        {keywords.length > 0 && (
          <div className="keywords-container">
            {keywords.map((kw, idx) => (
              <p key={idx} className="keyword-item">
                {kw.replace("</keyword>", "").trim()}
              </p>
            ))}
          </div>
        )}
      </>
    );
  };

  return (
    <div className="ability-container">
      <div className="ability-header">
        <img
          src={`/assets/ability_icons/${champion.champion.toLowerCase()}.png`}
          className="ability-icon"
          alt={champion.ability_name}
          onError={(e) => (e.target.src = "/assets/ability_icons/default.png")}
        />
        <h3 className="ability-title">{champion.ability_name}</h3>
      </div>
      <div className="description-text">
        {formatDescription(champion.ability_description)}
      </div>
    </div>
  );
};

export default ChampionAbility;