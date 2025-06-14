import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { Camera, ArrowRight, AlertCircle } from "lucide-react";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import ImageUploader from "./ImageUploader";
import ConditionSelector, { ProductCondition } from "./ConditionSelector";
import AnalysisLoading from "./AnalysisLoading";
import AnalysisResult, {
  AnalysisResultData,
  MarketplaceRecommendation,
} from "./AnalysisResult";
import { supabase } from "../../../supabase/supabase";
import { useAuth } from "../../../supabase/auth";

interface ProductAnalyzerProps {
  onAnalysisComplete?: (result: AnalysisResultData) => void;
  className?: string;
}

export default function ProductAnalyzer({
  onAnalysisComplete,
  className = "",
}: ProductAnalyzerProps) {
  const { toast } = useToast();
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState("upload");
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const [selectedCondition, setSelectedCondition] =
    useState<ProductCondition>("good");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState(1);
  const [analysisResult, setAnalysisResult] =
    useState<AnalysisResultData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [remainingCredits, setRemainingCredits] = useState<number | null>(null);
  const [previewImage, setPreviewImage] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      fetchUserCredits();
    }
  }, [user]);

  const fetchUserCredits = async () => {
    if (!user) return;

    try {
      const { data, error } = await supabase
        .from("users")
        .select("credits")
        .eq("user_id", user.id)
        .single();

      if (error) {
        console.log("User not found in users table, creating entry...");
        // Create user entry if it doesn't exist
        const { error: insertError } = await supabase.from("users").insert({
          user_id: user.id,
          email: user.email,
          credits: "5", // Give 5 free credits
          token_identifier: user.email || user.id,
        });

        if (insertError) {
          console.error("Error creating user entry:", insertError);
        }

        setRemainingCredits(5);
        return;
      }

      // If credits is null, set a default of 5 (free trial)
      const credits = data?.credits ? parseInt(data.credits) : 5;
      setRemainingCredits(credits);
    } catch (error) {
      console.error("Error fetching user credits:", error);
      // Default to 5 credits if there's an error
      setRemainingCredits(5);
    }
  };

  const handleImagesSelected = (images: File[]) => {
    setSelectedImages(images);
    if (images.length > 0) {
      setPreviewImage(URL.createObjectURL(images[0]));
    } else {
      setPreviewImage(null);
    }
  };

  const handleConditionChange = (condition: ProductCondition) => {
    setSelectedCondition(condition);
  };

  const startAnalysis = async () => {
    if (selectedImages.length === 0) {
      toast({
        title: "No images selected",
        description: "Please upload at least one product image to analyze.",
        variant: "destructive",
      });
      return;
    }

    if (remainingCredits !== null && remainingCredits <= 0) {
      toast({
        title: "No credits remaining",
        description: "Please upgrade your plan to analyze more products.",
        variant: "destructive",
      });
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    setActiveTab("analyzing");

    try {
      // Convert image to base64
      const imageFile = selectedImages[0];
      const base64Image = await convertImageToBase64(imageFile);

      // Show analysis stages
      await simulateAnalysisStages();

      // Call the analyze-product edge function
      const { data, error } = await supabase.functions.invoke(
        "supabase-functions-analyze-product",
        {
          body: {
            imageBase64: base64Image,
            condition: selectedCondition,
          },
        },
      );

      if (error) {
        console.error("Supabase function error:", error);
        throw new Error(`Function call failed: ${error.message}`);
      }

      if (!data) {
        throw new Error("No data returned from analysis function");
      }

      if (!data.success) {
        console.error("Analysis function returned error:", data);
        throw new Error(data.error || data.details || "Analysis failed");
      }

      // Convert the API response to our expected format
      const analysisData = data.analysis;
      const result: AnalysisResultData = {
        productName: analysisData.productName,
        brand: analysisData.brand || "Unknown",
        material: analysisData.material || "Unknown",
        styleOrType: analysisData.category || "Unknown",
        color: analysisData.color || "Unknown",
        sizeOrDimensions: "Unknown",
        condition: analysisData.condition,
        eraOrKeySpecs: analysisData.keyFeatures?.join(", ") || "Unknown",
        accessories: "None",
        detailedDescription: analysisData.description,
        tagsKeywords: analysisData.tags || [],
        suggestedCategory: analysisData.category || "General",
        recommendedPricing: {
          low: analysisData.pricing.low,
          median: analysisData.pricing.median,
          high: analysisData.pricing.high,
        },
        estimatedTimeToSell: "1-2 weeks",
        platformRecommendation:
          analysisData.marketplaceRecommendations[0]?.platform || "eBay",
        marketplaceRecommendations: analysisData.marketplaceRecommendations.map(
          (rec: any) => ({
            name: rec.platform,
            reasoning: rec.reasoning,
            fees: "Variable",
            audience: "General",
            suitability: rec.suitability,
            estimatedProfit: rec.estimatedProfit,
          }),
        ),
        generatedTitle: analysisData.generatedTitle,
        reasoning:
          "AI-powered analysis based on image recognition and market data",
        confidenceScore: analysisData.confidenceScore,
      };

      setAnalysisResult(result);

      // Update user credits
      if (user) {
        await updateUserCredits();
      }

      // Move to results tab
      setActiveTab("results");

      // Call the callback if provided
      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }
    } catch (error) {
      console.error("Analysis error:", error);
      setError(`Analysis failed: ${error.message || "Please try again."}`);
      setActiveTab("upload");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const convertImageToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  const updateUserCredits = async () => {
    if (!user || remainingCredits === null) return;

    try {
      const newCredits = Math.max(0, remainingCredits - 1);

      const { error } = await supabase
        .from("users")
        .update({ credits: newCredits.toString() })
        .eq("user_id", user.id);

      if (error) {
        console.error("Error updating user credits:", error);
        return;
      }

      setRemainingCredits(newCredits);
    } catch (error) {
      console.error("Error updating user credits:", error);
    }
  };

  const simulateAnalysisStages = async () => {
    // Simulate the different stages of analysis
    const stageDelays = [2000, 3000, 3000, 2000, 3000, 2000, 1000];

    for (let i = 1; i <= stageDelays.length; i++) {
      setAnalysisStage(i);
      await new Promise((resolve) => setTimeout(resolve, stageDelays[i - 1]));
    }
  };

  const generateMockAnalysisResult = (): AnalysisResultData => {
    // This would be replaced with actual API response data
    const marketplaceRecommendations: MarketplaceRecommendation[] = [
      {
        name: "eBay",
        reasoning:
          "eBay has the largest audience for this type of item and offers competitive fees. The platform's auction format can help maximize price for collectible or rare items.",
        fees: "13.25% + $0.30",
        audience: "Large global audience",
        suitability: 9,
        estimatedProfit: 85.25,
      },
      {
        name: "Poshmark",
        reasoning:
          "Poshmark specializes in fashion items and has a dedicated audience, but charges higher fees than eBay.",
        fees: "20%",
        audience: "Fashion-focused buyers",
        suitability: 7,
        estimatedProfit: 80.0,
      },
      {
        name: "Facebook Marketplace",
        reasoning:
          "Low fees but smaller audience for this specific item category. Better for local pickup items.",
        fees: "5%",
        audience: "Local buyers primarily",
        suitability: 6,
        estimatedProfit: 95.0,
      },
    ];

    return {
      productName: "Vintage Leather Jacket",
      brand: "Wilson Leather",
      material: "Genuine Leather",
      styleOrType: "Bomber Jacket",
      color: "Brown",
      sizeOrDimensions: "Men's Large",
      condition:
        selectedCondition === "new"
          ? "New with tags"
          : selectedCondition === "like_new"
            ? "Like new"
            : selectedCondition === "excellent"
              ? "Excellent used condition"
              : selectedCondition === "good"
                ? "Good used condition"
                : selectedCondition === "fair"
                  ? "Fair condition"
                  : "Poor condition",
      eraOrKeySpecs: "1990s, zip front, quilted lining, two front pockets",
      accessories: "None",
      detailedDescription:
        "Classic vintage Wilson leather bomber jacket in rich brown. Features a durable full-grain leather exterior with minimal wear and a warm quilted lining. Includes zippered front closure, ribbed cuffs and waistband, and two exterior pockets. Perfect for casual wear or adding a rugged touch to any outfit. This timeless piece has been well-maintained and shows only minor signs of wear consistent with its age.",
      tagsKeywords: [
        "leather jacket",
        "bomber jacket",
        "Wilson leather",
        "vintage",
        "men's jacket",
        "brown leather",
        "90s fashion",
        "outerwear",
        "winter jacket",
        "casual jacket",
        "motorcycle jacket",
      ],
      suggestedCategory: "Clothing & Accessories",
      recommendedPricing: {
        low: 75.0,
        median: 99.99,
        high: 125.0,
      },
      estimatedTimeToSell: "1-2 weeks",
      platformRecommendation: "eBay",
      marketplaceRecommendations,
      generatedTitle:
        "Vintage 90s Wilson Leather Brown Bomber Jacket Men's Size Large Excellent Condition",
      reasoning:
        "Based on recent sales of similar vintage leather jackets, the recommended price range accounts for the brand (Wilson Leather), condition (good), style (bomber), and current market demand. Leather jackets in this style typically sell between $75-$125 depending on condition and features.",
      confidenceScore: 0.92,
    };
  };

  const saveAnalysis = async () => {
    if (!analysisResult || !user) {
      toast({
        title: "Cannot save analysis",
        description:
          "Please ensure you're logged in and have completed an analysis.",
        variant: "destructive",
      });
      return;
    }

    try {
      const { error } = await supabase.from("analysis_history").insert({
        user_id: user.id,
        product_name: analysisResult.productName,
        product_image: previewImage,
        recommended_price: analysisResult.recommendedPricing.median,
        recommended_platform: analysisResult.platformRecommendation,
        analysis_data: analysisResult,
      });

      if (error) {
        console.error("Error saving analysis:", error);
        throw error;
      }

      toast({
        title: "Analysis saved",
        description: "This analysis has been saved to your history.",
      });
    } catch (error) {
      console.error("Error saving analysis:", error);
      toast({
        title: "Error saving analysis",
        description:
          "There was a problem saving this analysis. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <Card className={`${className}`}>
      <CardHeader>
        <CardTitle className="text-2xl flex items-center gap-2">
          <Camera className="h-6 w-6" />
          Product Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="upload" disabled={isAnalyzing}>
              Upload
            </TabsTrigger>
            <TabsTrigger value="analyzing" disabled={!isAnalyzing}>
              Analyzing
            </TabsTrigger>
            <TabsTrigger value="results" disabled={!analysisResult}>
              Results
            </TabsTrigger>
          </TabsList>

          <TabsContent value="upload" className="space-y-6 pt-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium">Upload Product Images</h3>
              {remainingCredits !== null && (
                <div className="text-sm text-gray-500">
                  Credits remaining:{" "}
                  <span className="font-medium">{remainingCredits}</span>
                </div>
              )}
            </div>

            <ImageUploader
              onImagesSelected={handleImagesSelected}
              maxImages={3}
            />

            <ConditionSelector
              selectedCondition={selectedCondition}
              onConditionChange={handleConditionChange}
            />
          </TabsContent>

          <TabsContent value="analyzing" className="pt-4">
            <AnalysisLoading stage={analysisStage} />
          </TabsContent>

          <TabsContent value="results" className="pt-4">
            {analysisResult && previewImage && (
              <AnalysisResult
                result={analysisResult}
                productImage={previewImage}
                onSave={saveAnalysis}
              />
            )}
          </TabsContent>
        </Tabs>
      </CardContent>

      {activeTab === "upload" && (
        <CardFooter className="flex justify-end">
          <Button
            onClick={startAnalysis}
            disabled={selectedImages.length === 0 || isAnalyzing}
            className="gap-2"
          >
            Start Analysis
            <ArrowRight className="h-4 w-4" />
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}
