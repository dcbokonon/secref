import React, { useState, useEffect } from 'react';

interface TreeNode {
  name: string;
  count?: number;
  url?: string;
  children?: TreeNode[];
  items?: any[];
  file?: string;
  category?: string;
}

interface TreeItemProps {
  node: TreeNode;
  level: number;
  basePath: string;
}

const TreeItem: React.FC<TreeItemProps> = ({ node, level, basePath }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [children, setChildren] = useState<TreeNode[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const hasChildren = node.children || node.file || (node.items && node.items.length > 0);
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
    if (children.length === 0 && node.file) {
      setIsLoading(true);
      try {
        const response = await fetch(`/data/${basePath}/${node.file}.json`);
        console.log('Loading:', `/data/${basePath}/${node.file}.json`);
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
                        count: 0
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
                      count: 0
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
                  count: 0
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
              count: 0
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
        {node.count !== undefined && (
          <span className="tree-count">({node.count})</span>
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
              basePath={basePath}
            />
          ))}
          {node.children?.map((child, index) => (
            <TreeItem 
              key={index} 
              node={child} 
              level={level + 1}
              basePath={basePath}
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
            { name: 'Reconnaissance', file: 'reconnaissance', count: data.toolsByPhase.reconnaissance.totalItems },
            { name: 'Vulnerability Scanners', file: 'vulnerability-assessment', count: data.toolsByPhase.vulnerability.totalItems },
            { name: 'Web Application Testing', file: 'web-security', count: data.webSecurityData.totalItems },
            { name: 'Network Testing', file: 'network-testing', count: data.networkTestingData.totalItems },
            { name: 'Penetration Testing', file: 'exploitation', count: data.toolsByPhase.exploitation.totalItems },
            { name: 'OSINT Tools', file: 'osint', count: data.osintData.totalItems },
            { name: 'API Security Testing', file: 'api-security', count: 56 }
          ]
        },
        {
          name: 'Monitoring & Detection',
          children: [
            { name: 'SIEM Platforms', file: 'siem', count: data.siemData.totalItems },
            { name: 'Network Monitoring', file: 'network-monitoring', count: data.networkMonitoringData.totalItems },
            { name: 'Endpoint Detection', file: 'endpoint-detection', count: data.endpointData.totalItems },
            { name: 'Threat Intelligence', file: 'threat-intelligence', count: data.threatIntelData.totalItems }
          ]
        },
        {
          name: 'Response & Analysis',
          children: [
            { name: 'Incident Response', file: 'incident-response', count: data.incidentResponseData.totalItems },
            { name: 'Digital Forensics', file: 'forensics-ir', count: data.toolsByPhase.forensics.totalItems },
            { name: 'Malware Analysis', file: 'malware-analysis', count: data.malwareAnalysisData.totalItems },
            { name: 'Log Analysis', file: 'log-analysis', count: data.logAnalysisData.totalItems }
          ]
        },
        {
          name: 'Specialized Domains',
          children: data.specializedData.map((item: any) => ({
            name: item.title,
            file: item.file,
            count: item.totalItems
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