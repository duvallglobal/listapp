import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Copy,
  Check,
  ExternalLink,
  DollarSign,
  ShoppingBag,
  Tag,
  FileText,
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

export interface PriceRange {
  low: number;
  median: number;
  high: number;
}

export interface MarketplaceRecommendation {
  name: string;
  reasoning: string;
  fees: string;
  audience: string;
  suitability: number; // 1-10 rating
  estimatedProfit: number;
}

export interface AnalysisResultData {
  productName: string;
  brand: string;
  material: string;
  styleOrType: string;
  color: string;
  sizeOrDimensions: string;
  condition: string;
  eraOrKeySpecs: string;
  accessories: string;
  detailedDescription: string;
  tagsKeywords: string[];
  suggestedCategory: string;
  recommendedPricing: PriceRange;
  estimatedTimeToSell: string;
  platformRecommendation: string;
  marketplaceRecommendations: MarketplaceRecommendation[];
  generatedTitle: string;
  reasoning: string;
  confidenceScore: number;
}

interface AnalysisResultProps {
  result: AnalysisResultData;
  productImage: string;
  onSave?: () => void;
  className?: string;
}

export default function AnalysisResult({
  result,
  productImage,
  onSave,
  className = "",
}: AnalysisResultProps) {
  const { toast } = useToast();
  const [copiedField, setCopiedField] = useState<string | null>(null);

  const copyToClipboard = (text: string, fieldName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedField(fieldName);
    toast({
      title: "Copied to clipboard",
      description: `${fieldName} has been copied to your clipboard.`,
    });
    setTimeout(() => setCopiedField(null), 2000);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  return (
    <div className={`space-y-6 ${className}`}>
      <div className="flex flex-col md:flex-row gap-6">
        {/* Product Image */}
        <Card className="md:w-1/3">
          <CardContent className="p-4">
            <div className="aspect-square rounded-md overflow-hidden bg-gray-100">
              <img
                src={productImage}
                alt={result.productName}
                className="w-full h-full object-cover"
              />
            </div>
          </CardContent>
        </Card>

        {/* Product Details */}
        <Card className="md:w-2/3">
          <CardHeader className="pb-3">
            <div className="flex justify-between items-start">
              <div>
                <Badge className="mb-2">{result.suggestedCategory}</Badge>
                <CardTitle className="text-2xl font-bold">
                  {result.productName}
                </CardTitle>
              </div>
              <Badge
                variant={result.confidenceScore > 0.8 ? "default" : "outline"}
                className="ml-2"
              >
                {Math.round(result.confidenceScore * 100)}% Confidence
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <h4 className="text-sm font-medium text-gray-500">Brand</h4>
                <p>{result.brand || "Unbranded"}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Material</h4>
                <p>{result.material || "Not specified"}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Style/Type
                </h4>
                <p>{result.styleOrType || "Not specified"}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Color</h4>
                <p>{result.color || "Not specified"}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">
                  Size/Dimensions
                </h4>
                <p>{result.sizeOrDimensions || "Not specified"}</p>
              </div>
              <div>
                <h4 className="text-sm font-medium text-gray-500">Condition</h4>
                <p>{result.condition || "Not specified"}</p>
              </div>
            </div>

            <Separator />

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">
                Specifications
              </h4>
              <p className="text-sm">
                {result.eraOrKeySpecs || "No specifications available"}
              </p>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-1">
                Accessories
              </h4>
              <p className="text-sm">
                {result.accessories || "No accessories included"}
              </p>
            </div>

            <div className="flex justify-end">
              <Button
                variant="outline"
                size="sm"
                className="flex items-center gap-1"
                onClick={() =>
                  copyToClipboard(
                    JSON.stringify(
                      {
                        name: result.productName,
                        brand: result.brand,
                        material: result.material,
                        styleOrType: result.styleOrType,
                        color: result.color,
                        sizeOrDimensions: result.sizeOrDimensions,
                        condition: result.condition,
                        eraOrKeySpecs: result.eraOrKeySpecs,
                        accessories: result.accessories,
                      },
                      null,
                      2,
                    ),
                    "Product Details",
                  )
                }
              >
                {copiedField === "Product Details" ? (
                  <>
                    <Check className="h-4 w-4" />
                    Copied
                  </>
                ) : (
                  <>
                    <Copy className="h-4 w-4" />
                    Copy Details
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for different sections */}
      <Tabs defaultValue="pricing" className="w-full">
        <TabsList className="grid grid-cols-4 mb-4">
          <TabsTrigger value="pricing">
            <DollarSign className="h-4 w-4 mr-2" />
            Pricing
          </TabsTrigger>
          <TabsTrigger value="marketplace">
            <ShoppingBag className="h-4 w-4 mr-2" />
            Marketplace
          </TabsTrigger>
          <TabsTrigger value="listing">
            <FileText className="h-4 w-4 mr-2" />
            Listing Content
          </TabsTrigger>
          <TabsTrigger value="tags">
            <Tag className="h-4 w-4 mr-2" />
            Tags
          </TabsTrigger>
        </TabsList>

        {/* Pricing Tab */}
        <TabsContent value="pricing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">Recommended Pricing</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-500">Low</h4>
                  <p className="text-2xl font-bold">
                    {formatCurrency(result.recommendedPricing.low)}
                  </p>
                </div>
                <div className="text-center p-4 bg-primary/10 rounded-lg border-2 border-primary/20">
                  <h4 className="text-sm font-medium text-gray-500">
                    Recommended
                  </h4>
                  <p className="text-2xl font-bold">
                    {formatCurrency(result.recommendedPricing.median)}
                  </p>
                </div>
                <div className="text-center p-4 bg-gray-50 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-500">High</h4>
                  <p className="text-2xl font-bold">
                    {formatCurrency(result.recommendedPricing.high)}
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-500">
                    Estimated Time to Sell
                  </h4>
                  <p>{result.estimatedTimeToSell}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-500">
                    Pricing Reasoning
                  </h4>
                  <p className="text-sm">{result.reasoning}</p>
                </div>
              </div>

              <div className="flex justify-end mt-4">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                  onClick={() =>
                    copyToClipboard(
                      formatCurrency(result.recommendedPricing.median),
                      "Recommended Price",
                    )
                  }
                >
                  {copiedField === "Recommended Price" ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy Price
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Marketplace Tab */}
        <TabsContent value="marketplace" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">
                Marketplace Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="p-4 bg-primary/10 rounded-lg border-2 border-primary/20">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-lg font-bold">
                    {result.platformRecommendation}
                  </h3>
                  <Badge>Best Match</Badge>
                </div>
                <p className="text-sm mb-4">
                  {result.marketplaceRecommendations[0]?.reasoning ||
                    "This platform offers the best combination of fees, audience reach, and category fit for your item."}
                </p>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <div>
                    <h4 className="font-medium text-gray-500">Est. Profit</h4>
                    <p className="font-bold">
                      {formatCurrency(
                        result.marketplaceRecommendations[0]?.estimatedProfit ||
                          result.recommendedPricing.median * 0.85,
                      )}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-500">Fees</h4>
                    <p>
                      {result.marketplaceRecommendations[0]?.fees ||
                        "~15% of sale price"}
                    </p>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-500">Audience</h4>
                    <p>
                      {result.marketplaceRecommendations[0]?.audience ||
                        "Large, diverse audience"}
                    </p>
                  </div>
                </div>
              </div>

              {result.marketplaceRecommendations
                .slice(1, 3)
                .map((rec, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="flex justify-between items-center mb-2">
                      <h3 className="text-lg font-medium">{rec.name}</h3>
                      <Badge variant="outline">Alternative {index + 1}</Badge>
                    </div>
                    <p className="text-sm mb-4">{rec.reasoning}</p>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <h4 className="font-medium text-gray-500">
                          Est. Profit
                        </h4>
                        <p className="font-bold">
                          {formatCurrency(rec.estimatedProfit)}
                        </p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-500">Fees</h4>
                        <p>{rec.fees}</p>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-500">Audience</h4>
                        <p>{rec.audience}</p>
                      </div>
                    </div>
                  </div>
                ))}

              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                  onClick={() =>
                    copyToClipboard(
                      result.platformRecommendation,
                      "Recommended Platform",
                    )
                  }
                >
                  {copiedField === "Recommended Platform" ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy Platform
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Listing Content Tab */}
        <TabsContent value="listing" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">
                Generated Listing Content
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <h4 className="text-sm font-medium text-gray-500">Title</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 flex items-center gap-1"
                    onClick={() =>
                      copyToClipboard(result.generatedTitle, "Title")
                    }
                  >
                    {copiedField === "Title" ? (
                      <Check className="h-3 w-3" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <p className="text-base font-medium p-3 bg-gray-50 rounded-md">
                  {result.generatedTitle}
                </p>
              </div>

              <div>
                <div className="flex justify-between items-center mb-2">
                  <h4 className="text-sm font-medium text-gray-500">
                    Description
                  </h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 flex items-center gap-1"
                    onClick={() =>
                      copyToClipboard(result.detailedDescription, "Description")
                    }
                  >
                    {copiedField === "Description" ? (
                      <Check className="h-3 w-3" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </Button>
                </div>
                <div className="p-3 bg-gray-50 rounded-md whitespace-pre-line">
                  {result.detailedDescription}
                </div>
              </div>

              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                  onClick={() =>
                    copyToClipboard(
                      `${result.generatedTitle}\n\n${result.detailedDescription}`,
                      "Full Listing Content",
                    )
                  }
                >
                  {copiedField === "Full Listing Content" ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy All Content
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tags Tab */}
        <TabsContent value="tags" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-xl">
                Suggested Tags & Keywords
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2 mb-4">
                {result.tagsKeywords.map((tag, index) => (
                  <Badge key={index} variant="secondary" className="text-sm">
                    {tag}
                  </Badge>
                ))}
              </div>

              <div className="flex justify-end">
                <Button
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-1"
                  onClick={() =>
                    copyToClipboard(
                      result.tagsKeywords.join(", "),
                      "Tags & Keywords",
                    )
                  }
                >
                  {copiedField === "Tags & Keywords" ? (
                    <>
                      <Check className="h-4 w-4" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      Copy All Tags
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() =>
            window.open(
              `https://${result.platformRecommendation.toLowerCase().replace(/\s+/g, "")}.com`,
              "_blank",
            )
          }
          className="flex items-center gap-2"
        >
          <ExternalLink className="h-4 w-4" />
          Visit {result.platformRecommendation}
        </Button>

        {onSave && <Button onClick={onSave}>Save Analysis</Button>}
      </div>
    </div>
  );
}
