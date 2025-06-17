
import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Check, Crown, Zap, Building, Enterprise, Loader2 } from 'lucide-react';
import { subscriptionTiers, subscriptionService, UserSubscription } from '@/services/subscriptionService';
import { useAuth } from '@/contexts/AuthContext';

interface PricingPlansProps {
  currentSubscription?: UserSubscription | null;
  onUpgrade?: () => void;
}

export function PricingPlans({ currentSubscription, onUpgrade }: PricingPlansProps) {
  const { user } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);

  const getIcon = (iconName: string) => {
    const icons = {
      Zap,
      Check,
      Crown,
      Building,
      Enterprise
    };
    return icons[iconName as keyof typeof icons] || Check;
  };

  const handleSelectPlan = async (tier: typeof subscriptionTiers[0]) => {
    if (!user || !tier.stripePriceId) return;
    
    setLoading(tier.id);
    
    try {
      if (currentSubscription && tier.stripePriceId !== currentSubscription.price_id) {
        // Upgrade/downgrade existing subscription
        await subscriptionService.upgradeSubscription(tier.stripePriceId, currentSubscription.stripe_subscription_id);
      } else if (!currentSubscription) {
        // Create new subscription
        await subscriptionService.createCheckoutSession(tier.stripePriceId, user.id);
      }
      
      onUpgrade?.();
    } catch (error) {
      console.error('Error selecting plan:', error);
    } finally {
      setLoading(null);
    }
  };

  const isCurrentTier = (tier: typeof subscriptionTiers[0]) => {
    return currentSubscription?.price_id === tier.stripePriceId;
  };

  const isDowngrade = (tier: typeof subscriptionTiers[0]) => {
    if (!currentSubscription) return false;
    const currentTierIndex = subscriptionTiers.findIndex(t => t.stripePriceId === currentSubscription.price_id);
    const newTierIndex = subscriptionTiers.findIndex(t => t.id === tier.id);
    return currentTierIndex > newTierIndex;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
      {subscriptionTiers.map((tier) => {
        const Icon = getIcon(tier.id === 'free_trial' ? 'Zap' : 
                           tier.id === 'basic' ? 'Check' :
                           tier.id === 'pro' ? 'Crown' :
                           tier.id === 'business' ? 'Building' : 'Enterprise');
        
        const isCurrent = isCurrentTier(tier);
        const isDowngradeOption = isDowngrade(tier);
        const isLoadingThis = loading === tier.id;

        return (
          <Card 
            key={tier.id} 
            className={`relative ${tier.popular ? 'border-primary shadow-lg' : ''} ${isCurrent ? 'bg-muted' : ''}`}
          >
            {tier.popular && (
              <Badge 
                className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-primary text-primary-foreground"
              >
                Most Popular
              </Badge>
            )}
            
            <CardHeader className="text-center pb-4">
              <div className="flex justify-center mb-4">
                <div className="p-3 rounded-full bg-primary/10">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
              </div>
              
              <CardTitle className="text-xl">{tier.name}</CardTitle>
              <CardDescription className="text-sm">{tier.description}</CardDescription>
              
              <div className="mt-4">
                <div className="text-3xl font-bold">
                  ${tier.price}
                  {tier.price > 0 && (
                    <span className="text-sm font-normal text-muted-foreground">
                      /{tier.interval}
                    </span>
                  )}
                </div>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              <ul className="space-y-2 text-sm">
                {tier.features.map((feature, index) => (
                  <li key={index} className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary flex-shrink-0" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                className="w-full"
                variant={isCurrent ? "outline" : tier.popular ? "default" : "outline"}
                disabled={isCurrent || isLoadingThis || !tier.stripePriceId}
                onClick={() => handleSelectPlan(tier)}
              >
                {isLoadingThis && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                {isCurrent 
                  ? "Current Plan" 
                  : isDowngradeOption
                  ? "Downgrade"
                  : tier.stripePriceId
                  ? "Select Plan"
                  : "Get Started"
                }
              </Button>

              {tier.id === 'free_trial' && (
                <p className="text-xs text-center text-muted-foreground">
                  No credit card required
                </p>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
