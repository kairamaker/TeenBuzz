-- Add fields for original article information
ALTER TABLE articles ADD COLUMN IF NOT EXISTS original_title TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS original_author TEXT;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS publish_date DATE;

-- Update existing articles with default values
UPDATE articles 
SET original_title = headline 
WHERE original_title IS NULL;

UPDATE articles 
SET publish_date = DATE(created_at) 
WHERE publish_date IS NULL;

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_original_title ON articles(original_title);
CREATE INDEX IF NOT EXISTS idx_articles_original_author ON articles(original_author);
CREATE INDEX IF NOT EXISTS idx_articles_publish_date ON articles(publish_date);

-- Validate URLs (ensure they start with http/https)
UPDATE articles 
SET original_url = CASE 
    WHEN original_url IS NOT NULL AND original_url != '' 
    AND (original_url NOT LIKE 'http://%' AND original_url NOT LIKE 'https://%')
    THEN 'https://' || original_url
    ELSE original_url
END;
