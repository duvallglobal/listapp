import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Check, Crown, Zap, Building, Enterprise, AlertCircle, Loader2 } from "lucide-react";
import { supabase, handleSupabaseError } from "@/lib/supabase";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "@/components/ui/use-toast";

interface SubscriptionPageState {
  currentSubscription: UserSubscription | null;
  loading: boolean;
  error: string | null;
}

export function Subscription() {
  const { user } = useAuth();
  const [state, setState] = useState<SubscriptionPageState>({
    currentSubscription: null,
    loading: true,
    error: null
  });

  useEffect(() => {
    if (user) {
      loadSubscriptionData();
    }
  }, [user]);

  const loadSubscriptionData = async () => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      const subscription = await subscriptionService.getCurrentSubscription(user!.id);

      setState(prev => ({
        ...prev,
        currentSubscription: subscription,
        loading: false
      }));
    } catch (error) {
      console.error('Error loading subscription:', error);
      setState(prev => ({
        ...prev,
        error: 'Failed to load subscription data',
        loading: false
      }));
    }
  };

  const handleSubscriptionUpdate = () => {
    loadSubscriptionData();
  };

  if (state.loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center gap-2">
          <Loader2 className="h-4 w-4 animate-spin" />
          <span>Loading subscription details...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold">Subscription Management</h1>
        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Manage your subscription, view usage, and upgrade your plan.
        </p>
      </div>

      {/* Error Alert */}
      {state.error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{state.error}</AlertDescription>
        </Alert>
      )}

      {/* Subscription Management Tabs */}
      <Tabs defaultValue="plans" className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="plans">Plans & Pricing</TabsTrigger>
          <TabsTrigger value="manage">Manage Subscription</TabsTrigger>
          <TabsTrigger value="usage">Usage & Credits</TabsTrigger>
        </TabsList>

        <TabsContent value="plans" className="space-y-6">
          <PricingPlans 
            currentSubscription={state.currentSubscription}
            onUpgrade={handleSubscriptionUpdate}
          />
        </TabsContent>

        <TabsContent value="manage" className="space-y-6">
          <SubscriptionManager />
        </TabsContent>

        <TabsContent value="usage" className="space-y-6">
          <CreditUsage />
        </TabsContent>
      </Tabs>
    </div>
  );
}