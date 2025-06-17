
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Calendar, CreditCard, AlertCircle, CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { subscriptionService, UserSubscription, subscriptionTiers } from '@/services/subscriptionService';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/components/ui/use-toast';

export function SubscriptionManager() {
  const { user } = useAuth();
  const [subscription, setSubscription] = useState<UserSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    if (user) {
      loadSubscription();
    }
  }, [user]);

  const loadSubscription = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const sub = await subscriptionService.getCurrentSubscription(user.id);
      setSubscription(sub);
    } catch (error) {
      console.error('Error loading subscription:', error);
      toast({
        title: "Error",
        description: "Failed to load subscription details.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!subscription) return;

    try {
      setActionLoading(true);
      await subscriptionService.cancelSubscription(subscription.stripe_subscription_id);
      await loadSubscription(); // Reload to get updated status
    } catch (error) {
      console.error('Error cancelling subscription:', error);
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'default';
      case 'canceled':
        return 'destructive';
      case 'past_due':
        return 'destructive';
      case 'unpaid':
        return 'destructive';
      default:
        return 'secondary';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4" />;
      case 'canceled':
        return <XCircle className="h-4 w-4" />;
      case 'past_due':
      case 'unpaid':
        return <AlertCircle className="h-4 w-4" />;
      default:
        return <AlertCircle className="h-4 w-4" />;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Loading subscription details...</span>
        </CardContent>
      </Card>
    );
  }

  if (!subscription) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>No Active Subscription</CardTitle>
          <CardDescription>
            You don't have an active subscription. Choose a plan to get started.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={() => window.location.href = '/subscription'}>
            View Plans
          </Button>
        </CardContent>
      </Card>
    );
  }

  const tier = subscriptionService.getTierByPriceId(subscription.price_id);

  return (
    <div className="space-y-6">
      {/* Subscription Status */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                Current Subscription
                <Badge variant={getStatusColor(subscription.status)} className="flex items-center gap-1">
                  {getStatusIcon(subscription.status)}
                  {subscription.status.charAt(0).toUpperCase() + subscription.status.slice(1)}
                </Badge>
              </CardTitle>
              <CardDescription>
                Manage your subscription and billing details
              </CardDescription>
            </div>
            <CreditCard className="h-5 w-5 text-muted-foreground" />
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Plan Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium mb-2">Plan Details</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Plan:</span>
                  <span className="font-medium">{tier?.name || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Price:</span>
                  <span className="font-medium">${tier?.price || 0}/{tier?.interval || 'month'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Analysis Limit:</span>
                  <span className="font-medium">{tier?.analysisLimit || 0} per month</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Billing Information</h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Period:</span>
                  <span className="font-medium">
                    {formatDate(subscription.current_period_start)} - {formatDate(subscription.current_period_end)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Next Billing:</span>
                  <span className="font-medium">
                    {subscription.cancel_at_period_end 
                      ? 'Cancelled' 
                      : formatDate(subscription.current_period_end)
                    }
                  </span>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          {/* Plan Features */}
          <div>
            <h4 className="font-medium mb-2">Plan Features</h4>
            <ul className="grid grid-cols-1 md:grid-cols-2 gap-1 text-sm">
              {tier?.features.map((feature, index) => (
                <li key={index} className="flex items-center gap-2">
                  <CheckCircle className="h-3 w-3 text-primary" />
                  <span>{feature}</span>
                </li>
              ))}
            </ul>
          </div>

          <Separator />

          {/* Actions */}
          <div className="flex gap-2 flex-wrap">
            <Button 
              variant="outline" 
              onClick={() => window.location.href = '/subscription'}
            >
              Change Plan
            </Button>
            
            {!subscription.cancel_at_period_end && (
              <Button
                variant="destructive"
                onClick={handleCancelSubscription}
                disabled={actionLoading}
              >
                {actionLoading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Cancel Subscription
              </Button>
            )}
          </div>

          {/* Cancellation Notice */}
          {subscription.cancel_at_period_end && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Your subscription is scheduled for cancellation on {formatDate(subscription.current_period_end)}. 
                You'll continue to have access until then.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
