-- TeenBuzz Database Setup SQL
-- Run this in your Supabase Dashboard → SQL Editor

-- 1. Create Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Create Articles Table
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    headline TEXT NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    source VARCHAR(255),
    url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    drawn_by_user_id UUID REFERENCES users(id),
    publish_date DATE,
    tags TEXT[],
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0
);

-- 3. Create User Draws Table
CREATE TABLE IF NOT EXISTS user_draws (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) NOT NULL,
    article_id INTEGER REFERENCES articles(id) NOT NULL,
    drawn_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, article_id)
);

-- 4. Create Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Create Password Reset Tokens Table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. Create User Preferences Table
CREATE TABLE IF NOT EXISTS user_preferences (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) UNIQUE NOT NULL,
    topics TEXT[],
    categories TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Create Indexes for Performance
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_created_at ON articles(created_at);
CREATE INDEX IF NOT EXISTS idx_articles_drawn_by ON articles(drawn_by_user_id);
CREATE INDEX IF NOT EXISTS idx_user_draws_user_id ON user_draws(user_id);
CREATE INDEX IF NOT EXISTS idx_user_draws_article_id ON user_draws(article_id);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

-- 8. Insert Sample Categories
INSERT INTO categories (name, description, icon) VALUES
('Technology', 'Latest tech news and innovations', 'fas fa-laptop-code'),
('Environment', 'Climate and environmental news', 'fas fa-leaf'),
('Health', 'Health and wellness topics', 'fas fa-heartbeat'),
('Social Issues', 'Social justice and community topics', 'fas fa-users'),
('Science', 'Scientific discoveries and research', 'fas fa-flask')
ON CONFLICT (name) DO NOTHING;

-- 9. Insert Sample Articles
INSERT INTO articles (headline, content, category, source, tags, views, likes) VALUES
('New AI Tools Help Students Study Smarter, Not Harder', 'Students are discovering how artificial intelligence can revolutionize their study habits. From personalized learning plans to instant homework help, AI is making education more accessible and effective for teens everywhere. These tools are changing how students approach learning, making complex subjects more digestible and study sessions more efficient.', 'Technology', 'TechCrunch', ARRAY['AI', 'education', 'technology', 'students', 'learning'], 1250, 89),

('Climate Change: What Teens Can Do to Make a Real Difference', 'Young activists are leading the charge against climate change with innovative solutions and powerful voices. Learn about the practical steps you can take to protect our planet and inspire others to join the movement. From school strikes to social media campaigns, teens are proving that age is just a number when it comes to environmental action.', 'Environment', 'BBC News', ARRAY['climate', 'environment', 'activism', 'sustainability', 'youth'], 980, 76),

('Mental Health Apps That Actually Help Teens Cope', 'New mental health resources designed specifically for teenagers are making it easier to find support and build resilience. These apps offer everything from meditation guides to crisis support, helping teens navigate the challenges of modern life with better mental health tools and resources.', 'Health', 'NPR', ARRAY['mental health', 'apps', 'wellness', 'teenagers', 'support'], 850, 64),

('The Future of Social Media: What Teens Need to Know', 'Social media platforms are evolving rapidly, and teens are at the forefront of these changes. From new privacy features to emerging platforms, understanding these shifts can help you navigate the digital world more safely and effectively.', 'Technology', 'Wired', ARRAY['social media', 'privacy', 'technology', 'digital', 'platforms'], 720, 58),

('How Gen Z is Redefining Success in the Workplace', 'Young people are changing what it means to have a successful career, prioritizing work-life balance, mental health, and meaningful work over traditional corporate ladders. This shift is reshaping entire industries and creating new opportunities.', 'Social Issues', 'Forbes', ARRAY['career', 'workplace', 'gen z', 'success', 'work-life balance'], 680, 52),

('The Science Behind Why Music Moves Us', 'New research reveals how music affects our brains and emotions, especially during teenage years. Understanding these connections can help you use music more effectively for studying, relaxation, and emotional regulation.', 'Science', 'Scientific American', ARRAY['music', 'science', 'brain', 'emotions', 'research'], 590, 45);

-- 10. Create Admin User
INSERT INTO users (username, email, password_hash, is_admin) VALUES
('admin', 'admin@teenbuzz.com', 'admin123', true)
ON CONFLICT (email) DO NOTHING;

-- 11. Enable Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_draws ENABLE ROW LEVEL SECURITY;
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- 12. Create RLS Policies
-- Allow public read access to articles and categories
CREATE POLICY "Allow public read access to articles" ON articles FOR SELECT USING (true);
CREATE POLICY "Allow public read access to categories" ON categories FOR SELECT USING (true);

-- Allow users to read their own data
CREATE POLICY "Users can read own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

-- Allow users to read their own draws
CREATE POLICY "Users can read own draws" ON user_draws FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own draws" ON user_draws FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Allow users to read their own preferences
CREATE POLICY "Users can read own preferences" ON user_preferences FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own preferences" ON user_preferences FOR ALL USING (auth.uid() = user_id);

-- Allow admin full access
CREATE POLICY "Admin full access to users" ON users FOR ALL USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true)
);

CREATE POLICY "Admin full access to articles" ON articles FOR ALL USING (
    EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND is_admin = true)
);

-- 13. Create Functions for Timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 14. Create Triggers for Auto-updating timestamps
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_articles_updated_at BEFORE UPDATE ON articles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_preferences_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 15. Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Success message
SELECT 'TeenBuzz database setup complete! All tables, indexes, and sample data have been created.' as status;
