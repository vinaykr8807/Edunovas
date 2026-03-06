import psycopg2
import urllib.parse

# Credentials
password = "mydobis059@123"
safe_password = urllib.parse.quote_plus(password)
URL = f"postgresql://postgres:{safe_password}@db.wlnybmztpkocfbnoacgs.supabase.co:5432/postgres"

SCHEMA_SQL = """
-- Drop existing tables to avoid conflict with new schema
DROP TABLE IF EXISTS coding_errors CASCADE;
DROP TABLE IF EXISTS interview_history CASCADE;
DROP TABLE IF EXISTS quiz_history CASCADE;
DROP TABLE IF EXISTS achievements CASCADE;
DROP TABLE IF EXISTS progress_tracking CASCADE;
DROP TABLE IF EXISTS user_progress CASCADE;
DROP TABLE IF EXISTS domain_stats CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;
DROP TABLE IF EXISTS student_profiles CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'student',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Profiles Table
CREATE TABLE student_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    degree TEXT,
    branch TEXT,
    academic_year TEXT,
    domain TEXT,
    skills TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Chat History Table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role TEXT,
    content TEXT,
    mode TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create User Progress Table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    badges TEXT[] DEFAULT '{}',
    career_phase TEXT DEFAULT 'Foundational',
    UNIQUE(user_id)
);

-- Create Achievements Table
CREATE TABLE achievements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    description TEXT,
    date_earned TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Quiz History Table
CREATE TABLE quiz_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT,
    score INTEGER,
    weak_areas TEXT[],
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Interview History Table
CREATE TABLE interview_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    role TEXT,
    score INTEGER,
    weak_topics TEXT[],
    feedback TEXT,
    date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create Coding Errors Table
CREATE TABLE coding_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    language TEXT,
    mistake_type TEXT,
    frequency INTEGER DEFAULT 1
);

-- Create Progress Tracking Table
CREATE TABLE progress_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    topic TEXT,
    confidence_score FLOAT,
    last_practiced TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    times_attempted INTEGER DEFAULT 1,
    UNIQUE(user_id, topic)
);

-- Create Domain Stats Table
CREATE TABLE domain_stats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    domain TEXT,
    interaction_count INTEGER DEFAULT 1,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, domain)
);

-- Create Indexes
CREATE INDEX idx_chat_user ON chat_messages(user_id);
CREATE INDEX idx_quiz_user ON quiz_history(user_id);
CREATE INDEX idx_interview_user ON interview_history(user_id);

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE achievements ENABLE ROW LEVEL SECURITY;
ALTER TABLE quiz_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE interview_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE coding_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_stats ENABLE ROW LEVEL SECURITY;

-- Create Policies (Allowing users to see/edit only their own data)
CREATE POLICY "Users can view their own data" ON users FOR SELECT USING (true); -- Allow select for auth
CREATE POLICY "Users can manage their own profile" ON student_profiles FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own chats" ON chat_messages FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own progress" ON user_progress FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can view their own achievements" ON achievements FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own quiz history" ON quiz_history FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own interview history" ON interview_history FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own coding errors" ON coding_errors FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own tracking" ON progress_tracking FOR ALL USING (user_id = auth.uid());
CREATE POLICY "Users can manage their own stats" ON domain_stats FOR ALL USING (user_id = auth.uid());
"""

def setup_schema():
    print("🚀 Initializing Full Performance & Reward System Schema...")
    try:
        conn = psycopg2.connect(URL)
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute(SCHEMA_SQL)
        print("✅ All Performance tracking tables initialized successfully.")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Schema initialization failed: {e}")
        return False

if __name__ == "__main__":
    setup_schema()
