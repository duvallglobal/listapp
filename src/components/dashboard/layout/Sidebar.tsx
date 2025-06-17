
import { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import {
  LayoutDashboard,
  Search,
  History,
  CreditCard,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  User,
  Bell,
} from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

interface SidebarProps {
  collapsed?: boolean;
  onToggle?: () => void;
}

export default function Sidebar({ collapsed = false, onToggle }: SidebarProps) {
  const location = useLocation();
  const { user, signOut } = useAuth();

  const navigationItems = [
    {
      title: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
      badge: null,
    },
    {
      title: "Analyze Product",
      href: "/analyze",
      icon: Search,
      badge: null,
    },
    {
      title: "Analysis History",
      href: "/history",
      icon: History,
      badge: null,
    },
    {
      title: "Subscriptions", 
      href: "/subscription",
      icon: CreditCard,
      badge: null,
    },
    {
      title: "Analytics",
      href: "/analytics", 
      icon: BarChart3,
      badge: "New",
    },
  ];

  const bottomItems = [
    {
      title: "Profile",
      href: "/profile",
      icon: User,
    },
    {
      title: "Notifications",
      href: "/notifications", 
      icon: Bell,
    },
    {
      title: "Settings",
      href: "/settings",
      icon: Settings,
    },
  ];

  const handleSignOut = async () => {
    await signOut();
  };

  return (
    <div className={`flex flex-col h-full bg-background border-r transition-all duration-300 
      ${collapsed ? 'w-16' : 'w-64'}`}>
      
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Search className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h2 className="font-semibold text-sm">Price Intelligence</h2>
              <p className="text-xs text-muted-foreground">AI-Powered Analysis</p>
            </div>
          </div>
        )}
        
        {onToggle && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="p-2"
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        )}
      </div>

      {/* User Info */}
      {!collapsed && user && (
        <div className="p-4 border-b">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
              <User className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">
                {user.user_metadata?.full_name || user.email}
              </p>
              <p className="text-xs text-muted-foreground truncate">
                {user.email}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Main Navigation */}
      <ScrollArea className="flex-1 px-3 py-4">
        <div className="space-y-1">
          {navigationItems.map((item) => {
            const isActive = location.pathname === item.href;
            
            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-primary text-primary-foreground' 
                    : 'hover:bg-muted text-muted-foreground hover:text-foreground'
                  }
                  ${collapsed ? 'justify-center' : ''}
                `}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                {!collapsed && (
                  <>
                    <span className="flex-1">{item.title}</span>
                    {item.badge && (
                      <Badge variant="secondary" className="text-xs">
                        {item.badge}
                      </Badge>
                    )}
                  </>
                )}
              </NavLink>
            );
          })}
        </div>

        <Separator className="my-4" />

        {/* Bottom Navigation */}
        <div className="space-y-1">
          {bottomItems.map((item) => {
            const isActive = location.pathname === item.href;
            
            return (
              <NavLink
                key={item.href}
                to={item.href}
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-primary text-primary-foreground' 
                    : 'hover:bg-muted text-muted-foreground hover:text-foreground'
                  }
                  ${collapsed ? 'justify-center' : ''}
                `}
              >
                <item.icon className="h-4 w-4 flex-shrink-0" />
                {!collapsed && <span className="flex-1">{item.title}</span>}
              </NavLink>
            );
          })}
        </div>
      </ScrollArea>

      {/* Sign Out */}
      <div className="p-3 border-t">
        <Button
          variant="ghost"
          onClick={handleSignOut}
          className={`w-full justify-start gap-3 text-muted-foreground hover:text-foreground
            ${collapsed ? 'px-3 justify-center' : ''}
          `}
        >
          <LogOut className="h-4 w-4 flex-shrink-0" />
          {!collapsed && <span>Sign Out</span>}
        </Button>
      </div>
    </div>
  );
}
