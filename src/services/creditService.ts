
import { supabase } from '@/lib/supabase';
import { subscriptionService } from './subscriptionService';

export interface CreditTransaction {
  id: string;
  user_id: string;
  amount: number;
  type: 'debit' | 'credit';
  reason: string;
  analysis_id?: string;
  admin_id?: string;
  created_at: string;
}

export interface UsageStats {
  totalAnalyses: number;
  creditsUsed: number;
  creditsRemaining: number;
  currentPeriodUsage: number;
  subscriptionLimit: number;
  resetDate: string;
}

class CreditService {
  async getUserUsageStats(userId: string): Promise<UsageStats> {
    try {
      // Get user's current subscription and credits
      const [subscription, userCredits] = await Promise.all([
        subscriptionService.getCurrentSubscription(userId),
        subscriptionService.getUserCredits(userId)
      ]);

      // Calculate current period start
      const currentPeriodStart = subscription?.current_period_start 
        ? new Date(subscription.current_period_start)
        : new Date(new Date().getFullYear(), new Date().getMonth(), 1);

      // Get usage for current period
      const { data: periodUsage, error: usageError } = await supabase
        .from('credit_usage')
        .select('credits_used')
        .eq('user_id', userId)
        .gte('created_at', currentPeriodStart.toISOString());

      if (usageError) throw usageError;

      const currentPeriodUsage = periodUsage?.reduce((sum, usage) => sum + usage.credits_used, 0) || 0;

      // Get total analyses count
      const { count: totalAnalyses, error: countError } = await supabase
        .from('analysis_history')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', userId);

      if (countError) throw countError;

      // Determine subscription limits
      const tier = subscription ? subscriptionService.getTierByPriceId(subscription.price_id) : null;
      const subscriptionLimit = tier?.analysisLimit || 2; // Default to free tier

      // Calculate next reset date
      const resetDate = subscription?.current_period_end 
        ? new Date(subscription.current_period_end)
        : new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1);

      return {
        totalAnalyses: totalAnalyses || 0,
        creditsUsed: currentPeriodUsage,
        creditsRemaining: userCredits,
        currentPeriodUsage,
        subscriptionLimit,
        resetDate: resetDate.toISOString()
      };
    } catch (error) {
      console.error('Error getting usage stats:', error);
      throw error;
    }
  }

  async canUserAnalyze(userId: string): Promise<boolean> {
    try {
      const stats = await this.getUserUsageStats(userId);
      
      // Check if user has credits remaining or is under subscription limit
      return stats.creditsRemaining > 0 || stats.currentPeriodUsage < stats.subscriptionLimit;
    } catch (error) {
      console.error('Error checking if user can analyze:', error);
      return false;
    }
  }

  async processAnalysisRequest(userId: string, analysisId: string): Promise<boolean> {
    try {
      const canAnalyze = await this.canUserAnalyze(userId);
      
      if (!canAnalyze) {
        throw new Error('Insufficient credits or subscription limit reached');
      }

      // Deduct credits
      await subscriptionService.deductCredits(userId, 1, analysisId);
      
      return true;
    } catch (error) {
      console.error('Error processing analysis request:', error);
      throw error;
    }
  }

  async addCredits(userId: string, amount: number, reason: string, adminId?: string): Promise<void> {
    try {
      const currentCredits = await subscriptionService.getUserCredits(userId);
      const newCredits = currentCredits + amount;

      // Update user credits
      const { error: updateError } = await supabase
        .from('users')
        .update({ credits: newCredits.toString() })
        .eq('id', userId);

      if (updateError) throw updateError;

      // Log credit addition
      const { error: logError } = await supabase
        .from('credit_usage')
        .insert({
          user_id: userId,
          credits_used: -amount, // Negative for addition
          credits_remaining: newCredits,
          action_type: 'admin_credit',
          admin_id: adminId
        });

      if (logError) throw logError;
    } catch (error) {
      console.error('Error adding credits:', error);
      throw error;
    }
  }

  async getCreditHistory(userId: string): Promise<CreditTransaction[]> {
    try {
      const { data, error } = await supabase
        .from('credit_usage')
        .select(`
          id,
          user_id,
          credits_used,
          credits_remaining,
          action_type,
          analysis_id,
          created_at
        `)
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(100);

      if (error) throw error;

      return data.map(item => ({
        id: item.id,
        user_id: item.user_id,
        amount: Math.abs(item.credits_used),
        type: item.credits_used < 0 ? 'credit' : 'debit',
        reason: item.action_type,
        analysis_id: item.analysis_id,
        created_at: item.created_at
      }));
    } catch (error) {
      console.error('Error fetching credit history:', error);
      return [];
    }
  }

  async resetMonthlyCredits(): Promise<void> {
    try {
      // This would typically be called by a scheduled function
      // Reset credits for all active subscribers based on their tier
      const { data: activeSubscriptions, error } = await supabase
        .from('subscriptions')
        .select('user_id, price_id')
        .eq('status', 'active');

      if (error) throw error;

      for (const subscription of activeSubscriptions) {
        const tier = subscriptionService.getTierByPriceId(subscription.price_id);
        if (tier) {
          await supabase
            .from('users')
            .update({ credits: tier.analysisLimit.toString() })
            .eq('id', subscription.user_id);
        }
      }
    } catch (error) {
      console.error('Error resetting monthly credits:', error);
      throw error;
    }
  }
}

export const creditService = new CreditService();
