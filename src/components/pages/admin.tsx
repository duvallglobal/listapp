
import React, { useState, useEffect } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Textarea
} from '../ui/textarea';
import {
  Switch
} from '../ui/switch';
import {
  Users,
  CreditCard,
  BarChart3,
  Settings,
  AlertTriangle,
  Plus,
  Edit,
  Trash2,
  DollarSign,
  RefreshCw,
  Search,
  Download,
  MessageSquare,
  Shield
} from 'lucide-react';

interface AdminUser {
  id: string;
  email: string;
  full_name: string;
  created_at: string;
  credits: number;
  subscription: string;
  stripe_customer_id?: string;
  last_login?: string;
  is_admin: boolean;
}

interface SystemStats {
  totalUsers: number;
  activeSubscriptions: number;
  totalAnalyses: number;
  monthlyRevenue: number;
  avgCreditsPerUser: number;
  topSubscriptionTier: string;
}

interface Announcement {
  id?: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success';
  active: boolean;
  created_at?: string;
}

const AdminPanel: React.FC = () => {
  const { user } = useAuth();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [stats, setStats] = useState<SystemStats>({
    totalUsers: 0,
    activeSubscriptions: 0,
    totalAnalyses: 0,
    monthlyRevenue: 0,
    avgCreditsPerUser: 0,
    topSubscriptionTier: 'Free'
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [showUserDialog, setShowUserDialog] = useState(false);
  const [showAnnouncementDialog, setShowAnnouncementDialog] = useState(false);
  const [announcement, setAnnouncement] = useState<Announcement>({
    title: '',
    message: '',
    type: 'info',
    active: true
  });

  useEffect(() => {
    checkAdminAccess();
  }, [user]);

  const checkAdminAccess = async () => {
    if (!user) return;

    try {
      const { data: userData, error } = await supabase
        .from('users')
        .select('is_admin')
        .eq('id', user.id)
        .single();

      if (error) throw error;

      if (!userData?.is_admin) {
        setError('Access denied. Admin privileges required.');
        return;
      }

      fetchDashboardData();
    } catch (error) {
      console.error('Error checking admin access:', error);
      setError('Failed to verify admin access');
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch users
      const { data: usersData, error: usersError } = await supabase
        .from('users')
        .select('*')
        .order('created_at', { ascending: false });

      if (usersError) throw usersError;

      // Fetch analysis data for stats
      const { data: analysesData, error: analysesError } = await supabase
        .from('analysis_history')
        .select('*');

      if (analysesError) throw analysesError;

      // Calculate stats
      const totalUsers = usersData?.length || 0;
      const activeSubscriptions = usersData?.filter(u => u.subscription !== 'Free').length || 0;
      const totalAnalyses = analysesData?.length || 0;

      const subscriptionCounts: Record<string, number> = {};
      let totalCredits = 0;

      usersData?.forEach(user => {
        const sub = user.subscription || 'Free';
        subscriptionCounts[sub] = (subscriptionCounts[sub] || 0) + 1;
        totalCredits += user.credits || 0;
      });

      const topSubscriptionTier = Object.keys(subscriptionCounts).reduce((a, b) =>
        subscriptionCounts[a] > subscriptionCounts[b] ? a : b, 'Free'
      );

      setUsers(usersData || []);
      setStats({
        totalUsers,
        activeSubscriptions,
        totalAnalyses,
        monthlyRevenue: activeSubscriptions * 19.99, // Simplified calculation
        avgCreditsPerUser: totalUsers > 0 ? totalCredits / totalUsers : 0,
        topSubscriptionTier
      });
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateUser = async (userId: string, updates: Partial<AdminUser>) => {
    try {
      const { error } = await supabase
        .from('users')
        .update(updates)
        .eq('id', userId);

      if (error) throw error;

      // Refresh data
      fetchDashboardData();
      setShowUserDialog(false);
      setSelectedUser(null);
    } catch (error) {
      console.error('Error updating user:', error);
      setError('Failed to update user');
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return;
    }

    try {
      // Delete user's analysis history first
      await supabase.from('analysis_history').delete().eq('user_id', userId);
      
      // Delete user
      const { error } = await supabase.from('users').delete().eq('id', userId);

      if (error) throw error;

      fetchDashboardData();
    } catch (error) {
      console.error('Error deleting user:', error);
      setError('Failed to delete user');
    }
  };

  const handleAllocateCredits = async (userId: string, credits: number) => {
    try {
      const { error } = await supabase
        .from('users')
        .update({ credits })
        .eq('id', userId);

      if (error) throw error;

      fetchDashboardData();
    } catch (error) {
      console.error('Error allocating credits:', error);
      setError('Failed to allocate credits');
    }
  };

  const handleCreateAnnouncement = async () => {
    try {
      const { error } = await supabase
        .from('announcements')
        .insert([{
          title: announcement.title,
          message: announcement.message,
          type: announcement.type,
          active: announcement.active,
          created_by: user?.id
        }]);

      if (error) throw error;

      setShowAnnouncementDialog(false);
      setAnnouncement({
        title: '',
        message: '',
        type: 'info',
        active: true
      });
    } catch (error) {
      console.error('Error creating announcement:', error);
      setError('Failed to create announcement');
    }
  };

  const exportUsersData = () => {
    const csvContent = [
      'Email,Full Name,Created At,Credits,Subscription,Last Login',
      ...users.map(user =>
        `${user.email},${user.full_name || 'N/A'},${user.created_at},${user.credits},${user.subscription},${user.last_login || 'Never'}`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `users-export-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (user.full_name && user.full_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (error && error.includes('Access denied')) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Alert variant="destructive">
          <Shield className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-4 w-4 animate-spin" />
          <span>Loading admin panel...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Admin Panel</h1>
            <p className="text-muted-foreground">
              Manage users, subscriptions, and system settings
            </p>
          </div>
          <div className="flex gap-2">
            <Button onClick={exportUsersData} variant="outline" className="gap-2">
              <Download className="h-4 w-4" />
              Export Data
            </Button>
            <Dialog open={showAnnouncementDialog} onOpenChange={setShowAnnouncementDialog}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <MessageSquare className="h-4 w-4" />
                  New Announcement
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Announcement</DialogTitle>
                  <DialogDescription>
                    Create a system-wide announcement for all users
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={announcement.title}
                      onChange={(e) => setAnnouncement({
                        ...announcement,
                        title: e.target.value
                      })}
                      placeholder="Announcement title"
                    />
                  </div>
                  <div>
                    <Label htmlFor="message">Message</Label>
                    <Textarea
                      id="message"
                      value={announcement.message}
                      onChange={(e) => setAnnouncement({
                        ...announcement,
                        message: e.target.value
                      })}
                      placeholder="Announcement message"
                      rows={4}
                    />
                  </div>
                  <div>
                    <Label htmlFor="type">Type</Label>
                    <Select
                      value={announcement.type}
                      onValueChange={(value: 'info' | 'warning' | 'success') =>
                        setAnnouncement({ ...announcement, type: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="info">Info</SelectItem>
                        <SelectItem value="warning">Warning</SelectItem>
                        <SelectItem value="success">Success</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="active"
                      checked={announcement.active}
                      onCheckedChange={(checked) =>
                        setAnnouncement({ ...announcement, active: checked })
                      }
                    />
                    <Label htmlFor="active">Active</Label>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setShowAnnouncementDialog(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateAnnouncement}>
                    Create Announcement
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>

        {/* Error Alert */}
        {error && !error.includes('Access denied') && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Users</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalUsers}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Subs</CardTitle>
              <CreditCard className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.activeSubscriptions}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalAnalyses}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Monthly Revenue</CardTitle>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                ${stats.monthlyRevenue.toFixed(0)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Avg Credits</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {stats.avgCreditsPerUser.toFixed(1)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Top Tier</CardTitle>
              <Badge variant="outline">{stats.topSubscriptionTier}</Badge>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.topSubscriptionTier}</div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="users" className="space-y-6">
          <TabsList>
            <TabsTrigger value="users">User Management</TabsTrigger>
            <TabsTrigger value="subscriptions">Subscriptions</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                  <div>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>
                      Manage user accounts and permissions
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        placeholder="Search users..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-8 w-64"
                      />
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>User</TableHead>
                        <TableHead>Subscription</TableHead>
                        <TableHead>Credits</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredUsers.map((user) => (
                        <TableRow key={user.id}>
                          <TableCell>
                            <div>
                              <p className="font-medium">{user.email}</p>
                              <p className="text-sm text-muted-foreground">
                                {user.full_name || 'No name set'}
                              </p>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{user.subscription}</Badge>
                          </TableCell>
                          <TableCell>{user.credits}</TableCell>
                          <TableCell>
                            {new Date(user.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => {
                                  setSelectedUser(user);
                                  setShowUserDialog(true);
                                }}
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleDeleteUser(user.id)}
                                className="text-destructive hover:text-destructive"
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Other tabs would be implemented similarly */}
          <TabsContent value="subscriptions">
            <Card>
              <CardHeader>
                <CardTitle>Subscription Management</CardTitle>
                <CardDescription>Coming soon...</CardDescription>
              </CardHeader>
            </Card>
          </TabsContent>

          <TabsContent value="analytics">
            <Card>
              <CardHeader>
                <CardTitle>Analytics & Reporting</CardTitle>
                <CardDescription>Coming soon...</CardDescription>
              </CardHeader>
            </Card>
          </TabsContent>
        </Tabs>

        {/* User Edit Dialog */}
        <Dialog open={showUserDialog} onOpenChange={setShowUserDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Edit User</DialogTitle>
              <DialogDescription>
                Update user information and settings
              </DialogDescription>
            </DialogHeader>
            {selectedUser && (
              <div className="space-y-4">
                <div>
                  <Label htmlFor="user-email">Email</Label>
                  <Input
                    id="user-email"
                    value={selectedUser.email}
                    onChange={(e) => setSelectedUser({
                      ...selectedUser,
                      email: e.target.value
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="user-name">Full Name</Label>
                  <Input
                    id="user-name"
                    value={selectedUser.full_name || ''}
                    onChange={(e) => setSelectedUser({
                      ...selectedUser,
                      full_name: e.target.value
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="user-credits">Credits</Label>
                  <Input
                    id="user-credits"
                    type="number"
                    value={selectedUser.credits}
                    onChange={(e) => setSelectedUser({
                      ...selectedUser,
                      credits: parseInt(e.target.value) || 0
                    })}
                  />
                </div>
                <div>
                  <Label htmlFor="user-subscription">Subscription</Label>
                  <Select
                    value={selectedUser.subscription}
                    onValueChange={(value) => setSelectedUser({
                      ...selectedUser,
                      subscription: value
                    })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Free">Free</SelectItem>
                      <SelectItem value="Basic">Basic</SelectItem>
                      <SelectItem value="Pro">Pro</SelectItem>
                      <SelectItem value="Business">Business</SelectItem>
                      <SelectItem value="Enterprise">Enterprise</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowUserDialog(false)}>
                Cancel
              </Button>
              <Button
                onClick={() => selectedUser && handleUpdateUser(selectedUser.id, {
                  email: selectedUser.email,
                  full_name: selectedUser.full_name,
                  credits: selectedUser.credits,
                  subscription: selectedUser.subscription
                })}
              >
                Save Changes
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
};

export default AdminPanel;
