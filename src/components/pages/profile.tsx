
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { supabase } from '../../lib/supabase';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../ui/card';
import {
  Alert,
  AlertDescription,
} from '../ui/alert';
import {
  Button
} from '../ui/button';
import {
  Input
} from '../ui/input';
import {
  Label
} from '../ui/label';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '../ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import {
  Badge
} from '../ui/badge';
import {
  Progress
} from '../ui/progress';
import {
  Separator
} from '../ui/separator';
import {
  User,
  Mail,
  Calendar,
  CreditCard,
  AlertTriangle,
  Shield,
  BarChart3,
  Download,
  Trash2,
  Save,
  RefreshCw,
  Eye,
  EyeOff
} from 'lucide-react';

interface UserProfile {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
  credits: number;
  subscription: string;
  stripe_customer_id?: string;
  last_login?: string;
}

interface AnalysisStats {
  totalAnalyses: number;
  thisMonth: number;
  totalSpent: number;
  averageProfit: number;
  topPlatform: string;
}

const Profile: React.FC = () => {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [analysisStats, setAnalysisStats] = useState<AnalysisStats>({
    totalAnalyses: 0,
    thisMonth: 0,
    totalSpent: 0,
    averageProfit: 0,
    topPlatform: 'N/A'
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [editedProfile, setEditedProfile] = useState<Partial<UserProfile>>({});
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    if (user) {
      fetchProfile();
      fetchAnalysisStats();
    }
  }, [user]);

  const fetchProfile = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from('users')
        .select('*')
        .eq('id', user.id)
        .single();

      if (error) throw error;

      setProfile(data);
      setEditedProfile(data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      setError('Failed to load profile data');
    }
  };

  const fetchAnalysisStats = async () => {
    if (!user) return;

    try {
      const { data: analyses, error } = await supabase
        .from('analysis_history')
        .select('*')
        .eq('user_id', user.id);

      if (error) throw error;

      const thisMonth = new Date();
      thisMonth.setDate(1);
      thisMonth.setHours(0, 0, 0, 0);

      const thisMonthAnalyses = analyses?.filter(
        analysis => new Date(analysis.created_at) >= thisMonth
      ) || [];

      const platformCounts: Record<string, number> = {};
      let totalProfit = 0;

      analyses?.forEach(analysis => {
        const platform = analysis.recommended_platform || 'Unknown';
        platformCounts[platform] = (platformCounts[platform] || 0) + 1;
        totalProfit += analysis.recommended_price || 0;
      });

      const topPlatform = Object.keys(platformCounts).reduce((a, b) =>
        platformCounts[a] > platformCounts[b] ? a : b, 'N/A'
      );

      setAnalysisStats({
        totalAnalyses: analyses?.length || 0,
        thisMonth: thisMonthAnalyses.length,
        totalSpent: (analyses?.length || 0) * 1, // Assuming $1 per analysis
        averageProfit: analyses?.length ? totalProfit / analyses.length : 0,
        topPlatform
      });
    } catch (error) {
      console.error('Error fetching analysis stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async () => {
    if (!user || !profile) return;

    setSaving(true);
    setError(null);
    setSuccess(null);

    try {
      const { error } = await supabase
        .from('users')
        .update({
          full_name: editedProfile.full_name,
          email: editedProfile.email,
        })
        .eq('id', user.id);

      if (error) throw error;

      setProfile({ ...profile, ...editedProfile });
      setSuccess('Profile updated successfully');
    } catch (error) {
      console.error('Error updating profile:', error);
      setError('Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!user || deleteConfirmation !== 'DELETE') return;

    setSaving(true);
    setError(null);

    try {
      // Delete user data
      await supabase.from('analysis_history').delete().eq('user_id', user.id);
      await supabase.from('users').delete().eq('id', user.id);

      // Sign out and redirect
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error deleting account:', error);
      setError('Failed to delete account');
    } finally {
      setSaving(false);
      setShowDeleteDialog(false);
    }
  };

  const exportData = async () => {
    if (!user) return;

    try {
      const { data: analyses } = await supabase
        .from('analysis_history')
        .select('*')
        .eq('user_id', user.id);

      const csvContent = [
        'Date,Product Name,Recommended Price,Platform,Status',
        ...(analyses || []).map(analysis =>
          `${analysis.created_at},${analysis.product_name},${analysis.recommended_price},${analysis.recommended_platform},${analysis.status}`
        )
      ].join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `price-intelligence-data-${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting data:', error);
      setError('Failed to export data');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span>Loading profile...</span>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>Failed to load profile data</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Profile Settings</h1>
            <p className="text-muted-foreground">
              Manage your account settings and preferences
            </p>
          </div>
          <Button onClick={() => navigate('/dashboard')} variant="outline">
            Back to Dashboard
          </Button>
        </div>

        {/* Alerts */}
        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert>
            <Shield className="h-4 w-4" />
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="general">General</TabsTrigger>
            <TabsTrigger value="subscription">Subscription</TabsTrigger>
            <TabsTrigger value="usage">Usage Stats</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
          </TabsList>

          {/* General Tab */}
          <TabsContent value="general" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <User className="h-5 w-5" />
                  Profile Information
                </CardTitle>
                <CardDescription>
                  Update your personal information and preferences
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name</Label>
                    <Input
                      id="full_name"
                      value={editedProfile.full_name || ''}
                      onChange={(e) => setEditedProfile({
                        ...editedProfile,
                        full_name: e.target.value
                      })}
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      type="email"
                      value={editedProfile.email || ''}
                      onChange={(e) => setEditedProfile({
                        ...editedProfile,
                        email: e.target.value
                      })}
                      placeholder="Enter your email"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label>Account Created</Label>
                  <div className="flex items-center gap-2 text-sm text-muted-foreground">
                    <Calendar className="h-4 w-4" />
                    {new Date(profile.created_at).toLocaleDateString()}
                  </div>
                </div>

                <Separator />

                <div className="flex justify-between items-center">
                  <Button
                    onClick={handleSaveProfile}
                    disabled={saving}
                    className="gap-2"
                  >
                    {saving ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Save className="h-4 w-4" />
                    )}
                    Save Changes
                  </Button>

                  <Button
                    onClick={exportData}
                    variant="outline"
                    className="gap-2"
                  >
                    <Download className="h-4 w-4" />
                    Export Data
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Subscription Tab */}
          <TabsContent value="subscription" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CreditCard className="h-5 w-5" />
                  Subscription Details
                </CardTitle>
                <CardDescription>
                  Manage your subscription and billing information
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Current Plan</p>
                    <p className="text-sm text-muted-foreground">
                      {profile.subscription} subscription
                    </p>
                  </div>
                  <Badge variant="outline">{profile.subscription}</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Remaining Credits</p>
                    <p className="text-sm text-muted-foreground">
                      Credits available for analyses
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-lg">{profile.credits}</p>
                  </div>
                </div>

                <Separator />

                <div className="flex gap-2">
                  <Button onClick={() => navigate('/subscription')}>
                    Manage Subscription
                  </Button>
                  <Button variant="outline" onClick={() => navigate('/subscription')}>
                    Upgrade Plan
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Usage Stats Tab */}
          <TabsContent value="usage" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Total Analyses</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analysisStats.totalAnalyses}</div>
                  <p className="text-sm text-muted-foreground">
                    +{analysisStats.thisMonth} this month
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Average Profit</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(analysisStats.averageProfit)}
                  </div>
                  <p className="text-sm text-muted-foreground">Per analysis</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Total Spent</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {formatCurrency(analysisStats.totalSpent)}
                  </div>
                  <p className="text-sm text-muted-foreground">On analyses</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Top Platform</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{analysisStats.topPlatform}</div>
                  <p className="text-sm text-muted-foreground">Most recommended</p>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Account Security
                </CardTitle>
                <CardDescription>
                  Manage your account security settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Email Verification</p>
                      <p className="text-sm text-muted-foreground">
                        Your email is verified and secure
                      </p>
                    </div>
                    <Badge variant="outline" className="text-green-600">
                      Verified
                    </Badge>
                  </div>

                  <Separator />

                  <div className="space-y-4">
                    <h4 className="text-sm font-medium text-red-600">Danger Zone</h4>
                    <div className="p-4 border border-red-200 rounded-lg bg-red-50">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-red-800">Delete Account</p>
                          <p className="text-sm text-red-600">
                            Permanently delete your account and all data
                          </p>
                        </div>
                        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
                          <DialogTrigger asChild>
                            <Button variant="destructive" size="sm" className="gap-2">
                              <Trash2 className="h-4 w-4" />
                              Delete Account
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Delete Account</DialogTitle>
                              <DialogDescription>
                                This action cannot be undone. This will permanently delete your
                                account and remove all of your data from our servers.
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div className="space-y-2">
                                <Label htmlFor="confirm-delete">
                                  Type "DELETE" to confirm:
                                </Label>
                                <Input
                                  id="confirm-delete"
                                  value={deleteConfirmation}
                                  onChange={(e) => setDeleteConfirmation(e.target.value)}
                                  placeholder="Type DELETE here"
                                />
                              </div>
                            </div>
                            <DialogFooter>
                              <Button
                                variant="outline"
                                onClick={() => setShowDeleteDialog(false)}
                              >
                                Cancel
                              </Button>
                              <Button
                                variant="destructive"
                                onClick={handleDeleteAccount}
                                disabled={deleteConfirmation !== 'DELETE' || saving}
                                className="gap-2"
                              >
                                {saving ? (
                                  <RefreshCw className="h-4 w-4 animate-spin" />
                                ) : (
                                  <Trash2 className="h-4 w-4" />
                                )}
                                Delete Account
                              </Button>
                            </DialogFooter>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Profile;
