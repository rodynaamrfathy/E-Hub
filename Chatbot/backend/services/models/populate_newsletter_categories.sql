-- Enhanced Newsletter Categories with Topics/Keywords
-- This script adds detailed categories with related search topics

-- First, add a topics column if it doesn't exist
ALTER TABLE newsletter_categories
ADD COLUMN IF NOT EXISTS topics JSONB DEFAULT '[]'::jsonb;

-- Ensure is_active column exists with proper default
DO $$
BEGIN
    -- Add is_active if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'newsletter_categories' AND column_name = 'is_active'
    ) THEN
        ALTER TABLE newsletter_categories ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL;
    END IF;

    -- Update any NULL values
    UPDATE newsletter_categories SET is_active = TRUE WHERE is_active IS NULL;

    -- Ensure NOT NULL constraint
    ALTER TABLE newsletter_categories ALTER COLUMN is_active SET DEFAULT TRUE;
    ALTER TABLE newsletter_categories ALTER COLUMN is_active SET NOT NULL;
END $$;

-- Create index for topics search
CREATE INDEX IF NOT EXISTS idx_newsletter_categories_topics
ON newsletter_categories USING GIN (topics);

-- Clear existing categories (optional - comment out if you want to keep existing)
-- TRUNCATE TABLE newsletter_categories CASCADE;

-- ====================================================
-- Insert Enhanced Categories with Topics
-- ====================================================

-- 1. Supply Chain Transparency & Circularity
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Supply Chain Transparency & Circularity',
    'Supply chain transparency, traceability, blockchain, digital product passports, circular supply chains, and sustainable sourcing',
    '[
        "supply chain transparency",
        "sustainable supply chain",
        "circular supply chains",
        "circular supply chain management",
        "supply chain traceability technologies",
        "blockchain in supply chain",
        "digital product passport",
        "DPP",
        "material passport circular economy",
        "sustainable sourcing",
        "circular business models",
        "circular economy strategies",
        "extended producer responsibility",
        "EPR compliance",
        "circular procurement",
        "EU Digital Product Passport"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 2. Digital Transformation & Smart Technologies
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Digital Transformation & Smart Technologies',
    'Digital transformation in waste management, IoT, AI, big data analytics, digital twins, and smart environmental technologies',
    '[
        "digital transformation in waste management",
        "environmental digital transformation",
        "IoT for waste tracking",
        "real-time waste monitoring sensors",
        "AI in circular economy",
        "big data for waste analytics",
        "digital twin lifecycle simulation",
        "green computing",
        "sustainable IT",
        "smart waste management",
        "waste monitoring technology",
        "environmental sensors",
        "AI waste sorting",
        "machine learning recycling"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 3. Plastic Credits & Offsetting
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Plastic Credits & Offsetting',
    'Plastic credit schemes, plastic footprint offsetting, verification standards, plastic neutrality, and market mechanisms',
    '[
        "plastic credits",
        "what are plastic credits",
        "plastic credit schemes",
        "plastic credit financing",
        "plastic footprint offsetting",
        "traceable plastic recovery credits",
        "plastic credit marketplace",
        "plastic credit standards",
        "Verra plastic credits",
        "OBP plastic credits",
        "plastic neutrality",
        "plastic credit verification",
        "plastic credit integrity",
        "social impact of plastic credits",
        "plastic credits and EPR compliance",
        "plastic credits additionality",
        "plastic credit regulation",
        "plastic credits criticisms"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 4. Waste Management & Recycling
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Waste Management & Recycling',
    'Waste management systems, recycling technologies, waste-to-energy, zero waste initiatives, and waste reduction strategies',
    '[
        "waste management",
        "recycling technologies",
        "waste reduction",
        "zero waste",
        "waste-to-energy",
        "landfill diversion",
        "waste sorting",
        "recycling programs",
        "municipal waste management",
        "industrial waste management",
        "hazardous waste management",
        "e-waste recycling",
        "organic waste composting",
        "waste hierarchy"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 5. Community Engagement & Social Impact
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Community Engagement & Social Impact',
    'Citizen engagement, community cleanups, waste reporting, informal sector integration, and social impact initiatives',
    '[
        "citizen-engaged waste reporting",
        "GPS-stamped waste reporting",
        "before-and-after cleanup photos",
        "community-driven cleanup reporting",
        "informal waste sector integration",
        "waste management education",
        "social impact of plastic credit projects",
        "community recycling programs",
        "waste picker support",
        "environmental education",
        "citizen science waste",
        "community composting",
        "neighborhood cleanup initiatives"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 6. Circular Economy & Sustainability
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Circular Economy & Sustainability',
    'Circular economy principles, 3R to 10R frameworks, circular design, zero waste systems, and sustainable business models',
    '[
        "circular economy fundamentals",
        "Reduce Reuse Recycle",
        "3R framework",
        "10R framework",
        "circular product design",
        "circular economy standards",
        "circular economy in agriculture",
        "circular economy in furniture",
        "European circular economy investments",
        "circular economy business models",
        "zero waste circular economy",
        "material lifecycles",
        "economic decoupling",
        "circular economy policy",
        "cradle to cradle design"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 7. SDG & Development Frameworks
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'SDG & Development Frameworks',
    'UN Sustainable Development Goals, SDG targets and indicators, sustainable consumption, climate action, and global frameworks',
    '[
        "SDG 1 No Poverty",
        "SDG 2 Zero Hunger",
        "SDG 3 Good Health",
        "SDG 4 Quality Education",
        "SDG 5 Gender Equality",
        "SDG 6 Clean Water and Sanitation",
        "SDG 7 Affordable Clean Energy",
        "SDG 8 Decent Work",
        "SDG 9 Industry Innovation",
        "SDG 10 Reduced Inequalities",
        "SDG 11 Sustainable Cities",
        "SDG 12 Responsible Consumption",
        "SDG 13 Climate Action",
        "SDG 14 Life Below Water",
        "SDG 15 Life on Land",
        "SDG 16 Peace Justice",
        "SDG 17 Partnerships",
        "sustainable consumption and production",
        "climate action",
        "sustainable cities",
        "biodiversity protection",
        "marine protection",
        "sustainable development targets",
        "SDG indicators"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 8. Climate Change & Environment
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Climate Change & Environment',
    'Climate change, global warming, carbon emissions, climate policy, environmental protection, and climate adaptation',
    '[
        "climate change",
        "global warming",
        "carbon emissions",
        "greenhouse gases",
        "climate policy",
        "Paris Agreement",
        "net zero",
        "carbon neutrality",
        "climate adaptation",
        "climate mitigation",
        "carbon footprint",
        "climate resilience",
        "extreme weather",
        "climate science",
        "IPCC reports"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 9. Renewable Energy
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Renewable Energy',
    'Solar, wind, hydro, and other clean energy sources, energy transition, and sustainable power generation',
    '[
        "renewable energy",
        "solar energy",
        "wind energy",
        "hydroelectric power",
        "geothermal energy",
        "biomass energy",
        "clean energy",
        "energy transition",
        "renewable energy technology",
        "solar panels",
        "wind turbines",
        "energy storage",
        "battery technology",
        "green hydrogen",
        "offshore wind"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 10. Sustainability News & Trends
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Sustainability News & Trends',
    'Latest sustainability news, circularity trends, regulatory updates, business sustainability, and global developments',
    '[
        "circularity news",
        "sustainability news waste management",
        "AI-driven circular economy news",
        "digital product passport updates",
        "regulation-driven digital sustainability",
        "business circularity advocacy",
        "sustainability policy",
        "plastic credits in policy",
        "global plastics treaty developments",
        "ESG regulations",
        "sustainability trends",
        "green business news",
        "environmental policy updates",
        "corporate sustainability",
        "fashion sustainability",
        "traceability news"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 11. Conservation & Biodiversity
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Conservation & Biodiversity',
    'Wildlife protection, habitat preservation, biodiversity conservation, ecosystem restoration, and nature-based solutions',
    '[
        "wildlife conservation",
        "habitat preservation",
        "biodiversity",
        "ecosystem restoration",
        "nature-based solutions",
        "endangered species",
        "wildlife protection",
        "forest conservation",
        "marine conservation",
        "coral reef protection",
        "wetland preservation",
        "species protection",
        "habitat restoration",
        "conservation biology"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 12. Sustainable Living
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Sustainable Living',
    'Eco-friendly lifestyle, green products, sustainability tips, zero waste living, and conscious consumption',
    '[
        "sustainable living",
        "eco-friendly lifestyle",
        "green products",
        "sustainability tips",
        "zero waste living",
        "conscious consumption",
        "sustainable fashion",
        "ethical shopping",
        "eco-friendly home",
        "sustainable food",
        "green cleaning",
        "plastic-free living",
        "minimalist lifestyle",
        "sustainable transportation"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 13. Environmental Policy & Regulation
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Environmental Policy & Regulation',
    'Environmental regulations, laws, compliance, government initiatives, international agreements, and policy frameworks',
    '[
        "environmental policy",
        "environmental regulations",
        "environmental law",
        "EPR regulations",
        "plastic ban policies",
        "carbon pricing",
        "emissions trading",
        "environmental compliance",
        "green legislation",
        "environmental standards",
        "international environmental agreements",
        "environmental governance",
        "policy advocacy",
        "regulatory frameworks"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 14. Green Technology & Innovation
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Green Technology & Innovation',
    'Environmental innovations, clean tech, sustainable technologies, green engineering, and eco-innovations',
    '[
        "green technology",
        "clean tech",
        "environmental innovation",
        "sustainable technologies",
        "green engineering",
        "eco-innovation",
        "cleantech startups",
        "environmental technology",
        "sustainable materials",
        "bio-based materials",
        "green chemistry",
        "environmental biotechnology",
        "sustainable packaging",
        "recycling technology"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 15. Ocean & Marine Life
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Ocean & Marine Life',
    'Ocean conservation, marine pollution, plastic in oceans, marine ecosystems, and aquatic life protection',
    '[
        "ocean conservation",
        "marine pollution",
        "plastic in oceans",
        "ocean plastic",
        "marine ecosystems",
        "coral reefs",
        "marine biodiversity",
        "overfishing",
        "marine protected areas",
        "ocean acidification",
        "marine debris",
        "ghost fishing gear",
        "ocean cleanup",
        "sustainable fisheries",
        "blue economy"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- 16. Regional & Brand Context (Dawar/Egypt)
INSERT INTO newsletter_categories (name, description, topics) VALUES (
    'Regional Sustainability & Local Impact',
    'Regional circular solutions, local waste management initiatives, Egypt sustainability, and Dawar platform developments',
    '[
        "scalable circular solutions Egypt",
        "Dawar app",
        "waste traceability solution",
        "digital waste management platform",
        "post-consumer waste tracking",
        "zero-to-landfill traceability",
        "Dawar traceability dashboards",
        "Egypt waste management",
        "MENA sustainability",
        "regional circular economy",
        "local environmental initiatives",
        "Egypt environmental policy",
        "Middle East sustainability",
        "North Africa waste management"
    ]'::jsonb
) ON CONFLICT (name) DO UPDATE SET
    description = EXCLUDED.description,
    topics = EXCLUDED.topics;

-- ====================================================
-- Verify Installation
-- ====================================================

-- Count categories
SELECT COUNT(*) as total_categories FROM newsletter_categories;

-- View all categories with topic counts
SELECT
    id,
    name,
    description,
    jsonb_array_length(topics) as topic_count,
    is_active
FROM newsletter_categories
ORDER BY name;

-- Search example: Find categories related to "plastic"
-- SELECT
--     name,
--     description
-- FROM newsletter_categories
-- WHERE topics @> '["plastic credits"]'::jsonb
--    OR name ILIKE '%plastic%'
--    OR description ILIKE '%plastic%';

-- ====================================================
-- Helper: View all topics across categories
-- ====================================================

-- SELECT DISTINCT jsonb_array_elements_text(topics) as topic
-- FROM newsletter_categories
-- ORDER BY topic;
