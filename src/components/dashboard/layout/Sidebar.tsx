import React from "react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Home,
  LayoutDashboard,
  Calendar,
  Users,
  Settings,
  HelpCircle,
  FolderKanban,
} from "lucide-react";

interface NavItem {
  icon: React.ReactNode;
  label: string;
  href?: string;
  isActive?: boolean;
}

interface SidebarProps {
  items?: NavItem[];
  activeItem?: string;
  onItemClick?: (label: string) => void;
}

const defaultNavItems: NavItem[] = [
  { icon: <LayoutDashboard size={18} />, label: "Dashboard", href: "/dashboard" },
  { icon: <FolderKanban size={18} />, label: "Product Analysis", href: "/analysis" },
  { icon: <Calendar size={18} />, label: "Subscription", href: "/subscription" },
  { icon: <Users size={18} />, label: "Team", href: "/team" },
  { icon: <HelpCircle size={18} />, label: "Help", href: "/help" },
];

const defaultBottomItems: NavItem[] = [];

import { Link, useLocation } from "react-router-dom";

const Sidebar = ({
  items = defaultNavItems,
  activeItem,
}: SidebarProps) => {
  const location = useLocation();
  return (
    <div className="w-[240px] h-full border-r border-gray-200 bg-white flex flex-col">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-1">PriceVision AI</h2>
        <p className="text-sm text-gray-500">AI-powered price intelligence</p>
      </div>

      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1">
          {items.map((item) => (
            <Link
              key={item.label}
              to={item.href || "/"}
              className={`w-full flex items-center gap-2 text-sm h-10 px-4 py-2 rounded-md transition-colors ${location.pathname.startsWith(item.href || "/") ? "bg-gray-100 text-primary font-semibold" : "hover:bg-gray-50 text-gray-700"}`}
              style={{ textDecoration: "none" }}
            >
              {item.icon}
              {item.label}
            </Link>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
};

export default Sidebar;
