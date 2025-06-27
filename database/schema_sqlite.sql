-- SecRef Database Schema for SQLite
-- Supports all current fields plus future expansion

-- Drop existing tables if they exist (for clean install)
DROP TABLE IF EXISTS resource_platforms;
DROP TABLE IF EXISTS resource_tags;
DROP TABLE IF EXISTS resource_links;
DROP TABLE IF EXISTS resource_categories;
DROP TABLE IF EXISTS resources;
DROP TABLE IF EXISTS categories;

-- Categories table (hierarchical)
CREATE TABLE categories (
    id TEXT PRIMARY KEY,
    parent_id TEXT REFERENCES categories(id) ON DELETE CASCADE,
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    metadata TEXT DEFAULT '{}', -- JSON stored as text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(parent_id, slug)
);

-- Create index for hierarchical queries
CREATE INDEX idx_categories_parent ON categories(parent_id);

-- Main resources table
CREATE TABLE resources (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    url TEXT,
    
    -- Type fields
    type TEXT CHECK (type IN ('free', 'paid', 'freemium')),
    resource_type TEXT CHECK (resource_type IN ('tool', 'technique', 'service', 'platform')),
    
    -- Difficulty and status
    difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced', 'expert')),
    status TEXT,
    
    -- Notation and pricing
    notation TEXT,
    pricing_note TEXT,
    
    -- Community indicators
    is_community_favorite INTEGER DEFAULT 0, -- Boolean as integer
    is_industry_standard INTEGER DEFAULT 0,  -- Boolean as integer
    popularity_note TEXT,
    
    -- Location and schedule (for events/communities)
    location TEXT,
    locations TEXT, -- JSON array as text
    schedule TEXT,
    
    -- Additional fields
    cost TEXT,
    duration TEXT,
    features TEXT, -- JSON array as text
    domains TEXT,  -- JSON array as text
    
    -- Flexible storage for unknown fields
    extra_data TEXT DEFAULT '{}', -- JSON as text
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_resources_type ON resources(type);
CREATE INDEX idx_resources_resource_type ON resources(resource_type);
CREATE INDEX idx_resources_difficulty ON resources(difficulty);
CREATE INDEX idx_resources_slug ON resources(slug);

-- Many-to-many relationship for categories
CREATE TABLE resource_categories (
    resource_id TEXT REFERENCES resources(id) ON DELETE CASCADE,
    category_id TEXT REFERENCES categories(id) ON DELETE CASCADE,
    is_primary INTEGER DEFAULT 0, -- Boolean as integer
    sort_order INTEGER DEFAULT 0,
    PRIMARY KEY (resource_id, category_id)
);

-- Links table (one-to-many)
CREATE TABLE resource_links (
    id TEXT PRIMARY KEY,
    resource_id TEXT REFERENCES resources(id) ON DELETE CASCADE,
    url TEXT NOT NULL,
    label TEXT NOT NULL,
    type TEXT CHECK (type IN ('docs', 'tutorial', 'cheatsheet', 'tool', 'other')),
    sort_order INTEGER DEFAULT 0
);

CREATE INDEX idx_resource_links_resource ON resource_links(resource_id);

-- Tags table (normalized many-to-many)
CREATE TABLE resource_tags (
    resource_id TEXT REFERENCES resources(id) ON DELETE CASCADE,
    tag TEXT NOT NULL,
    PRIMARY KEY (resource_id, tag)
);

CREATE INDEX idx_resource_tags_resource ON resource_tags(resource_id);
CREATE INDEX idx_resource_tags_tag ON resource_tags(tag);

-- Platforms table (normalized many-to-many)
CREATE TABLE resource_platforms (
    resource_id TEXT REFERENCES resources(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    PRIMARY KEY (resource_id, platform)
);

CREATE INDEX idx_resource_platforms_resource ON resource_platforms(resource_id);
CREATE INDEX idx_resource_platforms_platform ON resource_platforms(platform);

-- Audit log for tracking changes
CREATE TABLE audit_log (
    id TEXT PRIMARY KEY,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
    old_data TEXT, -- JSON as text
    new_data TEXT, -- JSON as text
    changed_by TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_record ON audit_log(table_name, record_id);
CREATE INDEX idx_audit_log_changed_at ON audit_log(changed_at);

-- View for easy querying with all related data
CREATE VIEW resources_full AS
SELECT 
    r.*,
    GROUP_CONCAT(DISTINCT t.tag) AS tags,
    GROUP_CONCAT(DISTINCT p.platform) AS platforms
FROM resources r
LEFT JOIN resource_tags t ON r.id = t.resource_id
LEFT JOIN resource_platforms p ON r.id = p.resource_id
GROUP BY r.id;