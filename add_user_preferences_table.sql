-- Add user preferences table for email and topic interests
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    topics TEXT[], -- Array of selected topics
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for email lookups
CREATE INDEX IF NOT EXISTS idx_user_preferences_email ON user_preferences(email);

-- Enable RLS
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can insert preferences" ON user_preferences FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can update their own preferences" ON user_preferences FOR UPDATE USING (true);
CREATE POLICY "Users can view their own preferences" ON user_preferences FOR SELECT USING (true); 