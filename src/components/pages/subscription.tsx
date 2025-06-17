
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Check, Crown, Zap, Building, Enterprise } from "lucide-react";
import { supabase } from "@/supabase/supabase";
import { toast } from "@/components/ui/use-toast";

interface SubscriptionTier {
  id: string;
  name: string;
  price: number;
  interval: string;
  features: string[];
  analysisLimit: number;
  icon: any;
  popular?: boolean;
  description: string;
  stripePriceId?: string;
}

interface UserSubscription {
  id: string;
  tier: string;
  status: string;
  current_period_end: string;
  analyses_used: number;
}

const subscriptionTiers: SubscriptionTier[] = [
  {
    id: "free_trial",
    name: "Free Trial",
    price: 0,
    interval: "forever",
    analysisLimit: 2,
    icon: Zap,
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
    icon: Check,
    description: "Great for individuals and small sellers",
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
    icon: Crown,
    popular: true,
    description: "Perfect for growing businesses",
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
    icon: Building,
    description: "Designed for established businesses",
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
    icon: Enterprise,
    description: "For large organizations with custom needs",
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

export default function SubscriptionPage() {
  const [currentSubscription, setCurrentSubscription] = useState<UserSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscriptionData();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) return;

      // Get user subscription
      const { data: subscription, error } = await supabase
        .from('subscriptions')
        .select('*')
        .eq('user_id', user.id)
        .eq('status', 'active')
        .maybeSingle();

      if (error && error.code !== 'PGRST116') {
        throw error;
      }

      // Get usage data
      const { data: userData } = await supabase
        .from('users')
        .select('analyses_used, subscription_tier')
        .eq('id', user.id)
        .single();

      if (subscription) {
        setCurrentSubscription({
          id: subscription.id,
          tier: subscription.tier,
          status: subscription.status,
          current_period_end: subscription.current_period_end,
          analyses_used: userData?.analyses_used || 0
        });
      } else {
        setCurrentSubscription({
          id: 'free',
          tier: userData?.subscription_tier || 'free_trial',
          status: 'active',
          current_period_end: '',
          analyses_used: userData?.analyses_used || 0
        });
      }
    } catch (error) {
      console.error('Error fetching subscription data:', error);
      toast({
        title: "Error",
        description: "Failed to load subscription data.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierId: string) => {
    setUpgrading(tierId);
    
    try {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        toast({
          title: "Authentication Required",
          description: "Please log in to upgrade your subscription.",
          variant: "destructive"
        });
        return;
      }

      // Create checkout session
      const { data, error } = await supabase.functions.invoke('create-checkout', {
        body: {
          priceId: tierId,
          userId: user.id,
          email: user.email
        }
      });

      if (error) throw error;

      if (data?.url) {
        window.location.href = data.url;
      }
    } catch (error) {
      console.error('Error creating checkout session:', error);
      toast({
        title: "Error",
        description: "Failed to start upgrade process. Please try again.",
        variant: "destructive"
      });
    } finally {
      setUpgrading(null);
    }
  };

  const getCurrentTier = () => {
    return subscriptionTiers.find(tier => tier.id === currentSubscription?.tier) || subscriptionTiers[0];
  };

  const calculateUsagePercentage = () => {
    const currentTier = getCurrentTier();
    const used = currentSubscription?.analyses_used || 0;
    return Math.min((used / currentTier.analysisLimit) * 100, 100);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  const currentTier = getCurrentTier();
  const usagePercentage = calculateUsagePercentage();

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Subscription Plans</h1>
        <p className="text-muted-foreground">
          Choose the perfect plan for your business needs
        </p>
      </div>

      {/* Current Plan Status */}
      {currentSubscription && (
        <Card className="mb-8 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <currentTier.icon className="h-5 w-5" />
              Current Plan: {currentTier.name}
            </CardTitle>
            <CardDescription>
              {currentSubscription.tier !== 'free_trial' && currentSubscription.current_period_end && (
                <>Next billing: {new Date(currentSubscription.current_period_end).toLocaleDateString()}</>
              )}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Analyses Used</span>
                  <span>{currentSubscription.analyses_used} / {currentTier.analysisLimit}</span>
                </div>
                <Progress value={usagePercentage} className="h-2" />
              </div>
              {usagePercentage > 80 && (
                <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
                  You're approaching your analysis limit. Consider upgrading to continue using our services.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Subscription Tiers */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
        {subscriptionTiers.map((tier) => {
          const Icon = tier.icon;
          const isCurrentTier = currentSubscription?.tier === tier.id;
          const isDowngrade = currentSubscription && 
            subscriptionTiers.findIndex(t => t.id === currentSubscription.tier) > 
            subscriptionTiers.findIndex(t => t.id === tier.id);

          return (
            <Card 
              key={tier.id} 
              className={`relative transition-all duration-300 hover:shadow-lg ${
                tier.popular ? 'border-blue-500 shadow-lg scale-105' : ''
              } ${isCurrentTier ? 'border-green-500 bg-green-50' : ''}`}
            >
              {tier.popular && (
                <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-blue-500">
                  Most Popular
                </Badge>
              )}
              {isCurrentTier && (
                <Badge className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-green-500">
                  Current Plan
                </Badge>
              )}
              
              <CardHeader className="text-center">
                <div className="flex justify-center mb-2">
                  <Icon className={`h-8 w-8 ${tier.popular ? 'text-blue-500' : 'text-gray-600'}`} />
                </div>
                <CardTitle className="text-xl">{tier.name}</CardTitle>
                <CardDescription className="text-sm">{tier.description}</CardDescription>
                <div className="mt-4">
                  <span className="text-3xl font-bold">${tier.price}</span>
                  <span className="text-muted-foreground">/{tier.interval}</span>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <ul className="space-y-2 text-sm">
                  {tier.features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-2">
                      <Check className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Button 
                  className="w-full mt-4"
                  variant={isCurrentTier ? "secondary" : tier.popular ? "default" : "outline"}
                  disabled={isCurrentTier || upgrading !== null}
                  onClick={() => !isCurrentTier && handleUpgrade(tier.id)}
                >
                  {upgrading === tier.id ? (
                    "Processing..."
                  ) : isCurrentTier ? (
                    "Current Plan"
                  ) : isDowngrade ? (
                    "Downgrade"
                  ) : tier.id === 'free_trial' ? (
                    "Current Plan"
                  ) : (
                    "Upgrade Now"
                  )}
                </Button>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* FAQ or Additional Info */}
      <div className="mt-12 text-center">
        <p className="text-muted-foreground mb-4">
          Need a custom plan? Contact our sales team for enterprise solutions.
        </p>
        <Button variant="outline">
          Contact Sales
        </Button>
      </div>
    </div>
  );
}
