import React, { useState, useEffect } from 'react';
import { ToolDetails } from './ToolDetails';

interface TreeNode {
  name: string;
  count?: number;
  url?: string;
  children?: TreeNode[];
  items?: any[];
  file?: string;
  category?: string;
  notation?: string;
  pricingNote?: string;
  description?: string;
  type?: string;
  platforms?: string[];
  tags?: string[];
  difficulty?: string;
}

interface TreeItemProps {
  node: TreeNode;
  level: number;
  basePath: string;
}

// Helper function to get tooltip text for notations
const getTooltipText = (notation: string): string => {
  const tooltips: { [key: string]: string } = {
    '(F)': 'Freemium - Basic features free, advanced features require payment',
    '(F)†': 'Freemium with registration - Must create account for free tier',
    '($)': 'Paid only - No free version available',
    '(E)': 'Enterprise pricing - Contact sales for custom quote',
    '†': 'Registration required',
    '[BETA]': 'Beta version - May have bugs or incomplete features',
    '[EOL]': 'End of Life - No longer maintained'
  };
  return tooltips[notation] || notation;
};

// Helper function to get notation class
const getNotationClass = (notation: string): string => {
  if (notation.includes('(F)')) return 'notation-free';
  if (notation.includes('($)')) return 'notation-paid';
  if (notation.includes('(E)')) return 'notation-enterprise';
  if (notation === '†') return 'notation-registration';
  return '';
};

interface ExtendedTreeItemProps extends TreeItemProps {
  onToolClick: (tool: any) => void;
}

const TreeItem: React.FC<ExtendedTreeItemProps> = ({ node, level, basePath, onToolClick }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [children, setChildren] = useState<TreeNode[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Check if node has children or can load children
  const hasChildren = !!(node.children?.length || node.file || node.items?.length);
  const indent = level * 20;

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    if (!hasChildren) {
      // Leaf node - show details instead of navigating
      onToolClick(node);
      return;
    }

    // Toggle expansion
    if (isExpanded) {
      setIsExpanded(false);
      return;
    }

    // Load children if needed
    if (children.length === 0 && node.file && basePath) {
      setIsLoading(true);
      try {
        const url = `/data/${basePath}/${node.file}.json`;
        console.log('Loading:', url);
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`Failed to load ${url}: ${response.status}`);
        }
        const data = await response.json();
        
        // Extract items from the JSON structure
        const items: TreeNode[] = [];
        
        // Handle different JSON structures
        if (data.categories && Array.isArray(data.categories)) {
          // Has categories array with subcategories
          data.categories.forEach((category: any) => {
            if (category.subcategories && category.subcategories.length > 0) {
              // Has subcategories - add them as expandable nodes
              category.subcategories.forEach((sub: any) => {
                if (sub.subcategories && sub.subcategories.length > 0) {
                  // Nested subcategories
                  sub.subcategories.forEach((subsub: any) => {
                    // Check if this subcategory has even more subcategories
                    if (subsub.subcategories && subsub.subcategories.length > 0) {
                      // Even deeper nesting - handle it
                      items.push({
                        name: subsub.title,
                        count: subsub.subcategories.reduce((sum: number, s: any) => sum + (s.items?.length || 0), 0),
                        children: subsub.subcategories.map((subsubsub: any) => ({
                          name: subsubsub.title,
                          count: subsubsub.items?.length || 0,
                          children: subsubsub.items?.map((item: any) => ({
                            name: item.name,
                            url: item.url || item.link,
                            count: 0,
                            notation: item.notation,
                            pricingNote: item.pricingNote,
                            description: item.description,
                            type: item.type,
                            platforms: item.platforms,
                            tags: item.tags,
                            difficulty: item.difficulty
                          })) || []
                        }))
                      });
                    } else {
                      // Regular handling for subcategories with items
                      items.push({
                        name: subsub.title,
                        count: subsub.items?.length || 0,
                        children: subsub.items?.map((item: any) => ({
                          name: item.name,
                          url: item.url || item.link,
                          count: 0,
                          notation: item.notation,
                          pricingNote: item.pricingNote,
                          description: item.description,
                          type: item.type,
                          platforms: item.platforms,
                          tags: item.tags,
                          difficulty: item.difficulty
                        })) || []
                      });
                    }
                  });
                } else if (sub.items && sub.items.length > 0) {
                  // Direct items under subcategory
                  items.push({
                    name: sub.title,
                    count: sub.items.length,
                    children: sub.items.map((item: any) => ({
                      name: item.name,
                      url: item.url || item.link,
                      count: 0,
                      notation: item.notation,
                      pricingNote: item.pricingNote,
                      description: item.description,
                      type: item.type,
                      platforms: item.platforms,
                      tags: item.tags,
                      difficulty: item.difficulty
                    }))
                  });
                }
              });
            } else if (category.items) {
              // Direct items under category
              items.push({
                name: category.title,
                count: category.items.length,
                children: category.items.map((item: any) => ({
                  name: item.name,
                  url: item.url || item.link,
                  count: 0,
                  notation: item.notation,
                  pricingNote: item.pricingNote,
                  description: item.description,
                  type: item.type,
                  platforms: item.platforms,
                  tags: item.tags,
                  difficulty: item.difficulty
                }))
              });
            }
          });
        } else if (data.items) {
          // Direct items
          data.items.forEach((item: any) => {
            items.push({
              name: item.name,
              url: item.url || item.link,
              count: 0,
              notation: item.notation,
              pricingNote: item.pricingNote,
              description: item.description,
              type: item.type,
              platforms: item.platforms,
              tags: item.tags,
              difficulty: item.difficulty
            });
          });
        }
        
        setChildren(items);
      } catch (error) {
        console.error('Failed to load data:', error);
      }
      setIsLoading(false);
    }
    
    setIsExpanded(true);
  };

  return (
    <div className="tree-item">
      <div 
        className={`tree-node ${hasChildren ? 'expandable' : 'leaf'}`}
        style={{ paddingLeft: `${indent}px` }}
        onClick={handleClick}
      >
        <span className="tree-icon">
          {hasChildren ? (isExpanded ? '▼' : '▶') : '→'}
        </span>
        <span className="tree-name">{node.name}</span>
        {node.notation && (
          <span 
            className={`notation ${getNotationClass(node.notation)}`}
            data-tooltip={`${getTooltipText(node.notation)}${node.pricingNote ? ` - ${node.pricingNote}` : ''}`}
            aria-label={getTooltipText(node.notation)}
          >
            {node.notation}
          </span>
        )}
        {node.count !== undefined && node.count > 0 && (
          <span className="tree-count">({node.count} resources)</span>
        )}
        {isLoading && <span className="loading">...</span>}
      </div>
      
      {isExpanded && (
        <div className="tree-children">
          {children.map((child, index) => (
            <TreeItem 
              key={index} 
              node={child} 
              level={level + 1}
              basePath={child.category || basePath}
              onToolClick={onToolClick}
            />
          ))}
          {node.children?.map((child, index) => (
            <TreeItem 
              key={index} 
              node={child} 
              level={level + 1}
              basePath={child.category || basePath}
              onToolClick={onToolClick}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface TreeNavigationProps {
  data: any;
}

export const TreeNavigation: React.FC<TreeNavigationProps> = ({ data }) => {
  const [selectedTool, setSelectedTool] = useState<any>(null);

  const handleToolClick = (tool: any) => {
    setSelectedTool(tool);
  };
  const sections = [
    {
      name: 'SECURITY TOOLS',
      count: data.totalTools,
      category: 'tools',
      children: [
        {
          name: 'Assessment & Testing',
          children: [
            { name: 'Reconnaissance', file: 'reconnaissance', count: data.toolsByPhase.reconnaissance.totalItems, category: 'tools' },
            { name: 'Vulnerability Assessment', file: 'vulnerability-assessment', count: data.toolsByPhase.vulnerability.totalItems, category: 'tools' },
            { name: 'Exploitation', file: 'exploitation', count: data.toolsByPhase.exploitation.totalItems, category: 'tools' }
          ]
        },
        {
          name: 'Monitoring & Detection',
          children: [
            { name: 'Defense & Monitoring', file: 'defense-monitoring', count: data.toolsByPhase.defense.totalItems, category: 'tools' }
          ]
        },
        {
          name: 'Response & Analysis',
          children: [
            { name: 'Forensics & Incident Response', file: 'forensics-ir', count: data.toolsByPhase.forensics.totalItems, category: 'tools' }
          ]
        },
        {
          name: 'Security Tools',
          children: [
            { name: 'Cryptography & Privacy', file: 'cryptography', count: data.toolsByPhase.crypto.totalItems, category: 'tools' },
            { name: 'Development Security', file: 'development-security', count: data.toolsByPhase.development.totalItems, category: 'tools' },
            { name: 'Hardware & Physical', file: 'hardware-physical', count: data.toolsByPhase.hardware.totalItems, category: 'tools' },
            { name: 'Mobile Security', file: 'mobile-security', count: data.toolsByPhase.mobile.totalItems, category: 'tools' },
            { name: 'Cloud Security', file: 'cloud-security', count: data.toolsByPhase.cloud.totalItems, category: 'tools' }
          ]
        },
        {
          name: 'Specialized Domains',
          children: data.specializedData.map((item: any) => ({
            name: item.title,
            file: item.file,
            count: item.totalItems,
            category: 'specialized-domains'
          }))
        }
      ]
    },
    {
      name: 'LEARNING RESOURCES',
      count: data.totalLearning,
      category: 'learning',
      children: data.learningData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'PRACTICE & CHALLENGES',
      count: data.totalPractice,
      category: 'practice',
      children: data.practiceData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'COMMUNITY',
      count: data.totalCommunity,
      category: 'communities',
      children: data.communityData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'CAREER RESOURCES',
      count: data.totalCareer,
      category: 'career',
      children: data.careerData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'REFERENCES & DOCUMENTATION',
      count: data.totalReferences,
      category: 'references',
      children: data.referencesData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'NEWS & INFORMATION',
      count: data.totalNews,
      category: 'news',
      children: data.newsData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'COMPLIANCE & STANDARDS',
      count: data.totalCompliance,
      category: 'compliance',
      children: data.complianceData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'VULNERABILITY INTELLIGENCE',
      count: data.totalVulnIntel,
      category: 'vulnerability-intelligence',
      children: data.vulnIntelData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    },
    {
      name: 'SECURITY DISTRIBUTIONS',
      count: data.totalDistros,
      category: 'distributions',
      children: data.distrosData.map((item: any) => ({
        name: item.title,
        file: item.file,
        count: item.totalItems
      }))
    }
  ];

  return (
    <>
      <div className={`tree-navigation ${selectedTool ? 'has-details' : ''}`}>
        {sections.map((section, index) => (
          <TreeItem 
            key={index} 
            node={section} 
            level={0}
            basePath={section.category || ''}
            onToolClick={handleToolClick}
          />
        ))}
      </div>
      {selectedTool && (
        <ToolDetails 
          tool={selectedTool} 
          onClose={() => setSelectedTool(null)} 
        />
      )}
    </>
  );
};