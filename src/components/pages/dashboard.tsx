
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  Search, 
  TrendingUp, 
  DollarSign, 
  BarChart3,
  Plus,
  Eye,
  Calendar,
  AlertCircle,
  RefreshCw,
  Wifi,
  WifiOff
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { supabase, handleSupabaseError } from "@/lib/supabase";
import { useAuth } from "@/contexts/AuthContext";

interface DashboardStats {
  totalAnalyses: number;
  analysesThisMonth: number;
  averageProfit: number;
  subscriptionTier: string;
  analysesUsed: number;
  analysesLimit: number;
}

interface RecentAnalysis {
  id: string;
  product_name: string;
  condition: string;
  created_at: string;
  status: string;
  image_url?: string;
  analysis_result?: any;
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const { connectionStatus, retryConnection } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentAnalyses, setRecentAnalyses] = useState<RecentAnalysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  useEffect(() => {
    if (connectionStatus === 'connected') {
      fetchDashboardData();
    } else if (connectionStatus === 'disconnected') {
      setLoading(false);
      setError('No database connection available');
    }
  }, [connectionStatus]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        setError('No authenticated user found');
        return;
      }

      // Fetch user stats with error handling
      const { data: userData, error: userError } = await supabase
        .from('users')
        .select('subscription_tier, analyses_used')
        .eq('id', user.id)
        .maybeSingle();

      if (userError && userError.code !== 'PGRST116') {
        throw userError;
      }

      // Fetch analysis history with error handling
      const { data: analyses, count: totalCount, error: analysisError } = await supabase
        .from('analysis_history')
        .select('*', { count: 'exact' })
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(5);

      if (analysisError) {
        console.error('Analysis fetch error:', analysisError);
        // Don't throw, just log and continue with empty data
      }

      // Fetch this month's analyses
      const startOfMonth = new Date();
      startOfMonth.setDate(1);
      startOfMonth.setHours(0, 0, 0, 0);

      const { count: monthlyCount, error: monthlyError } = await supabase
        .from('analysis_history')
        .select('*', { count: 'exact' })
        .eq('user_id', user.id)
        .gte('created_at', startOfMonth.toISOString());

      if (monthlyError) {
        console.error('Monthly count error:', monthlyError);
      }

      // Calculate average profit safely
      const averageProfit = analyses?.length ? 
        analyses.reduce((acc, analysis) => {
          const result = analysis.analysis_result;
          const profit = result?.estimated_profit || result?.profit || 0;
          return acc + (typeof profit === 'number' ? profit : 0);
        }, 0) / analyses.length : 0;

      // Get subscription limits
      const tierLimits = {
        free_trial: 2,
        basic: 50,
        pro: 200,
        business: 1000,
        enterprise: 5000
      };

      const subscriptionTier = userData?.subscription_tier || 'free_trial';

      setStats({
        totalAnalyses: totalCount || 0,
        analysesThisMonth: monthlyCount || 0,
        averageProfit,
        subscriptionTier,
        analysesUsed: userData?.analyses_used || 0,
        analysesLimit: tierLimits[subscriptionTier as keyof typeof tierLimits] || 2
      });

      setRecentAnalyses(analyses || []);
    } catch (error: any) {
      console.error('Error fetching dashboard data:', error);
      setError(handleSupabaseError(error));
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async () => {
    setRetrying(true);
    try {
      await retryConnection();
      if (connectionStatus === 'connected') {
        await fetchDashboardData();
      }
    } finally {
      setRetrying(false);
    }
  };

  const quickActions = [
    {
      title: "New Analysis",
      description: "Analyze a product with AI",
      icon: Search,
      action: () => navigate("/analysis"),
      color: "bg-blue-500",
      disabled: connectionStatus !== 'connected'
    },
    {
      title: "View History",
      description: "See past analyses",
      icon: BarChart3,
      action: () => navigate("/history"),
      color: "bg-green-500",
      disabled: connectionStatus !== 'connected'
    },
    {
      title: "Upgrade Plan",
      description: "Unlock more features",
      icon: TrendingUp,
      action: () => navigate("/subscription"),
      color: "bg-purple-500",
      disabled: connectionStatus !== 'connected'
    }
  ];

  // Connection Status Component
  const ConnectionStatus = () => (
    <Alert className={connectionStatus === 'connected' ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
      <div className="flex items-center space-x-2">
        {connectionStatus === 'connected' ? (
          <Wifi className="h-4 w-4 text-green-600" />
        ) : (
          <WifiOff className="h-4 w-4 text-red-600" />
        )}
        <AlertDescription className={connectionStatus === 'connected' ? 'text-green-700' : 'text-red-700'}>
          {connectionStatus === 'connected' && 'Connected to database'}
          {connectionStatus === 'disconnected' && 'Database connection lost'}
          {connectionStatus === 'checking' && 'Checking connection...'}
        </AlertDescription>
        {connectionStatus !== 'connected' && (
          <Button
            size="sm"
            variant="outline"
            onClick={handleRetry}
            disabled={retrying}
            className="ml-auto"
          >
            {retrying ? <RefreshCw className="h-3 w-3 animate-spin" /> : 'Retry'}
          </Button>
        )}
      </div>
    </Alert>
  );

  if (loading && connectionStatus === 'checking') {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const usagePercentage = stats ? (stats.analysesUsed / stats.analysesLimit) * 100 : 0;

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's an overview of your price intelligence activities.
        </p>
      </div>

      {/* Connection Status */}
      <div className="mb-6">
        <ConnectionStatus />
      </div>

      {/* Error State */}
      {error && (
        <Alert className="mb-6 border-red-200 bg-red-50">
          <AlertCircle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-700">
            {error}
            <Button
              size="sm"
              variant="outline"
              onClick={handleRetry}
              disabled={retrying}
              className="ml-2"
            >
              {retrying ? <RefreshCw className="h-3 w-3 animate-spin" /> : 'Retry'}
            </Button>
          </AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card className="bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
            <BarChart3 className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-700">{stats?.totalAnalyses || 0}</div>
            <p className="text-xs text-blue-600">All time</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-green-50 to-green-100 border-green-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">This Month</CardTitle>
            <Calendar className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-700">{stats?.analysesThisMonth || 0}</div>
            <p className="text-xs text-green-600">Analyses completed</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-purple-50 to-purple-100 border-purple-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Avg. Profit</CardTitle>
            <DollarSign className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-700">
              ${stats?.averageProfit?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-purple-600">Per analysis</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-orange-50 to-orange-100 border-orange-200">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Plan</CardTitle>
            <TrendingUp className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-lg font-bold text-orange-700 capitalize">
              {stats?.subscriptionTier?.replace('_', ' ') || 'Free Trial'}
            </div>
            <p className="text-xs text-orange-600">Current subscription</p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Progress */}
      {stats && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Monthly Usage</CardTitle>
            <CardDescription>
              Track your analysis usage for the current billing period
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between text-sm">
                <span>Analyses Used</span>
                <span>{stats.analysesUsed} / {stats.analysesLimit}</span>
              </div>
              <Progress value={usagePercentage} className="h-3" />
              {usagePercentage > 80 && (
                <div className="text-sm text-amber-600 bg-amber-50 p-3 rounded-lg">
                  You're approaching your analysis limit. 
                  <Button 
                    variant="link" 
                    className="p-0 ml-1 h-auto"
                    onClick={() => navigate("/subscription")}
                    disabled={connectionStatus !== 'connected'}
                  >
                    Upgrade your plan
                  </Button> to continue analyzing products.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Quick Actions */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Get started with your most common tasks
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              return (
                <Card 
                  key={index} 
                  className={`cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105 ${
                    action.disabled ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                  onClick={() => !action.disabled && action.action()}
                >
                  <CardContent className="p-6 text-center">
                    <div className={`inline-flex p-3 rounded-full ${action.color} mb-4`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="font-semibold mb-2">{action.title}</h3>
                    <p className="text-sm text-muted-foreground">{action.description}</p>
                    {action.disabled && (
                      <Badge variant="secondary" className="mt-2">
                        Requires Connection
                      </Badge>
                    )}
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Recent Analyses */}
      {connectionStatus === 'connected' && recentAnalyses.length > 0 && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Analyses</CardTitle>
              <CardDescription>Your latest product analyses</CardDescription>
            </div>
            <Button variant="outline" onClick={() => navigate("/history")}>
              <Eye className="h-4 w-4 mr-2" />
              View All
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAnalyses.map((analysis) => (
                <div key={analysis.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                  {analysis.image_url && (
                    <img 
                      src={analysis.image_url} 
                      alt={analysis.product_name}
                      className="h-16 w-16 object-cover rounded-lg"
                      onError={(e) => {
                        const target = e.target as HTMLImageElement;
                        target.style.display = 'none';
                      }}
                    />
                  )}
                  <div className="flex-1">
                    <h4 className="font-semibold">{analysis.product_name}</h4>
                    <p className="text-sm text-muted-foreground">
                      Condition: {analysis.condition}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(analysis.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Badge variant={analysis.status === 'completed' ? 'default' : 'secondary'}>
                    {analysis.status}
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Empty State */}
      {connectionStatus === 'connected' && recentAnalyses.length === 0 && !loading && (
        <Card>
          <CardContent className="text-center py-12">
            <Search className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No analyses yet</h3>
            <p className="text-muted-foreground mb-4">
              Start by analyzing your first product to see insights here.
            </p>
            <Button onClick={() => navigate("/analysis")} disabled={connectionStatus !== 'connected'}>
              <Plus className="h-4 w-4 mr-2" />
              Start First Analysis
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Offline State */}
      {connectionStatus === 'disconnected' && (
        <Card>
          <CardContent className="text-center py-12">
            <WifiOff className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Offline Mode</h3>
            <p className="text-muted-foreground mb-4">
              Some features are unavailable while offline. Check your connection and try again.
            </p>
            <Button onClick={handleRetry} disabled={retrying}>
              {retrying ? <RefreshCw className="h-4 w-4 mr-2 animate-spin" /> : <RefreshCw className="h-4 w-4 mr-2" />}
              Retry Connection
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
