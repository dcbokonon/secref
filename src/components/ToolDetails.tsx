import React from 'react';

interface ToolDetailsProps {
  tool: {
    name: string;
    url?: string;
    links?: Array<{
      url: string;
      label: string;
      type: 'docs' | 'tutorial' | 'cheatsheet' | 'tool' | 'other';
    }>;
    description?: string;
    type?: string;
    resourceType?: 'tool' | 'technique' | 'service' | 'platform';
    notation?: string;
    pricingNote?: string;
    platforms?: string[];
    tags?: string[];
    difficulty?: string;
    isCommunityFavorite?: boolean;
    isIndustryStandard?: boolean;
    popularityNote?: string;
  } | null;
  onClose: () => void;
}

export const ToolDetails: React.FC<ToolDetailsProps> = ({ tool, onClose }) => {
  if (!tool) return null;

  return (
    <div className="tool-details">
      <div className="tool-details-header">
        <h3>
          {tool.name}
          {tool.isCommunityFavorite && <span className="badge-favorite" title="Community Favorite">⭐</span>}
          {tool.isIndustryStandard && <span className="badge-standard" title="Industry Standard">🏆</span>}
        </h3>
        <button className="close-button" onClick={onClose} aria-label="Close">×</button>
      </div>
      
      <div className="tool-details-content">
        {tool.description && (
          <div className="detail-section">
            <h4>Description</h4>
            <p>{tool.description}</p>
          </div>
        )}
        
        {tool.popularityNote && (
          <div className="detail-section popularity-section">
            <p className="popularity-note">{tool.popularityNote}</p>
          </div>
        )}
        
        {tool.type && tool.resourceType !== 'technique' && (
          <div className="detail-section">
            <h4>License</h4>
            <p className={`license-type ${tool.type}`}>
              {tool.type === 'free' ? 'Free & Open Source' : 
               tool.type === 'freemium' ? 'Freemium' : 
               tool.type === 'paid' ? 'Commercial' : tool.type}
              {tool.notation && <span className={`notation ${getNotationClass(tool.notation)}`}> {tool.notation}</span>}
            </p>
            {tool.pricingNote && <p className="pricing-note">{tool.pricingNote}</p>}
          </div>
        )}
        
        {tool.resourceType && (
          <div className="detail-section">
            <h4>Resource Type</h4>
            <p className={`resource-type resource-type-${tool.resourceType}`}>
              {tool.resourceType.charAt(0).toUpperCase() + tool.resourceType.slice(1)}
            </p>
          </div>
        )}
        
        {tool.platforms && tool.platforms.length > 0 && (
          <div className="detail-section">
            <h4>Platforms</h4>
            <div className="platforms">
              {tool.platforms.map((platform, idx) => (
                <span key={idx} className={`platform platform-${platform}`}>
                  {platform}
                </span>
              ))}
            </div>
          </div>
        )}
        
        {tool.difficulty && (
          <div className="detail-section">
            <h4>Difficulty</h4>
            <span className={`difficulty difficulty-${tool.difficulty}`}>
              {tool.difficulty.charAt(0).toUpperCase() + tool.difficulty.slice(1)}
            </span>
          </div>
        )}
        
        {tool.tags && tool.tags.length > 0 && (
          <div className="detail-section">
            <h4>Tags</h4>
            <div className="tags">
              {tool.tags.map((tag, idx) => (
                <span key={idx} className="tag">#{tag}</span>
              ))}
            </div>
          </div>
        )}
        
        {(tool.links && tool.links.length > 0) ? (
          <div className="detail-section">
            <h4>Resources</h4>
            <div className="links-list">
              {tool.links.map((link, idx) => (
                <a 
                  key={idx}
                  href={link.url} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className={`external-link link-type-${link.type}`}
                >
                  {link.label} →
                </a>
              ))}
            </div>
          </div>
        ) : tool.url && (
          <div className="detail-section">
            <a 
              href={tool.url} 
              target="_blank" 
              rel="noopener noreferrer" 
              className="external-link"
            >
              Visit Website →
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

// Helper function to get notation class
const getNotationClass = (notation: string): string => {
  if (notation.includes('(F)')) return 'notation-free';
  if (notation.includes('($)')) return 'notation-paid';
  if (notation.includes('(E)')) return 'notation-enterprise';
  if (notation === '†') return 'notation-registration';
  return '';
};