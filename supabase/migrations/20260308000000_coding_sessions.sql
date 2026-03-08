CREATE TABLE IF NOT EXISTS public.coding_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES public.users(id) ON DELETE CASCADE,
    optimization_score NUMERIC NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE public.coding_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can insert their own coding sessions"
ON public.coding_sessions FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view their own coding sessions"
ON public.coding_sessions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Service role can view all coding sessions"
ON public.coding_sessions FOR ALL
TO service_role
USING (true)
WITH CHECK (true);
