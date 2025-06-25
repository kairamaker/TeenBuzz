-- Fix RLS policies to allow INSERT operations for articles
-- Run this in your Supabase SQL editor

-- Add policy to allow INSERT operations on articles table
CREATE POLICY "Allow INSERT on articles" ON articles FOR INSERT WITH CHECK (true);

-- Add policy to allow UPDATE operations on articles table (for future admin features)
CREATE POLICY "Allow UPDATE on articles" ON articles FOR UPDATE USING (true);

-- Add policy to allow DELETE operations on articles table (for future admin features)
CREATE POLICY "Allow DELETE on articles" ON articles FOR DELETE USING (true);

-- Also add policies for categories table
CREATE POLICY "Allow INSERT on categories" ON categories FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow UPDATE on categories" ON categories FOR UPDATE USING (true);
CREATE POLICY "Allow DELETE on categories" ON categories FOR DELETE USING (true); 