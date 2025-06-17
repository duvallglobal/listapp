
import { loadStripe } from '@stripe/stripe-js';
import { supabase, handleSupabaseError } from '@/lib/supabase';
import { toast } from '@/components/ui/use-toast';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY!);

export interface SubscriptionTier {
  id: string;
  name: string;
  price: number;
  interval: string;
  features: string[];
  analysisLimit: number;
  stripePriceId?: string;
  popular?: boolean;
  description: string;
}

export interface UserSubscription {
  id: string;
  user_id: string;
  stripe_subscription_id: string;
  stripe_customer_id: string;
  status: string;
  price_id: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreditUsage {
  id: string;
  user_id: string;
  credits_used: number;
  credits_remaining: number;
  action_type: string;
  analysis_id?: string;
  created_at: string;
}

export const subscriptionTiers: SubscriptionTier[] = [
  {
    id: "free_trial",
    name: "Free Trial",
    price: 0,
    interval: "forever",
    analysisLimit: 2,
    description: "Perfect for trying out our platform",
    features: [
      "2 product analyses",
      "Basic marketplace comparison",
      "Standard fee calculations",
      "Email support"
    ]
  },
  {
    id: "basic",
    name: "Basic",
    price: 9.99,
    interval: "month",
    analysisLimit: 50,
    description: "Great for individuals and small sellers",
    stripePriceId: "price_basic_monthly",
    features: [
      "50 product analyses per month",
      "Advanced marketplace comparison",
      "Detailed fee calculations",
      "Priority email support",
      "Export data to CSV"
    ]
  },
  {
    id: "pro",
    name: "Pro",
    price: 29.99,
    interval: "month",
    analysisLimit: 200,
    popular: true,
    description: "Perfect for growing businesses",
    stripePriceId: "price_pro_monthly",
    features: [
      "200 product analyses per month",
      "AI-powered pricing recommendations",
      "Advanced profit optimization",
      "Live chat support",
      "API access",
      "Custom reports",
      "Historical data analysis"
    ]
  },
  {
    id: "business",
    name: "Business",
    price: 99.99,
    interval: "month",
    analysisLimit: 1000,
    description: "Designed for established businesses",
    stripePriceId: "price_business_monthly",
    features: [
      "1,000 product analyses per month",
      "Advanced AI insights",
      "Multi-marketplace optimization",
      "Dedicated account manager",
      "Custom integrations",
      "White-label reports",
      "Team collaboration tools",
      "Priority phone support"
    ]
  },
  {
    id: "enterprise",
    name: "Enterprise",
    price: 299.99,
    interval: "month",
    analysisLimit: 5000,
    description: "For large organizations with custom needs",
    stripePriceId: "price_enterprise_monthly",
    features: [
      "5,000+ product analyses per month",
      "Custom AI model training",
      "Enterprise-grade security",
      "24/7 dedicated support",
      "Custom API endpoints",
      "Advanced analytics dashboard",
      "SSO integration",
      "SLA guarantees",
      "On-premise deployment options"
    ]
  }
];

class SubscriptionService {
  async createCheckoutSession(priceId: string, userId: string) {
    try {
      const { data, error } = await supabase.functions.invoke('create-checkout', {
        body: {
          priceId,
          userId,
          successUrl: `${window.location.origin}/subscription?success=true`,
          cancelUrl: `${window.location.origin}/subscription?canceled=true`
        }
      });

      if (error) throw error;

      const stripe = await stripePromise;
      if (!stripe) throw new Error('Stripe failed to load');

      const { error: stripeError } = await stripe.redirectToCheckout({
        sessionId: data.sessionId
      });

      if (stripeError) throw stripeError;
    } catch (error) {
      console.error('Error creating checkout session:', error);
      toast({
        title: "Payment Error",
        description: "Failed to start checkout process. Please try again.",
        variant: "destructive"
      });
      throw error;
    }
  }

  async getCurrentSubscription(userId: string): Promise<UserSubscription | null> {
    try {
      const { data, error } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('user_id', userId)
        .eq('status', 'active')
        .single();

      if (error && error.code !== 'PGRST116') {
        throw error;
      }

      return data;
    } catch (error) {
      console.error('Error fetching subscription:', error);
      return null;
    }
  }

  async cancelSubscription(subscriptionId: string) {
    try {
      const { data, error } = await supabase.functions.invoke('cancel-subscription', {
        body: { subscriptionId }
      });

      if (error) throw error;

      toast({
        title: "Subscription Cancelled",
        description: "Your subscription will be cancelled at the end of the current billing period."
      });

      return data;
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      toast({
        title: "Cancellation Error",
        description: "Failed to cancel subscription. Please try again.",
        variant: "destructive"
      });
      throw error;
    }
  }

  async upgradeSubscription(newPriceId: string, currentSubscriptionId: string) {
    try {
      const { data, error } = await supabase.functions.invoke('upgrade-subscription', {
        body: {
          subscriptionId: currentSubscriptionId,
          newPriceId
        }
      });

      if (error) throw error;

      toast({
        title: "Subscription Updated",
        description: "Your subscription has been successfully updated."
      });

      return data;
    } catch (error) {
      console.error('Error upgrading subscription:', error);
      toast({
        title: "Upgrade Error",
        description: "Failed to upgrade subscription. Please try again.",
        variant: "destructive"
      });
      throw error;
    }
  }

  async getUserCredits(userId: string) {
    try {
      const { data, error } = await supabase
        .from('users')
        .select('credits')
        .eq('id', userId)
        .single();

      if (error) throw error;

      return parseInt(data.credits || '0');
    } catch (error) {
      console.error('Error fetching user credits:', error);
      return 0;
    }
  }

  async deductCredits(userId: string, amount: number = 1, analysisId?: string) {
    try {
      // Get current credits
      const currentCredits = await this.getUserCredits(userId);
      
      if (currentCredits < amount) {
        throw new Error('Insufficient credits');
      }

      const newCredits = currentCredits - amount;

      // Update user credits
      const { error: updateError } = await supabase
        .from('users')
        .update({ credits: newCredits.toString() })
        .eq('id', userId);

      if (updateError) throw updateError;

      // Log credit usage
      const { error: logError } = await supabase
        .from('credit_usage')
        .insert({
          user_id: userId,
          credits_used: amount,
          credits_remaining: newCredits,
          action_type: 'analysis',
          analysis_id: analysisId
        });

      if (logError) throw logError;

      return newCredits;
    } catch (error) {
      console.error('Error deducting credits:', error);
      throw error;
    }
  }

  async getCreditHistory(userId: string) {
    try {
      const { data, error } = await supabase
        .from('credit_usage')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(50);

      if (error) throw error;

      return data;
    } catch (error) {
      console.error('Error fetching credit history:', error);
      return [];
    }
  }

  getTierByPriceId(priceId: string): SubscriptionTier | null {
    return subscriptionTiers.find(tier => tier.stripePriceId === priceId) || null;
  }

  getTierById(tierId: string): SubscriptionTier | null {
    return subscriptionTiers.find(tier => tier.id === tierId) || null;
  }
}

export const subscriptionService = new SubscriptionService();
