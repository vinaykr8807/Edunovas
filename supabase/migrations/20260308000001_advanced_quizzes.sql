-- Migration: Enhance Quiz and Progress Tracking for Advanced Features

-- Add quiz_mode and confidence_score to quiz_history
ALTER TABLE public.quiz_history 
ADD COLUMN IF NOT EXISTS quiz_mode TEXT DEFAULT 'standard',
ADD COLUMN IF NOT EXISTS average_confidence FLOAT DEFAULT 0;

-- Add mastery_level to progress_tracking for Knowledge Graph
ALTER TABLE public.progress_tracking
ADD COLUMN IF NOT EXISTS mastery_level FLOAT DEFAULT 0,
ADD COLUMN IF NOT EXISTS topic_status TEXT DEFAULT 'learning'; -- 'idle', 'learning', 'done', 'struggling'

-- Add knowledge_graph storage to user_progress for faster rendering
ALTER TABLE public.user_progress
ADD COLUMN IF NOT EXISTS knowledge_graph JSONB DEFAULT '{}'::jsonb;

-- Create a table for adaptive learning logs (AI detecting weak areas)
CREATE TABLE IF NOT EXISTS public.adaptive_learning_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    subtopic TEXT,
    gap_analysis TEXT,
    remediation_steps TEXT[],
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- RLS for the new table
ALTER TABLE public.adaptive_learning_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage their own logs" ON public.adaptive_learning_logs FOR ALL USING (user_id = auth.uid());
