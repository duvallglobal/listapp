
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Calendar, CreditCard, TrendingUp, RefreshCw, Plus, Minus, Loader2 } from 'lucide-react';
import { creditService, UsageStats, CreditTransaction } from '@/services/creditService';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/components/ui/use-toast';

export function CreditUsage() {
  const { user } = useAuth();
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null);
  const [creditHistory, setCreditHistory] = useState<CreditTransaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      loadUsageData();
    }
  }, [user]);

  const loadUsageData = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const [stats, history] = await Promise.all([
        creditService.getUserUsageStats(user.id),
        creditService.getCreditHistory(user.id)
      ]);
      
      setUsageStats(stats);
      setCreditHistory(history);
    } catch (error) {
      console.error('Error loading usage data:', error);
      toast({
        title: "Error",
        description: "Failed to load usage statistics.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const getUsagePercentage = () => {
    if (!usageStats) return 0;
    return Math.min(100, (usageStats.currentPeriodUsage / usageStats.subscriptionLimit) * 100);
  };

  const getUsageColor = () => {
    const percentage = getUsagePercentage();
    if (percentage >= 90) return 'destructive';
    if (percentage >= 75) return 'warning';
    return 'default';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionIcon = (type: string) => {
    return type === 'credit' ? <Plus className="h-3 w-3 text-green-500" /> : <Minus className="h-3 w-3 text-red-500" />;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="h-6 w-6 animate-spin mr-2" />
          <span>Loading usage statistics...</span>
        </CardContent>
      </Card>
    );
  }

  if (!usageStats) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Usage Statistics</CardTitle>
          <CardDescription>Unable to load usage data</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Usage Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                Credit Usage
                <Badge variant={getUsageColor()}>
                  {usageStats.currentPeriodUsage}/{usageStats.subscriptionLimit}
                </Badge>
              </CardTitle>
              <CardDescription>
                Current billing period usage and remaining credits
              </CardDescription>
            </div>
            <Button variant="outline" size="sm" onClick={loadUsageData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span>Analyses Used</span>
              <span>{usageStats.currentPeriodUsage} of {usageStats.subscriptionLimit}</span>
            </div>
            <Progress 
              value={getUsagePercentage()} 
              className="h-2"
            />
            {getUsagePercentage() >= 90 && (
              <p className="text-sm text-destructive mt-2">
                You're approaching your monthly limit. Consider upgrading your plan.
              </p>
            )}
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold text-primary">{usageStats.creditsRemaining}</div>
              <div className="text-sm text-muted-foreground">Credits Remaining</div>
            </div>
            
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{usageStats.totalAnalyses}</div>
              <div className="text-sm text-muted-foreground">Total Analyses</div>
            </div>
            
            <div className="text-center p-4 bg-muted rounded-lg">
              <div className="text-2xl font-bold">{Math.max(0, usageStats.subscriptionLimit - usageStats.currentPeriodUsage)}</div>
              <div className="text-sm text-muted-foreground">Remaining This Period</div>
            </div>
          </div>

          {/* Reset Information */}
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Calendar className="h-4 w-4" />
            <span>
              Usage resets on {new Date(usageStats.resetDate).toLocaleDateString('en-US', {
                month: 'long',
                day: 'numeric',
                year: 'numeric'
              })}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Credit History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>
            Your recent credit transactions and analysis history
          </CardDescription>
        </CardHeader>

        <CardContent>
          {creditHistory.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CreditCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No activity yet</p>
            </div>
          ) : (
            <div className="space-y-3">
              {creditHistory.slice(0, 10).map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    {getTransactionIcon(transaction.type)}
                    <div>
                      <div className="font-medium text-sm">
                        {transaction.type === 'credit' ? 'Credits Added' : 'Analysis Performed'}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatDate(transaction.created_at)}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className={`font-medium text-sm ${
                      transaction.type === 'credit' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {transaction.type === 'credit' ? '+' : '-'}{transaction.amount}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {transaction.reason}
                    </div>
                  </div>
                </div>
              ))}
              
              {creditHistory.length > 10 && (
                <div className="text-center pt-4">
                  <Button variant="outline" size="sm">
                    View Full History
                  </Button>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
