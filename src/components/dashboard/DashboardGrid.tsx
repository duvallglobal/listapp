import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { supabase } from "../../../supabase/supabase";
import { useAuth } from "../../../supabase/auth";

interface DashboardStats {
  totalAnalyses: number;
  avgPrice: number;
  topPlatform: string;
}

export default function DashboardGrid() {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    totalAnalyses: 0,
    avgPrice: 0,
    topPlatform: "eBay",
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchDashboardStats();
    }
  }, [user]);

  const fetchDashboardStats = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from("analysis_history")
        .select("recommended_price, recommended_platform")
        .eq("user_id", user.id);

      if (error) {
        console.error("Error fetching dashboard stats:", error);
        setLoading(false);
        return;
      }

      const analyses = data || [];
      const totalAnalyses = analyses.length;

      let avgPrice = 0;
      let topPlatform = "eBay";

      if (totalAnalyses > 0) {
        // Calculate average price
        const totalPrice = analyses.reduce(
          (sum, analysis) => sum + (analysis.recommended_price || 0),
          0,
        );
        avgPrice = totalPrice / totalAnalyses;

        // Find most recommended platform
        const platformCounts: { [key: string]: number } = {};
        analyses.forEach((analysis) => {
          const platform = analysis.recommended_platform || "eBay";
          platformCounts[platform] = (platformCounts[platform] || 0) + 1;
        });

        topPlatform =
          Object.keys(platformCounts).reduce((a, b) =>
            platformCounts[a] > platformCounts[b] ? a : b,
          ) || "eBay";
      }

      setStats({
        totalAnalyses,
        avgPrice,
        topPlatform,
      });
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="border border-gray-200 shadow-sm">
            <CardHeader className="pb-2">
              <div className="h-4 bg-gray-200 rounded animate-pulse" />
            </CardHeader>
            <CardContent>
              <div className="h-8 bg-gray-200 rounded animate-pulse mb-2" />
              <div className="h-3 bg-gray-200 rounded animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <Card className="border border-gray-200 shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Total Analyses</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.totalAnalyses}</div>
          <p className="text-xs text-gray-500">All time</p>
        </CardContent>
      </Card>
      <Card className="border border-gray-200 shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Avg. Price</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {stats.totalAnalyses > 0 ? formatCurrency(stats.avgPrice) : "$0"}
          </div>
          <p className="text-xs text-gray-500">Per item analyzed</p>
        </CardContent>
      </Card>
      <Card className="border border-gray-200 shadow-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium">Top Platform</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{stats.topPlatform}</div>
          <p className="text-xs text-gray-500">Most recommended</p>
        </CardContent>
      </Card>
    </div>
  );
}
