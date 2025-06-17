import { supabase } from '@/lib/supabase';
import { creditService } from './creditService';
import { toast } from '@/components/ui/use-toast';
import { imageService, UploadedImage } from './imageService';

export interface AnalysisRequest {
  imageFile: File;
  condition: string;
  estimatedCost?: number;
  notes?: string;
}

export interface AnalysisResult {
  id: string;
  userId: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  productName?: string;
  brand?: string;
  category?: string;
  condition: string;
  estimatedValue?: {
    low: number;
    median: number;
    high: number;
  };
  marketplaceRecommendations?: Array<{
    platform: string;
    suitability: number;
    reasoning: string;
    estimatedProfit: number;
    fees: number;
  }>;
  confidenceScore?: number;
  generatedTitle?: string;
  description?: string;
  tags?: string[];
  imageUrl?: string;
  imageUrls?: string[];
  error?: string;
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

export interface UserStats {
  totalAnalyses: number;
  analysesThisMonth: number;
  analysesUsed: number;
  analysesLimit: number;
  subscriptionTier: string;
  averageProfit?: number;
}

class AnalysisService {
  /**
   * Submit new analysis request
   */
  async submitAnalysis(request: AnalysisRequest, userId: string): Promise<string> {
    try {
      // Check if user can perform analysis (credits/subscription)
      if (userId) {
        const canAnalyze = await creditService.canUserAnalyze(userId);
        if (!canAnalyze) {
          toast({
            title: "Insufficient Credits",
            description: "You don't have enough credits or have reached your subscription limit. Please upgrade your plan.",
            variant: "destructive"
          });
          throw new Error('Insufficient credits or subscription limit reached');
        }
      }

      // Upload image first
      const uploadedImage = await imageService.uploadImage(
        request.imageFile, 
        userId,
        { folder: 'analysis-uploads' }
      );

      // Create analysis record in database
      const { data, error } = await supabase
        .from('analysis_history')
        .insert({
          user_id: userId,
          status: 'pending',
          condition: request.condition,
          estimated_cost: request.estimatedCost || 0,
          notes: request.notes,
          image_url: uploadedImage.url,
          image_path: uploadedImage.path,
          created_at: new Date().toISOString()
        })
        .select('id')
        .single();

      if (error) {
        throw new Error(`Failed to create analysis: ${error.message}`);
      }

      const analysisId = data.id;

      // Submit to backend API for processing
      await this.triggerBackendAnalysis(analysisId, uploadedImage.url, request);

      return analysisId;

    } catch (error) {
      console.error('Analysis submission error:', error);
      throw error;
    }
  }

  /**
   * Trigger backend AI analysis
   */
  private async triggerBackendAnalysis(
    analysisId: string, 
    imageUrl: string, 
    request: AnalysisRequest
  ): Promise<void> {
    try {
      // Update status to analyzing
      await supabase
        .from('analysis_history')
        .update({ 
          status: 'analyzing',
          updated_at: new Date().toISOString()
        })
        .eq('id', analysisId);

      // Call backend API (replace with your actual backend URL)
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

      const formData = new FormData();
      formData.append('image', request.imageFile);
      formData.append('estimated_cost', request.estimatedCost?.toString() || '0');
      formData.append('condition', request.condition);
      formData.append('analysis_id', analysisId);

      const response = await fetch(`${backendUrl}/api/analysis/analyze`, {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${await this.getAuthToken()}`
        }
      });

      if (!response.ok) {
        throw new Error(`Backend analysis failed: ${response.statusText}`);
      }

      const result = await response.json();

      // Update analysis with results
      await this.updateAnalysisWithResults(analysisId, result);

    } catch (error) {
      console.error('Backend analysis error:', error);

      // Mark analysis as failed
      await supabase
        .from('analysis_history')
        .update({ 
          status: 'failed',
          error: error instanceof Error ? error.message : 'Unknown error',
          updated_at: new Date().toISOString()
        })
        .eq('id', analysisId);

      throw error;
    }
  }

  /**
   * Update analysis with AI results
   */
  private async updateAnalysisWithResults(
    analysisId: string, 
    results: any
  ): Promise<void> {
    try {
      const updateData = {
        status: 'completed',
        product_name: results.productName,
        brand: results.brand,
        category: results.category,
        estimated_value_low: results.pricing?.low,
        estimated_value_median: results.pricing?.median,
        estimated_value_high: results.pricing?.high,
        marketplace_recommendations: results.marketplaceRecommendations,
        confidence_score: results.confidenceScore,
        generated_title: results.generatedTitle,
        description: results.description,
        tags: results.tags,
        completed_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      const { error } = await supabase
        .from('analysis_history')
        .update(updateData)
        .eq('id', analysisId);

      if (error) {
        throw new Error(`Failed to update analysis: ${error.message}`);
      }

           // Deduct credits after successful analysis
           try {
            await creditService.processAnalysisRequest(analysisId);
          } catch (creditError) {
            console.error('Error processing credit deduction:', creditError);
            // Don't fail the analysis if credit deduction fails
          }

    } catch (error) {
      console.error('Update analysis error:', error);
      throw error;
    }
  }

  /**
   * Get analysis by ID
   */
  async getAnalysis(analysisId: string): Promise<AnalysisResult | null> {
    try {
      const { data, error } = await supabase
        .from('analysis_history')
        .select('*')
        .eq('id', analysisId)
        .single();

      if (error) {
        if (error.code === 'PGRST116') return null; // Not found
        throw new Error(`Failed to get analysis: ${error.message}`);
      }

      return this.mapDatabaseToAnalysisResult(data);

    } catch (error) {
      console.error('Get analysis error:', error);
      throw error;
    }
  }

  /**
   * Get user's analysis history
   */
  async getUserAnalyses(
    userId: string, 
    limit: number = 20, 
    offset: number = 0
  ): Promise<AnalysisResult[]> {
    try {
      const { data, error } = await supabase
        .from('analysis_history')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

      if (error) {
        throw new Error(`Failed to get user analyses: ${error.message}`);
      }

      return (data || []).map(this.mapDatabaseToAnalysisResult);

    } catch (error) {
      console.error('Get user analyses error:', error);
      throw error;
    }
  }

  /**
   * Get user statistics
   */
  async getUserStats(userId: string): Promise<UserStats> {
    try {
      // Get user subscription info
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('subscription_tier, analyses_used, analyses_limit')
        .eq('id', userId)
        .single();

      if (userError) {
        throw new Error(`Failed to get user data: ${userError.message}`);
      }

      // Get analysis counts
      const { count: totalCount } = await supabase
        .from('analysis_history')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', userId);

      // Get this month's count
      const startOfMonth = new Date();
      startOfMonth.setDate(1);
      startOfMonth.setHours(0, 0, 0, 0);

      const { count: monthCount } = await supabase
        .from('analysis_history')
        .select('*', { count: 'exact', head: true })
        .eq('user_id', userId)
        .gte('created_at', startOfMonth.toISOString());

      // Calculate average profit
      const { data: profitData } = await supabase
        .from('analysis_history')
        .select('marketplace_recommendations')
        .eq('user_id', userId)
        .eq('status', 'completed')
        .not('marketplace_recommendations', 'is', null);

      let averageProfit = 0;
      if (profitData && profitData.length > 0) {
        const profits = profitData
          .map(item => item.marketplace_recommendations?.[0]?.estimatedProfit || 0)
          .filter(profit => profit > 0);

        if (profits.length > 0) {
          averageProfit = profits.reduce((sum, profit) => sum + profit, 0) / profits.length;
        }
      }

      return {
        totalAnalyses: totalCount || 0,
        analysesThisMonth: monthCount || 0,
        analysesUsed: userData.analyses_used || 0,
        analysesLimit: userData.analyses_limit || 0,
        subscriptionTier: userData.subscription_tier || 'free_trial',
        averageProfit
      };

    } catch (error) {
      console.error('Get user stats error:', error);
      throw error;
    }
  }

  /**
   * Save analysis to favorites
   */
  async saveAnalysisToFavorites(analysisId: string): Promise<void> {
    try {
      const { error } = await supabase
        .from('analysis_history')
        .update({ 
          is_favorite: true,
          updated_at: new Date().toISOString()
        })
        .eq('id', analysisId);

      if (error) {
        throw new Error(`Failed to save to favorites: ${error.message}`);
      }

    } catch (error) {
      console.error('Save to favorites error:', error);
      throw error;
    }
  }

  /**
   * Delete analysis
   */
  async deleteAnalysis(analysisId: string): Promise<void> {
    try {
      // Get analysis data first to clean up images
      const analysis = await this.getAnalysis(analysisId);

      if (analysis?.imageUrl) {
        // Extract path from URL and delete from storage
        const url = new URL(analysis.imageUrl);
        const path = url.pathname.split('/').slice(-3).join('/'); // Extract folder/userId/filename
        await imageService.deleteImage(path);
      }

      // Delete from database
      const { error } = await supabase
        .from('analysis_history')
        .delete()
        .eq('id', analysisId);

      if (error) {
        throw new Error(`Failed to delete analysis: ${error.message}`);
      }

    } catch (error) {
      console.error('Delete analysis error:', error);
      throw error;
    }
  }

  /**
   * Get auth token for backend API calls
   */
  private async getAuthToken(): Promise<string> {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || '';
  }

  /**
   * Map database record to AnalysisResult interface
   */
  private mapDatabaseToAnalysisResult(data: any): AnalysisResult {
    return {
      id: data.id,
      userId: data.user_id,
      status: data.status,
      productName: data.product_name,
      brand: data.brand,
      category: data.category,
      condition: data.condition,
      estimatedValue: data.estimated_value_low ? {
        low: data.estimated_value_low,
        median: data.estimated_value_median,
        high: data.estimated_value_high
      } : undefined,
      marketplaceRecommendations: data.marketplace_recommendations,
      confidenceScore: data.confidence_score,
      generatedTitle: data.generated_title,
      description: data.description,
      tags: data.tags,
      imageUrl: data.image_url,
      error: data.error,
      createdAt: data.created_at,
      updatedAt: data.updated_at,
      completedAt: data.completed_at
    };
  }
}

export const analysisService = new AnalysisService();