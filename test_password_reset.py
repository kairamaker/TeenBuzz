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

# Test if password_reset_tokens table exists
try:
    # Try to insert a test record
    result = supabase.table('password_reset_tokens').insert({
        'user_id': 1,
        'token': 'test_token_123',
        'expires_at': '2025-12-31T23:59:59Z'
    }).execute()
    print("✅ password_reset_tokens table exists and is working!")
    
    # Clean up test record
    supabase.table('password_reset_tokens').delete().eq('token', 'test_token_123').execute()
    print("✅ Test record cleaned up")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nYou need to create the password_reset_tokens table manually in your Supabase dashboard.")
    print("Go to your Supabase dashboard > SQL Editor and run this SQL:")
    print("""
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

ALTER TABLE password_reset_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all operations on password_reset_tokens" ON password_reset_tokens
    FOR ALL USING (true);
    """) 