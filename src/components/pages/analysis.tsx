import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Camera, History, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";
import TopNavigation from "../dashboard/layout/TopNavigation";
import Sidebar from "../dashboard/layout/Sidebar";
import ProductAnalyzer from "../ai/ProductAnalyzer";
import AnalysisHistory from "../dashboard/AnalysisHistory";
import AnalysisResult, { AnalysisResultData } from "../ai/AnalysisResult";

interface AnalysisHistoryItem {
  id: string;
  created_at: string;
  product_name: string;
  product_image: string;
  recommended_price: number;
  recommended_platform: string;
  analysis_data: AnalysisResultData;
}

export default function AnalysisPage() {
  const [activeTab, setActiveTab] = useState("new");
  const [selectedAnalysis, setSelectedAnalysis] =
    useState<AnalysisHistoryItem | null>(null);

  const handleViewAnalysis = (analysis: AnalysisHistoryItem) => {
    setSelectedAnalysis(analysis);
    setActiveTab("view");
  };

  const handleBackToHistory = () => {
    setSelectedAnalysis(null);
    setActiveTab("history");
  };

  return (
    <div className="min-h-screen bg-white">
      <TopNavigation />

      <div className="flex pt-16">
        <Sidebar activeItem="Analysis" />

        <main className="flex-1 overflow-auto p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-800">
              Product Analysis
            </h1>
            <p className="text-gray-600">
              Analyze products to get pricing and marketplace recommendations
            </p>
          </div>

          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="w-full"
          >
            <TabsList className="grid w-full max-w-md grid-cols-2 mb-6">
              <TabsTrigger value="new" className="flex items-center gap-2">
                <Camera className="h-4 w-4" />
                New Analysis
              </TabsTrigger>
              <TabsTrigger value="history" className="flex items-center gap-2">
                <History className="h-4 w-4" />
                History
              </TabsTrigger>
            </TabsList>

            <TabsContent value="new">
              <ProductAnalyzer />
            </TabsContent>

            <TabsContent value="history">
              <AnalysisHistory onViewAnalysis={handleViewAnalysis} />
            </TabsContent>

            <TabsContent value="view">
              {selectedAnalysis && (
                <div className="space-y-4">
                  <Button
                    variant="ghost"
                    onClick={handleBackToHistory}
                    className="flex items-center gap-2 mb-4"
                  >
                    <ArrowLeft className="h-4 w-4" />
                    Back to History
                  </Button>

                  <AnalysisResult
                    result={selectedAnalysis.analysis_data}
                    productImage={selectedAnalysis.product_image}
                  />
                </div>
              )}
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}
