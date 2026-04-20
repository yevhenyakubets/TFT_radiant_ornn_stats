  export const getRarityColor = (cost) => {
    switch (cost) {
      case 1: return "rgb(24, 36, 49)";
      case 2: return "rgb(20, 77, 29)";
      case 3: return "rgb(28, 52, 93)";
      case 4: return "rgb(102, 20, 79)";
      case 5:
      case 7: return "rgb(134, 84, 11)";
      default: return "#ccc";
    }
  };

  export const stat_map = {
    "AD": "AD", "AP": "AP", "AS": "AS", "Armor": "Armor",
    "Health": "Health", "MagicResist": "MR", "CritChance": "CritChance",
    "BuffDamageAmp": "scaleDA", "ManaRegen": "scalemanaregen",
    "{cd951938}": "scaleDR", "StatOmnivamp": "scaleSV",
    "DamageAmp": "scaleDA", "BonusDamage": "scaleDA"
  };

  export const formatStatValue = (value, key) => {
    if (["BuffDamageAmp", "AD", "StatOmnivamp", "DamageAmp", "{cd951938}", "BonusDamage"].includes(key)) {
      return `+${Math.round(value * 100)}%`;
    }
    if (["AS", "CritChance"].includes(key)) return `+${Math.round(value)}%`;
    return `+${Math.round(value)}`;
  };

export const formatItemDescription = (text) => {
  if (!text) return null;
  const parts = text.split("<keyword>");
  return {
    mainBody: parts[0].split('\n').filter(l => l.trim() && l.trim() !== 'X'),
    keywords: parts.slice(1).map(kw => kw.replace("</keyword>", "").trim())
  };
};

export const getDeltaColor = (delta) => {
  if (delta === null || delta === undefined) return 'var(--text-main)';
  if (delta < 0) return 'var(--utility-green)';
  if (delta > 0) return 'var(--physical-damage)';
  return 'var(--text-main)';
};

export const processDescriptionIcons = (processed) => {
  if (!processed) return "";
  
  processed = processed.replace(/\(\s*[a-zA-Z]*:\s*\)/g, "");
  processed = processed.replace(/\(\s*\)/g, "");

  return processed
    .replace(/([0-9./%]+)(?:<[^>]+>)*\s*\(([^)]+)\)/g, (match, val, stats) => {
      if (!stats || !stats.trim()) return val;

      const icons = stats.split(',').map(s => s.trim()).map(stat => {
        const fileName = {
          'ad': 'AD', 'ap': 'AP', 'armor': 'Armor', 'as': 'AS',
          'crit': 'CritChance', 'health': 'Health', 'hp': 'Health',
          'mr': 'MR', 'amp': 'Amp'
        }[stat.toLowerCase()] || stat;
        
        return `<img src="/assets/stats/${fileName}.png" class="description-stat-icon" alt="${stat}" />`;
      }).join('');

      return `<span class="stat-wrapper"><span class="stat-value">${val}</span>${icons}</span>`;
    })
    .replace(/%i:goldCoins%/g, 
      `<img src="/assets/other/gold.png" class="description-inline-icon" alt="gold" />`
    );
};