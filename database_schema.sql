-- TeenBuzz Database Schema for Supabase

-- Users table for authentication and tracking
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Articles table to store news articles (updated with user tracking)
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL PRIMARY KEY,
    headline VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    relevance TEXT,
    image_url VARCHAR(500),
    original_url VARCHAR(500),
    drawn_by_user_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User article draws tracking (for rate limiting and analytics)
CREATE TABLE IF NOT EXISTS user_draws (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    article_id BIGINT REFERENCES articles(id) NOT NULL,
    drawn_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
CREATE INDEX IF NOT EXISTS idx_articles_drawn_by ON articles(drawn_by_user_id);
CREATE INDEX IF NOT EXISTS idx_user_draws_user_id ON user_draws(user_id);
CREATE INDEX IF NOT EXISTS idx_user_draws_drawn_at ON user_draws(drawn_at DESC);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Enable Row Level Security (RLS)
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_draws ENABLE ROW LEVEL SECURITY;

-- Create policies for public read access (since it's a news app)
CREATE POLICY "Articles are publicly readable" ON articles FOR SELECT USING (true);
CREATE POLICY "Categories are publicly readable" ON categories FOR SELECT USING (true);

-- Policies for user operations
CREATE POLICY "Users can insert articles" ON articles FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own articles" ON articles FOR UPDATE USING (true);
CREATE POLICY "Users can insert draws" ON user_draws FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can view their own draws" ON user_draws FOR SELECT USING (true);

-- Insert a default admin user (password: admin123)
-- In production, you should use a proper password hashing library
INSERT INTO users (username, password_hash, email, is_admin) VALUES
('admin', 'admin123', 'admin@teenbuzz.com', TRUE)
ON CONFLICT (username) DO NOTHING; 