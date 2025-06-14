import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/components/ui/use-toast";
import {
  Search,
  FileDown,
  Trash2,
  Eye,
  Calendar,
  ArrowUpDown,
} from "lucide-react";
import { supabase } from "../../../supabase/supabase";
import { useAuth } from "../../../supabase/auth";
import { format } from "date-fns";

interface AnalysisHistoryItem {
  id: string;
  created_at: string;
  product_name: string;
  product_image: string;
  recommended_price: number;
  recommended_platform: string;
  analysis_data: any;
}

interface AnalysisHistoryProps {
  onViewAnalysis?: (analysis: AnalysisHistoryItem) => void;
  className?: string;
}

export default function AnalysisHistory({
  onViewAnalysis,
  className = "",
}: AnalysisHistoryProps) {
  const { toast } = useToast();
  const { user } = useAuth();
  const [analyses, setAnalyses] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState<
    "created_at" | "product_name" | "recommended_price"
  >("created_at");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");

  useEffect(() => {
    if (user) {
      fetchAnalysisHistory();
    }
  }, [user]);

  const fetchAnalysisHistory = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const { data, error } = await supabase
        .from("analysis_history")
        .select("*")
        .eq("user_id", user.id)
        .order(sortField, { ascending: sortDirection === "asc" });

      if (error) {
        console.error("Error fetching analysis history:", error);
        // Don't throw error, just show empty state
        setAnalyses([]);
      } else {
        setAnalyses(data || []);
      }
    } catch (error) {
      console.error("Error fetching analysis history:", error);
      setAnalyses([]);
      toast({
        title: "Error loading history",
        description: "There was a problem loading your analysis history.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSort = (
    field: "created_at" | "product_name" | "recommended_price",
  ) => {
    if (sortField === field) {
      // Toggle direction if clicking the same field
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      // Set new field and default to descending
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const handleDeleteAnalysis = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!user) return;

    try {
      const { error } = await supabase
        .from("analysis_history")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);

      if (error) throw error;

      setAnalyses(analyses.filter((analysis) => analysis.id !== id));
      toast({
        title: "Analysis deleted",
        description: "The analysis has been removed from your history.",
      });
    } catch (error) {
      console.error("Error deleting analysis:", error);
      toast({
        title: "Error deleting analysis",
        description: "There was a problem deleting this analysis.",
        variant: "destructive",
      });
    }
  };

  const exportToCsv = () => {
    if (analyses.length === 0) return;

    // Create CSV content
    const headers = ["Date", "Product Name", "Price", "Platform"];
    const rows = analyses.map((analysis) => [
      format(new Date(analysis.created_at), "yyyy-MM-dd"),
      analysis.product_name,
      analysis.recommended_price.toFixed(2),
      analysis.recommended_platform,
    ]);

    const csvContent = [
      headers.join(","),
      ...rows.map((row) => row.join(",")),
    ].join("\n");

    // Create and download the file
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `price-analysis-history-${format(new Date(), "yyyy-MM-dd")}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredAnalyses = analyses.filter(
    (analysis) =>
      analysis.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      analysis.recommended_platform
        .toLowerCase()
        .includes(searchQuery.toLowerCase()),
  );

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  return (
    <Card className={className}>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-xl">Analysis History</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={exportToCsv}
          disabled={analyses.length === 0}
          className="flex items-center gap-1"
        >
          <FileDown className="h-4 w-4" />
          Export
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Search className="h-4 w-4 text-gray-500" />
            <Input
              placeholder="Search by product name or platform..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="flex-1"
            />
          </div>

          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
              <p className="text-gray-500">Loading your analysis history...</p>
            </div>
          ) : filteredAnalyses.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">
                {searchQuery
                  ? "No matching analyses found."
                  : "No analysis history yet."}
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="grid grid-cols-12 gap-4 py-2 px-4 bg-gray-50 rounded-md text-sm font-medium text-gray-500">
                <div
                  className="col-span-5 flex items-center gap-1 cursor-pointer"
                  onClick={() => handleSort("product_name")}
                >
                  Product
                  <ArrowUpDown className="h-3 w-3" />
                </div>
                <div
                  className="col-span-2 flex items-center gap-1 cursor-pointer"
                  onClick={() => handleSort("recommended_price")}
                >
                  Price
                  <ArrowUpDown className="h-3 w-3" />
                </div>
                <div className="col-span-2">Platform</div>
                <div
                  className="col-span-2 flex items-center gap-1 cursor-pointer"
                  onClick={() => handleSort("created_at")}
                >
                  Date
                  <ArrowUpDown className="h-3 w-3" />
                </div>
                <div className="col-span-1"></div>
              </div>

              {filteredAnalyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="grid grid-cols-12 gap-4 py-3 px-4 bg-white rounded-md border border-gray-100 hover:border-gray-300 cursor-pointer transition-colors"
                  onClick={() => onViewAnalysis && onViewAnalysis(analysis)}
                >
                  <div className="col-span-5 flex items-center gap-3">
                    <div className="h-10 w-10 rounded-md bg-gray-100 overflow-hidden flex-shrink-0">
                      {analysis.product_image ? (
                        <img
                          src={analysis.product_image}
                          alt={analysis.product_name}
                          className="h-full w-full object-cover"
                        />
                      ) : (
                        <div className="h-full w-full flex items-center justify-center text-gray-400">
                          <Eye className="h-5 w-5" />
                        </div>
                      )}
                    </div>
                    <span className="font-medium truncate">
                      {analysis.product_name}
                    </span>
                  </div>
                  <div className="col-span-2 flex items-center font-medium">
                    {formatCurrency(analysis.recommended_price)}
                  </div>
                  <div className="col-span-2 flex items-center">
                    <Badge variant="outline">
                      {analysis.recommended_platform}
                    </Badge>
                  </div>
                  <div className="col-span-2 flex items-center text-sm text-gray-500">
                    <Calendar className="h-3 w-3 mr-1" />
                    {format(new Date(analysis.created_at), "MMM d, yyyy")}
                  </div>
                  <div className="col-span-1 flex items-center justify-end">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-gray-500 hover:text-red-500"
                      onClick={(e) => handleDeleteAnalysis(analysis.id, e)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {filteredAnalyses.length > 0 && (
            <div className="pt-2">
              <Separator className="my-2" />
              <p className="text-sm text-gray-500 text-center">
                Showing {filteredAnalyses.length} of {analyses.length} analyses
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
