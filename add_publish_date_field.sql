-- Add publish_date field to articles table
ALTER TABLE articles ADD COLUMN IF NOT EXISTS publish_date DATE;

-- Update existing articles with a default publish_date (using created_at)
UPDATE articles 
SET publish_date = DATE(created_at) 
WHERE publish_date IS NULL;

-- Make publish_date NOT NULL for future articles
ALTER TABLE articles ALTER COLUMN publish_date SET NOT NULL;

-- Add index for better performance when filtering by date
CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date);
CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source);
