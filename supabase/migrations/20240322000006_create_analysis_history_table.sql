-- Create analysis_history table for storing product analysis results
CREATE TABLE IF NOT EXISTS public.analysis_history (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id text NOT NULL REFERENCES public.users(user_id),
    product_name text NOT NULL,
    product_image text,
    recommended_price numeric NOT NULL,
    recommended_platform text NOT NULL,
    analysis_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS analysis_history_user_id_idx ON public.analysis_history(user_id);
CREATE INDEX IF NOT EXISTS analysis_history_created_at_idx ON public.analysis_history(created_at DESC);

-- Enable RLS
ALTER TABLE public.analysis_history ENABLE ROW LEVEL SECURITY;

-- Create policy for users to see only their own analysis history
DROP POLICY IF EXISTS "Users can view own analysis history" ON public.analysis_history;
CREATE POLICY "Users can view own analysis history" ON public.analysis_history
    FOR ALL USING (auth.uid()::text = user_id);

-- Enable realtime
alter publication supabase_realtime add table analysis_history;
