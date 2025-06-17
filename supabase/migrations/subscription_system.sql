
-- Update users table for subscription management
ALTER TABLE public.users 
ADD COLUMN IF NOT EXISTS stripe_customer_id text,
ADD COLUMN IF NOT EXISTS subscription_status text DEFAULT 'inactive';

-- Create comprehensive subscriptions table
DROP TABLE IF EXISTS public.subscriptions;
CREATE TABLE public.subscriptions (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    stripe_subscription_id text UNIQUE NOT NULL,
    stripe_customer_id text NOT NULL,
    status text NOT NULL DEFAULT 'inactive',
    price_id text NOT NULL,
    current_period_start timestamp with time zone NOT NULL,
    current_period_end timestamp with time zone NOT NULL,
    cancel_at_period_end boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create credit usage tracking table
CREATE TABLE IF NOT EXISTS public.credit_usage (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    credits_used integer NOT NULL,
    credits_remaining integer NOT NULL,
    action_type text NOT NULL,
    analysis_id uuid REFERENCES public.analysis_history(id),
    admin_id uuid REFERENCES public.users(id),
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create webhook events table if not exists
CREATE TABLE IF NOT EXISTS public.webhook_events (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    stripe_event_id text UNIQUE,
    event_type text NOT NULL,
    data jsonb NOT NULL,
    processed boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS subscriptions_user_id_idx ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS subscriptions_stripe_subscription_id_idx ON public.subscriptions(stripe_subscription_id);
CREATE INDEX IF NOT EXISTS subscriptions_status_idx ON public.subscriptions(status);

CREATE INDEX IF NOT EXISTS credit_usage_user_id_idx ON public.credit_usage(user_id);
CREATE INDEX IF NOT EXISTS credit_usage_created_at_idx ON public.credit_usage(created_at);
CREATE INDEX IF NOT EXISTS credit_usage_action_type_idx ON public.credit_usage(action_type);

CREATE INDEX IF NOT EXISTS webhook_events_stripe_event_id_idx ON public.webhook_events(stripe_event_id);
CREATE INDEX IF NOT EXISTS webhook_events_event_type_idx ON public.webhook_events(event_type);
CREATE INDEX IF NOT EXISTS webhook_events_processed_idx ON public.webhook_events(processed);

-- Enable RLS
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.webhook_events ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for subscriptions
CREATE POLICY "Users can view own subscriptions" ON public.subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage subscriptions" ON public.subscriptions
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Create RLS policies for credit usage
CREATE POLICY "Users can view own credit usage" ON public.credit_usage
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage credit usage" ON public.credit_usage
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Create RLS policies for webhook events
CREATE POLICY "Only service role can access webhook events" ON public.webhook_events
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Update users RLS policy for new columns
DROP POLICY IF EXISTS "Users can update own profile" ON public.users;
CREATE POLICY "Users can update own profile" ON public.users
    FOR UPDATE USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Function to automatically update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at
    BEFORE UPDATE ON public.subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON public.users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
