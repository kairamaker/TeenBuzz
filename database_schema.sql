-- TeenBuzz Database Schema for Supabase

-- Articles table to store news articles
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    headline VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    relevance TEXT,
    image_url VARCHAR(500),
    original_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Categories table (optional, for future expansion)
CREATE TABLE IF NOT EXISTS categories (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default categories
INSERT INTO categories (name, description) VALUES
('Technology', 'Tech news, gadgets, apps, and digital trends'),
('Entertainment', 'Movies, TV shows, music, and celebrity news'),
('Sports', 'Sports news, games, and athlete updates'),
('Health', 'Health tips, wellness, and medical news'),
('Environment', 'Climate change, sustainability, and environmental issues'),
('Education', 'School news, study tips, and educational developments'),
('Social Issues', 'Social justice, equality, and community issues'),
('Science', 'Scientific discoveries and research'),
('Gaming', 'Video games, esports, and gaming culture'),
('Music', 'Music news, artist updates, and new releases')
ON CONFLICT (name) DO NOTHING;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);

-- Enable Row Level Security (RLS) - optional for future user features
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (since it's a news app)
CREATE POLICY "Articles are publicly readable" ON articles FOR SELECT USING (true);
CREATE POLICY "Categories are publicly readable" ON categories FOR SELECT USING (true);

-- For admin operations, you might want to add policies for INSERT/UPDATE/DELETE
-- These would typically be restricted to authenticated admin users 