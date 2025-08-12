import os
from dotenv import load_dotenv
from supabase.client import create_client, Client

load_dotenv()

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')

if not url or not key:
    print("Error: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(url, key)

# SQL to create password reset tokens table
sql = """
-- Create password reset tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for faster token lookups
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

-- Enable RLS (Row Level Security)
ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations (since this is for password reset)
CREATE POLICY "Allow all operations on password_reset_tokens" ON password_reset_tokens
    FOR ALL USING (true);
"""

try:
    # Execute the SQL
    result = supabase.rpc('exec_sql', {'sql': sql}).execute()
    print("Password reset tokens table created successfully!")
except Exception as e:
    print(f"Error creating table: {e}")
    print("You may need to run this SQL manually in your Supabase dashboard:")
    print(sql) 