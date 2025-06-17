import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { 
  TrendingUp, 
  DollarSign, 
  Package, 
  Calculator,
  ExternalLink,
  Download,
  Share
} from "lucide-react";

interface AnalysisResultProps {
  result: {
    id: string;
    product_name: string;
    condition: string;
    image_url?: string;
    image_urls?: string[];
    analysis_result?: any;
    pricing_data?: any;
    marketplace_recommendations?: any;
    fee_calculations?: any;
    created_at: string;
  };
}

export default function AnalysisResult({ result }: AnalysisResultProps) {
  const analysisData = result.analysis_result || {};
  const pricingData = result.pricing_data || {};
  const recommendations = result.marketplace_recommendations || {};
  const feeCalculations = result.fee_calculations || {};

  // Get the best image URL
  const getImageUrl = () => {
    if (result.image_urls && result.image_urls.length > 0) {
      return result.image_urls[0];
    }
    return result.image_url;
  };

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.target as HTMLImageElement;
    img.style.display = 'none';
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const getConditionBadgeVariant = (condition: string) => {
    switch (condition.toLowerCase()) {
      case 'new': return 'default';
      case 'like new': return 'secondary';
      case 'good': return 'outline';
      case 'fair': return 'destructive';
      default: return 'secondary';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50">
        <CardHeader>
          <div className="flex flex-col md:flex-row gap-6">
            {/* Product Image */}
            <div className="flex-shrink-0">
              {getImageUrl() ? (
                <img
                  src={getImageUrl()}
                  alt={result.product_name}
                  className="w-32 h-32 object-cover rounded-lg border shadow-sm"
                  onError={handleImageError}
                />
              ) : (
                <div className="w-32 h-32 bg-gray-200 rounded-lg flex items-center justify-center">
                  <Package className="h-8 w-8 text-gray-400" />
                </div>
              )}
            </div>

            {/* Product Info */}
            <div className="flex-1">
              <CardTitle className="text-2xl mb-2">{result.product_name}</CardTitle>
              <div className="flex items-center gap-2 mb-4">
                <Badge variant={getConditionBadgeVariant(result.condition)}>
                  {result.condition}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Analyzed on {new Date(result.created_at).toLocaleDateString()}
                </span>
              </div>
              <CardDescription className="text-base">
                {analysisData.description || "AI-powered analysis complete with pricing insights and recommendations."}
              </CardDescription>
            </div>

            {/* Actions */}
            <div className="flex flex-col gap-2">
              <Button size="sm" variant="outline">
                <Share className="h-4 w-4 mr-2" />
                Share
              </Button>
              <Button size="sm" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <DollarSign className="h-5 w-5 text-green-600" />
              <div>
                <p className="text-sm text-muted-foreground">Est. Selling Price</p>
                <p className="text-xl font-bold text-green-600">
                  {formatCurrency(analysisData.estimated_price || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-600" />
              <div>
                <p className="text-sm text-muted-foreground">Profit Potential</p>
                <p className="text-xl font-bold text-blue-600">
                  {formatCurrency(analysisData.estimated_profit || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Calculator className="h-5 w-5 text-purple-600" />
              <div>
                <p className="text-sm text-muted-foreground">Total Fees</p>
                <p className="text-xl font-bold text-purple-600">
                  {formatCurrency(feeCalculations.total_fees || 0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <Package className="h-5 w-5 text-orange-600" />
              <div>
                <p className="text-sm text-muted-foreground">Demand Level</p>
                <p className="text-xl font-bold text-orange-600">
                  {analysisData.demand_level || 'Medium'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Marketplace Comparison */}
      {recommendations.marketplaces && recommendations.marketplaces.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Marketplace Comparison</CardTitle>
            <CardDescription>
              Compare potential selling opportunities across different platforms
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recommendations.marketplaces.map((marketplace: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                      <span className="font-semibold text-sm">{marketplace.name?.charAt(0) || 'M'}</span>
                    </div>
                    <div>
                      <h4 className="font-semibold">{marketplace.name || 'Marketplace'}</h4>
                      <p className="text-sm text-muted-foreground">
                        {marketplace.category || 'General marketplace'}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold">{formatCurrency(marketplace.estimated_price || 0)}</p>
                    <p className="text-sm text-muted-foreground">
                      {marketplace.commission_rate || '10'}% commission
                    </p>
                  </div>
                  <Button size="sm" variant="outline">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Pricing Insights */}
      {pricingData.similar_products && pricingData.similar_products.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Similar Products</CardTitle>
            <CardDescription>
              Pricing data from similar products to help optimize your listing
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {pricingData.similar_products.slice(0, 6).map((product: any, index: number) => (
                <Card key={index} className="border-l-4 border-l-blue-500">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      {product.image_url && (
                        <img
                          src={product.image_url}
                          alt={product.title}
                          className="w-16 h-16 object-cover rounded"
                          onError={handleImageError}
                        />
                      )}
                      <div className="flex-1">
                        <h5 className="font-medium text-sm mb-1 line-clamp-2">
                          {product.title || 'Similar Product'}
                        </h5>
                        <p className="text-lg font-bold text-green-600">
                          {formatCurrency(product.price || 0)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {product.marketplace || 'Unknown marketplace'}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Fee Breakdown */}
      {feeCalculations.breakdown && (
        <Card>
          <CardHeader>
            <CardTitle>Fee Breakdown</CardTitle>
            <CardDescription>
              Detailed breakdown of selling fees across different platforms
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(feeCalculations.breakdown).map(([platform, fees]: [string, any]) => (
                <div key={platform} className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-3 capitalize">{platform}</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground">Commission</p>
                      <p className="font-medium">{formatCurrency(fees.commission || 0)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Payment Processing</p>
                      <p className="font-medium">{formatCurrency(fees.payment_processing || 0)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Listing Fee</p>
                      <p className="font-medium">{formatCurrency(fees.listing_fee || 0)}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Total</p>
                      <p className="font-semibold text-red-600">{formatCurrency(fees.total || 0)}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Insights */}
      {analysisData.insights && (
        <Card>
          <CardHeader>
            <CardTitle>AI Insights & Recommendations</CardTitle>
            <CardDescription>
              Smart recommendations to maximize your selling potential
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none">
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-blue-800">{analysisData.insights}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}