# Create New Supabase Project

## Steps to Create a New Supabase Project:

1. **Go to Supabase Dashboard**
   - Visit: https://supabase.com
   - Sign in to your account

2. **Create New Project**
   - Click "New Project"
   - Choose your organization
   - Enter project name: "TeenBuzz-New"
   - Choose a strong database password
   - Select a region close to you
   - Click "Create new project"

3. **Wait for Project Setup**
   - This usually takes 1-2 minutes
   - Wait for the project to be fully initialized

4. **Get New Credentials**
   - Go to Settings → API
   - Copy the new Project URL
   - Copy the new anon public key

5. **Update .env File**
   - Replace the old SUPABASE_URL with the new one
   - Replace the old SUPABASE_KEY with the new one

6. **Test Connection**
   - Run: `python test_database_fix.py`
   - Should show successful connection

## Alternative: Check Current Project Status

If you want to keep the current project:

1. **Check Project Status**
   - Go to your Supabase dashboard
   - Check if the project is still active
   - Look for any error messages

2. **Try Different Region**
   - The project might be in a region with DNS issues
   - Consider recreating in a different region

3. **Contact Supabase Support**
   - If the project seems stuck, contact support
   - They can help resolve DNS issues
