
import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '../../ui/sheet';
import {
  Button
} from '../../ui/button';
import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from '../../ui/avatar';
import {
  Separator
} from '../../ui/separator';
import {
  Badge
} from '../../ui/badge';
import {
  Menu,
  Home,
  Search,
  CreditCard,
  User,
  Settings,
  LogOut,
  BarChart3,
  Shield
} from 'lucide-react';

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
}

const navigationItems: NavigationItem[] = [
  { name: 'Dashboard', href: '/dashboard', icon: Home },
  { name: 'Analyze Product', href: '/analyze', icon: Search },
  { name: 'Subscription', href: '/subscription', icon: CreditCard },
  { name: 'Profile', href: '/profile', icon: User },
  { name: 'Admin Panel', href: '/admin', icon: Shield, adminOnly: true },
];

const MobileNavigation: React.FC = () => {
  const { user, signOut, profile } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const handleNavigation = (href: string) => {
    navigate(href);
    setOpen(false);
  };

  const handleSignOut = async () => {
    await signOut();
    setOpen(false);
    navigate('/');
  };

  const getUserInitials = () => {
    if (profile?.full_name) {
      return profile.full_name
        .split(' ')
        .map(name => name[0])
        .join('')
        .toUpperCase()
        .slice(0, 2);
    }
    return user?.email?.charAt(0).toUpperCase() || 'U';
  };

  const isAdmin = profile?.is_admin || false;

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="sm" className="md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle navigation menu</span>
        </Button>
      </SheetTrigger>
      <SheetContent side="left" className="w-80 p-0">
        <div className="flex flex-col h-full">
          {/* Header */}
          <SheetHeader className="p-6 pb-4">
            <div className="flex items-center space-x-3">
              <Avatar className="h-12 w-12">
                <AvatarImage src={profile?.avatar_url} />
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {getUserInitials()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <SheetTitle className="text-left text-lg truncate">
                  {profile?.full_name || 'User'}
                </SheetTitle>
                <SheetDescription className="text-left text-sm truncate">
                  {user?.email}
                </SheetDescription>
                <div className="mt-1">
                  <Badge variant="outline" className="text-xs">
                    {profile?.subscription || 'Free'}
                  </Badge>
                </div>
              </div>
            </div>
          </SheetHeader>

          <Separator />

          {/* Navigation Items */}
          <nav className="flex-1 px-6 py-4">
            <div className="space-y-1">
              {navigationItems.map((item) => {
                // Skip admin-only items for non-admin users
                if (item.adminOnly && !isAdmin) {
                  return null;
                }

                const isActive = location.pathname === item.href;
                const Icon = item.icon;

                return (
                  <button
                    key={item.name}
                    onClick={() => handleNavigation(item.href)}
                    className={`
                      w-full flex items-center space-x-3 px-3 py-2 rounded-lg text-left transition-colors
                      ${isActive
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:text-foreground hover:bg-muted'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5 flex-shrink-0" />
                    <span className="font-medium">{item.name}</span>
                  </button>
                );
              })}
            </div>
          </nav>

          <Separator />

          {/* Footer */}
          <div className="p-6 pt-4">
            <div className="space-y-3">
              {/* Credits Info */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Credits remaining:</span>
                <Badge variant="secondary">
                  {profile?.credits || 0}
                </Badge>
              </div>

              {/* Sign Out Button */}
              <Button
                variant="ghost"
                className="w-full justify-start gap-3 text-muted-foreground hover:text-foreground"
                onClick={handleSignOut}
              >
                <LogOut className="h-4 w-4" />
                Sign out
              </Button>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
};

export default MobileNavigation;
