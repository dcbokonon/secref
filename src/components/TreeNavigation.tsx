import React, { useState, useEffect } from 'react';

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

const TreeItem: React.FC<TreeItemProps> = ({ node, level, basePath }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [children, setChildren] = useState<TreeNode[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Check if node has children or can load children
  const hasChildren = !!(node.children?.length || node.file || node.items?.length);
  const indent = level * 20;

  const handleClick = async (e: React.MouseEvent) => {
    e.preventDefault();
    
    if (!hasChildren) {
      // Leaf node - navigate to URL
      if (node.url) {
        window.location.href = node.url;
      }
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
                    items.push({
                      name: subsub.title,
                      count: subsub.items?.length || 0,
                      children: subsub.items?.map((item: any) => ({
                        name: item.name,
                        url: item.url || item.link,
                        count: 0,
                        notation: item.notation,
                        pricingNote: item.pricingNote
                      })) || []
                    });
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
                      pricingNote: item.pricingNote
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
                  pricingNote: item.pricingNote
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
              pricingNote: item.pricingNote
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
            />
          ))}
          {node.children?.map((child, index) => (
            <TreeItem 
              key={index} 
              node={child} 
              level={level + 1}
              basePath={child.category || basePath}
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
            { name: 'Vulnerability Scanners', file: 'vulnerability-assessment', count: data.toolsByPhase.vulnerability.totalItems, category: 'tools' },
            { name: 'Web Application Testing', file: 'web-security', count: data.webSecurityData.totalItems, category: 'tools' },
            { name: 'Network Testing', file: 'network-testing', count: data.networkTestingData.totalItems, category: 'tools' },
            { name: 'Penetration Testing', file: 'exploitation', count: data.toolsByPhase.exploitation.totalItems, category: 'tools' },
            { name: 'OSINT Tools', file: 'osint', count: data.osintData.totalItems, category: 'tools' },
            { name: 'API Security Testing', file: 'api-security', count: 56, category: 'tools' }
          ]
        },
        {
          name: 'Monitoring & Detection',
          children: [
            { name: 'SIEM Platforms', file: 'siem', count: data.siemData.totalItems, category: 'tools' },
            { name: 'Network Monitoring', file: 'network-monitoring', count: data.networkMonitoringData.totalItems, category: 'tools' },
            { name: 'Endpoint Detection', file: 'endpoint-detection', count: data.endpointData.totalItems, category: 'tools' },
            { name: 'Threat Intelligence', file: 'threat-intelligence', count: data.threatIntelData.totalItems, category: 'tools' }
          ]
        },
        {
          name: 'Response & Analysis',
          children: [
            { name: 'Incident Response', file: 'incident-response', count: data.incidentResponseData.totalItems, category: 'tools' },
            { name: 'Digital Forensics', file: 'forensics-ir', count: data.toolsByPhase.forensics.totalItems, category: 'tools' },
            { name: 'Malware Analysis', file: 'malware-analysis', count: data.malwareAnalysisData.totalItems, category: 'tools' },
            { name: 'Log Analysis', file: 'log-analysis', count: data.logAnalysisData.totalItems, category: 'tools' }
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
    <div className="tree-navigation">
      {sections.map((section, index) => (
        <TreeItem 
          key={index} 
          node={section} 
          level={0}
          basePath={section.category || ''}
        />
      ))}
    </div>
  );
};