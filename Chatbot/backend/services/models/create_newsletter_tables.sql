-- Newsletter Tables Creation Script
-- Database: PostgreSQL

-- ====================================================
-- Table: newsletter_categories
-- Purpose: Store newsletter topic categories
-- ====================================================
CREATE TABLE IF NOT EXISTS newsletter_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_newsletter_categories_name ON newsletter_categories(name);
CREATE INDEX IF NOT EXISTS idx_newsletter_categories_is_active ON newsletter_categories(is_active);

-- ====================================================
-- Table: newsletter_subscribers
-- Purpose: Store newsletter subscriber information
-- ====================================================
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    categories JSONB DEFAULT '[]'::jsonb,  -- Array of subscribed category IDs
    subscribed_at TIMESTAMP NOT NULL DEFAULT NOW(),
    unsubscribed_at TIMESTAMP,
    last_sent_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_email ON newsletter_subscribers(email);
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_is_active ON newsletter_subscribers(is_active);
CREATE INDEX IF NOT EXISTS idx_newsletter_subscribers_categories ON newsletter_subscribers USING GIN (categories);

-- ====================================================
-- Table: generated_articles
-- Purpose: Store AI-generated newsletter articles
-- ====================================================
CREATE TABLE IF NOT EXISTS generated_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    topic VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL,
    source_articles JSONB DEFAULT '[]'::jsonb,  -- Array of source article IDs
    references JSONB DEFAULT '[]'::jsonb,       -- Array of reference objects
    word_count INTEGER,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    sent_to_subscribers BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_generated_articles_category
        FOREIGN KEY (category_id)
        REFERENCES newsletter_categories(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_generated_articles_category_id ON generated_articles(category_id);
CREATE INDEX IF NOT EXISTS idx_generated_articles_generated_at ON generated_articles(generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_generated_articles_sent ON generated_articles(sent_to_subscribers);

-- ====================================================
-- Insert Default Categories
-- ====================================================
INSERT INTO newsletter_categories (name, description) VALUES
    ('Climate Change', 'News about climate change, global warming, and environmental policy'),
    ('Renewable Energy', 'Solar, wind, hydro, and other clean energy sources'),
    ('Waste Management', 'Recycling, waste reduction, and circular economy'),
    ('Conservation', 'Wildlife protection, habitat preservation, and biodiversity'),
    ('Sustainable Living', 'Eco-friendly lifestyle, green products, and sustainability tips'),
    ('Environmental Policy', 'Environmental regulations, laws, and government initiatives'),
    ('Green Technology', 'Innovations in environmental and sustainable technologies'),
    ('Ocean & Marine Life', 'Ocean conservation, marine pollution, and aquatic ecosystems')
ON CONFLICT (name) DO NOTHING;

-- ====================================================
-- Helpful Queries for Management
-- ====================================================

-- View all categories with article counts
-- SELECT
--     c.id,
--     c.name,
--     c.description,
--     c.is_active,
--     COUNT(ga.id) as article_count
-- FROM newsletter_categories c
-- LEFT JOIN generated_articles ga ON c.id = ga.category_id
-- GROUP BY c.id, c.name, c.description, c.is_active
-- ORDER BY c.name;

-- View subscriber statistics
-- SELECT
--     COUNT(*) as total_subscribers,
--     COUNT(*) FILTER (WHERE is_active = TRUE) as active_subscribers,
--     COUNT(*) FILTER (WHERE is_active = FALSE) as unsubscribed
-- FROM newsletter_subscribers;

-- View subscribers by category preference
-- SELECT
--     c.name as category_name,
--     COUNT(DISTINCT s.id) as subscriber_count
-- FROM newsletter_categories c
-- CROSS JOIN newsletter_subscribers s
-- WHERE s.is_active = TRUE
--   AND s.categories ? c.id::text
-- GROUP BY c.name
-- ORDER BY subscriber_count DESC;

-- View recent generated articles
-- SELECT
--     ga.id,
--     ga.title,
--     ga.topic,
--     c.name as category,
--     ga.word_count,
--     ga.generated_at,
--     ga.sent_to_subscribers,
--     jsonb_array_length(ga.references) as reference_count
-- FROM generated_articles ga
-- JOIN newsletter_categories c ON ga.category_id = c.id
-- ORDER BY ga.generated_at DESC
-- LIMIT 10;

-- ====================================================
-- Clean Up (Use with caution!)
-- ====================================================

-- Drop all newsletter tables (DESTRUCTIVE)
-- DROP TABLE IF EXISTS generated_articles CASCADE;
-- DROP TABLE IF EXISTS newsletter_subscribers CASCADE;
-- DROP TABLE IF EXISTS newsletter_categories CASCADE;
