import React from 'react';
import { processDescriptionIcons } from "../utils/helper";

const ChampionAbility = ({ champion }) => {
  if (!champion || !champion.ability_description) return null;

  const formatDescription = (text) => {
    const [mainBody, ...keywords] = text.split("<keyword>");
    const iconProcessedBody = processDescriptionIcons(mainBody);

    return (
      <>
        <div 
          className="main-ability-text" 
          dangerouslySetInnerHTML={{ 
            __html: iconProcessedBody.replace(/\n/g, '<br/>') 
          }} 
        />
        
        {keywords.length > 0 && (
          <div className="keywords-container">
            {keywords.map((kw, idx) => (
              <p 
                key={idx} 
                className="keyword-item"
                dangerouslySetInnerHTML={{ 
                  __html: processDescriptionIcons(kw.replace("</keyword>", "").trim()) 
                }}
              />
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