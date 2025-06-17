import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger,
  DropdownMenuSeparator 
} from "@/components/ui/dropdown-menu";
import { Badge } from "@/components/ui/badge";
import { 
  Home, 
  Search, 
  CreditCard, 
  History, 
  Settings, 
  LogOut,
  User,
  AlertCircle,
  RefreshCw
} from "lucide-react";
import { useNavigate, useLocation } from "react-router-dom";
import { supabase } from "@/lib/supabase";
import { useAuth } from "@/contexts/AuthContext";

interface TopNavigationProps {
  user?: any;
}

export function TopNavigation({ user }: TopNavigationProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { connectionStatus, retryConnection } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [isRetrying, setIsRetrying] = useState(false);

  const handleSignOut = async () => {
    setIsLoading(true);
    try {
      await supabase.auth.signOut();
      navigate("/");
    } catch (error) {
      console.error("Error signing out:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRetryConnection = async () => {
    setIsRetrying(true);
    try {
      await retryConnection();
    } finally {
      setIsRetrying(false);
    }
  };

  // Updated navigation items (removed Team and Help)
  const navigationItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: Home,
    },
    {
      name: "New Analysis",
      href: "/analysis",
      icon: Search,
    },
    {
      name: "Analysis History",
      href: "/history",
      icon: History,
    },
    {
      name: "Subscription",
      href: "/subscription",
      icon: CreditCard,
    },
  ];

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <div className="flex h-full flex-col">
      {/* Logo */}
      <div className="flex h-16 items-center border-b px-6">
        <div className="flex items-center space-x-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600"></div>
          <span className="text-xl font-bold">Price Intelligence</span>
        </div>
      </div>

      {/* Connection Status */}
      {connectionStatus !== 'connected' && (
        <div className="border-b border-red-200 bg-red-50 px-4 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span className="text-sm text-red-700">
                {connectionStatus === 'checking' ? 'Checking connection...' : 'Database offline'}
              </span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={handleRetryConnection}
              disabled={isRetrying || connectionStatus === 'checking'}
              className="text-red-700 border-red-300 hover:bg-red-100"
            >
              {isRetrying ? (
                <RefreshCw className="h-3 w-3 animate-spin" />
              ) : (
                'Retry'
              )}
            </Button>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="flex-1 space-y-2 px-4 py-6">
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const disabled = connectionStatus !== 'connected' && item.href !== '/dashboard';

          return (
            <Button
              key={item.name}
              variant={isActive(item.href) ? "secondary" : "ghost"}
              className={`w-full justify-start transition-all duration-200 ${
                isActive(item.href) 
                  ? "bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20" 
                  : "hover:bg-gradient-to-r hover:from-blue-500/5 hover:to-purple-500/5"
              } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
              onClick={() => !disabled && navigate(item.href)}
              disabled={disabled}
            >
              <Icon className="mr-3 h-5 w-5" />
              {item.name}
              {disabled && (
                <Badge variant="secondary" className="ml-auto text-xs">
                  Offline
                </Badge>
              )}
            </Button>
          );
        })}
      </nav>

      {/* Connection Status Badge */}
      <div className="px-4 pb-2">
        <div className="flex items-center justify-center">
          <Badge 
            variant={connectionStatus === 'connected' ? 'default' : 'destructive'}
            className="text-xs"
          >
            {connectionStatus === 'connected' && '● Online'}
            {connectionStatus === 'disconnected' && '● Offline'}
            {connectionStatus === 'checking' && '● Connecting...'}
          </Badge>
        </div>
      </div>

      {/* User Menu */}
      <div className="border-t p-4">
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="w-full justify-start p-2">
              <Avatar className="h-8 w-8 mr-3">
                <AvatarImage src={user?.avatar_url} />
                <AvatarFallback>
                  {user?.full_name?.charAt(0) || user?.email?.charAt(0) || "U"}
                </AvatarFallback>
              </Avatar>
              <div className="flex flex-col items-start flex-1 min-w-0">
                <span className="text-sm font-medium truncate">
                  {user?.full_name || "User"}
                </span>
                <span className="text-xs text-muted-foreground truncate">
                  {user?.email}
                </span>
              </div>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuItem 
              onClick={() => navigate("/profile")}
              disabled={connectionStatus !== 'connected'}
            >
              <User className="mr-2 h-4 w-4" />
              Profile
              {connectionStatus !== 'connected' && (
                <Badge variant="secondary" className="ml-auto text-xs">
                  Offline
                </Badge>
              )}
            </DropdownMenuItem>
            <DropdownMenuItem 
              onClick={() => navigate("/settings")}
              disabled={connectionStatus !== 'connected'}
            >
              <Settings className="mr-2 h-4 w-4" />
              Settings
              {connectionStatus !== 'connected' && (
                <Badge variant="secondary" className="ml-auto text-xs">
                  Offline
                </Badge>
              )}
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={handleSignOut} disabled={isLoading}>
              <LogOut className="mr-2 h-4 w-4" />
              {isLoading ? "Signing out..." : "Sign Out"}
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}