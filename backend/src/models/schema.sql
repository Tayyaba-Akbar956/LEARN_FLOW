-- LearnFlow Database Schema
-- PostgreSQL 14+

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'teacher', 'admin')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(50) NOT NULL CHECK (session_type IN ('chat', 'code', 'exercise')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_seconds INTEGER,
    metadata JSONB DEFAULT '{}',
    consent_given BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_started_at ON sessions(started_at);
CREATE INDEX idx_sessions_is_active ON sessions(is_active);

-- Exercises table
CREATE TABLE IF NOT EXISTS exercises (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level BETWEEN 1 AND 10),
    topic VARCHAR(100) NOT NULL,
    starter_code TEXT,
    solution_code TEXT,
    test_cases JSONB NOT NULL DEFAULT '[]',
    hints JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_exercises_difficulty ON exercises(difficulty_level);
CREATE INDEX idx_exercises_topic ON exercises(topic);
CREATE INDEX idx_exercises_created_at ON exercises(created_at);

-- Exercise attempts table
CREATE TABLE IF NOT EXISTS exercise_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exercise_id UUID NOT NULL REFERENCES exercises(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    submitted_code TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    execution_time_ms INTEGER,
    hints_used INTEGER DEFAULT 0,
    attempt_number INTEGER NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    feedback TEXT,
    test_results JSONB DEFAULT '[]'
);

CREATE INDEX idx_exercise_attempts_user_id ON exercise_attempts(user_id);
CREATE INDEX idx_exercise_attempts_exercise_id ON exercise_attempts(exercise_id);
CREATE INDEX idx_exercise_attempts_session_id ON exercise_attempts(session_id);
CREATE INDEX idx_exercise_attempts_submitted_at ON exercise_attempts(submitted_at);

-- Struggle events table
CREATE TABLE IF NOT EXISTS struggle_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN ('failure', 'timeout', 'help_request', 'repeated_error', 'prolonged_inactivity')),
    severity INTEGER NOT NULL CHECK (severity BETWEEN 1 AND 5),
    context JSONB NOT NULL DEFAULT '{}',
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_type VARCHAR(50) CHECK (resolution_type IN ('self_resolved', 'ai_helped', 'teacher_intervened', 'abandoned'))
);

CREATE INDEX idx_struggle_events_user_id ON struggle_events(user_id);
CREATE INDEX idx_struggle_events_session_id ON struggle_events(session_id);
CREATE INDEX idx_struggle_events_detected_at ON struggle_events(detected_at);
CREATE INDEX idx_struggle_events_severity ON struggle_events(severity);

-- Teacher alerts table
CREATE TABLE IF NOT EXISTS teacher_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    teacher_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('struggle_detected', 'prolonged_struggle', 'repeated_failures', 'help_requested')),
    priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 5),
    message TEXT NOT NULL,
    context JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'acknowledged', 'in_progress', 'resolved', 'dismissed'))
);

CREATE INDEX idx_teacher_alerts_student_id ON teacher_alerts(student_id);
CREATE INDEX idx_teacher_alerts_teacher_id ON teacher_alerts(teacher_id);
CREATE INDEX idx_teacher_alerts_status ON teacher_alerts(status);
CREATE INDEX idx_teacher_alerts_priority ON teacher_alerts(priority);
CREATE INDEX idx_teacher_alerts_created_at ON teacher_alerts(created_at);

-- Messages table (chat history)
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'teacher')),
    content TEXT NOT NULL,
    agent_type VARCHAR(50) CHECK (agent_type IN ('concept_explainer', 'debugger', 'hint_provider', 'exercise_generator', 'human')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    parent_message_id UUID REFERENCES messages(id) ON DELETE SET NULL
);

CREATE INDEX idx_messages_session_id ON messages(session_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- Code submissions table
CREATE TABLE IF NOT EXISTS code_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL DEFAULT 'python',
    execution_status VARCHAR(20) NOT NULL CHECK (execution_status IN ('pending', 'running', 'success', 'error', 'timeout')),
    stdout TEXT,
    stderr TEXT,
    execution_time_ms INTEGER,
    memory_used_kb INTEGER,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    executed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_code_submissions_user_id ON code_submissions(user_id);
CREATE INDEX idx_code_submissions_session_id ON code_submissions(session_id);
CREATE INDEX idx_code_submissions_submitted_at ON code_submissions(submitted_at);
CREATE INDEX idx_code_submissions_status ON code_submissions(execution_status);

-- Student progress tracking
CREATE TABLE IF NOT EXISTS student_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic VARCHAR(100) NOT NULL,
    current_difficulty_level INTEGER NOT NULL CHECK (current_difficulty_level BETWEEN 1 AND 10),
    exercises_completed INTEGER DEFAULT 0,
    exercises_attempted INTEGER DEFAULT 0,
    success_rate DECIMAL(5,2),
    average_time_seconds INTEGER,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, topic)
);

CREATE INDEX idx_student_progress_user_id ON student_progress(user_id);
CREATE INDEX idx_student_progress_topic ON student_progress(topic);

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_student_progress_updated_at BEFORE UPDATE ON student_progress
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Comments for documentation
COMMENT ON TABLE users IS 'Stores user accounts (students, teachers, admins)';
COMMENT ON TABLE sessions IS 'Tracks user learning sessions with consent for monitoring';
COMMENT ON TABLE exercises IS 'Stores coding exercises with difficulty levels and test cases';
COMMENT ON TABLE exercise_attempts IS 'Records student attempts at exercises';
COMMENT ON TABLE struggle_events IS 'Tracks indicators of student struggle for intervention';
COMMENT ON TABLE teacher_alerts IS 'Alerts for teachers when students need help';
COMMENT ON TABLE messages IS 'Chat message history between students and AI tutors';
COMMENT ON TABLE code_submissions IS 'Records code execution requests and results';
COMMENT ON TABLE student_progress IS 'Tracks student progress and adaptive difficulty';
