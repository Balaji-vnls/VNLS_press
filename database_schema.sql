-- Personalized News Recommendation System Database Schema
-- Run this in Supabase SQL Editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Profiles Table
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- News Articles Table
CREATE TABLE IF NOT EXISTS news_articles (
    id VARCHAR(255) PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    summary TEXT,
    url TEXT,
    source VARCHAR(255),
    category VARCHAR(100),
    published_at TIMESTAMP WITH TIME ZONE,
    image_url TEXT,
    author VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User Interactions Table
CREATE TABLE IF NOT EXISTS user_interactions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    article_id VARCHAR(255) REFERENCES news_articles(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50) NOT NULL, -- 'click', 'read', 'like', 'share', 'bookmark', 'feedback'
    duration FLOAT, -- time spent reading (in seconds)
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recommendation Logs Table
CREATE TABLE IF NOT EXISTS recommendation_logs (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    article_ids TEXT[], -- array of article IDs
    scores FLOAT[], -- corresponding recommendation scores
    algorithm VARCHAR(100) DEFAULT 'mtl_model',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_news_articles_category ON news_articles(category);
CREATE INDEX IF NOT EXISTS idx_news_articles_published_at ON news_articles(published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_articles_source ON news_articles(source);
CREATE INDEX IF NOT EXISTS idx_user_interactions_user_id ON user_interactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_article_id ON user_interactions(article_id);
CREATE INDEX IF NOT EXISTS idx_user_interactions_timestamp ON user_interactions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_user_interactions_type ON user_interactions(interaction_type);
CREATE INDEX IF NOT EXISTS idx_recommendation_logs_user_id ON recommendation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_recommendation_logs_timestamp ON recommendation_logs(timestamp DESC);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_user_profiles_updated_at 
    BEFORE UPDATE ON user_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_news_articles_updated_at 
    BEFORE UPDATE ON news_articles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) Policies
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE recommendation_logs ENABLE ROW LEVEL SECURITY;

-- User profiles: users can only access their own profile
CREATE POLICY "Users can view own profile" ON user_profiles
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON user_profiles
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON user_profiles
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User interactions: users can only access their own interactions
CREATE POLICY "Users can view own interactions" ON user_interactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own interactions" ON user_interactions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Recommendation logs: users can only access their own logs
CREATE POLICY "Users can view own recommendation logs" ON recommendation_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service can insert recommendation logs" ON recommendation_logs
    FOR INSERT WITH CHECK (true); -- Allow service to insert logs

-- News articles: public read access
ALTER TABLE news_articles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Anyone can view news articles" ON news_articles
    FOR SELECT USING (true);

-- Allow service role to insert/update news articles
CREATE POLICY "Service can manage news articles" ON news_articles
    FOR ALL USING (auth.role() = 'service_role');

-- Create views for analytics
CREATE OR REPLACE VIEW user_reading_stats AS
SELECT 
    ui.user_id,
    COUNT(*) as total_interactions,
    COUNT(DISTINCT ui.article_id) as unique_articles_read,
    COUNT(DISTINCT na.category) as categories_explored,
    AVG(ui.duration) as avg_reading_time,
    MAX(ui.timestamp) as last_activity
FROM user_interactions ui
LEFT JOIN news_articles na ON ui.article_id = na.id
WHERE ui.interaction_type IN ('read', 'click')
GROUP BY ui.user_id;

CREATE OR REPLACE VIEW popular_articles AS
SELECT 
    na.id,
    na.title,
    na.category,
    na.source,
    na.published_at,
    COUNT(ui.id) as interaction_count,
    COUNT(DISTINCT ui.user_id) as unique_readers,
    AVG(ui.duration) as avg_reading_time
FROM news_articles na
LEFT JOIN user_interactions ui ON na.id = ui.article_id
WHERE ui.interaction_type IN ('read', 'click')
    AND ui.timestamp > NOW() - INTERVAL '7 days'
GROUP BY na.id, na.title, na.category, na.source, na.published_at
ORDER BY interaction_count DESC;

CREATE OR REPLACE VIEW category_popularity AS
SELECT 
    na.category,
    COUNT(ui.id) as interaction_count,
    COUNT(DISTINCT ui.user_id) as unique_readers,
    AVG(ui.duration) as avg_reading_time
FROM news_articles na
LEFT JOIN user_interactions ui ON na.id = ui.article_id
WHERE ui.interaction_type IN ('read', 'click')
    AND ui.timestamp > NOW() - INTERVAL '30 days'
GROUP BY na.category
ORDER BY interaction_count DESC;

-- Insert sample categories (optional)
INSERT INTO news_articles (id, title, content, category, source, published_at) VALUES
('sample-tech', 'Sample Tech Article', 'Sample content for technology', 'technology', 'Sample Source', NOW()),
('sample-business', 'Sample Business Article', 'Sample content for business', 'business', 'Sample Source', NOW()),
('sample-health', 'Sample Health Article', 'Sample content for health', 'health', 'Sample Source', NOW())
ON CONFLICT (id) DO NOTHING;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;

-- Refresh the schema cache
NOTIFY pgrst, 'reload schema';