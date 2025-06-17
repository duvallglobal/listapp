import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { AlertCircle, CheckCircle, Clock, DollarSign, TrendingUp, Camera, MapPin, Star, Package, Zap, Copy, Download, Share2, Heart } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';

interface AnalysisData {
  id: string;
  status: 'pending' | 'analyzing' | 'completed' | 'error';
  productName?: string;
  brand?: string;
  category?: string;
  condition?: string;
  estimatedValue?: {
    low: number;
    median: number;
    high: number;
  };
  marketplaceRecommendations?: Array<{
    platform: string;
    suitability: number;
    reasoning: string;
    estimatedProfit: number;
    fees: number;
  }>;
  confidenceScore?: number;
  generatedTitle?: string;
  description?: string;
  tags?: string[];
  imageUrl?: string;
  error?: string;
  createdAt?: string;
  analysisVersion?: string;
}

interface AnalysisResultProps {
  analysisId: string;
  data?: AnalysisData;
  onRetry?: () => void;
  onSave?: (data: AnalysisData) => void;
}

const AnalysisResult: React.FC<AnalysisResultProps> = ({ analysisId, data, onRetry, onSave }) => {
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const { toast } = useToast();

  const handleSaveAnalysis = async () => {
    if (!data || !onSave) return;

    setIsSaving(true);
    try {
      await onSave(data);
      setIsSaved(true);
      toast({ title: "Analysis saved successfully!" });
    } catch (error) {
      toast({ title: "Failed to save analysis", variant: "destructive" });
    } finally {
      setIsSaving(false);
    }
  };

  const copyToClipboard = (text: string, message: string) => {
    navigator.clipboard.writeText(text);
    toast({ title: message });
  };

  if (!data) {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="flex items-center justify-center space-x-2">
            <Clock className="h-5 w-5 animate-spin" />
            <span>Loading analysis...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (data.status === 'error') {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Analysis failed: {data.error || 'Unknown error occurred'}
              {onRetry && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={onRetry}
                  className="ml-2"
                >
                  Retry
                </Button>
              )}
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  if (data.status === 'analyzing' || data.status === 'pending') {
    return (
      <Card className="w-full max-w-4xl mx-auto">
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 animate-spin" />
              <span className="font-medium">Analyzing your product...</span>
            </div>
            <Progress value={data.status === 'analyzing' ? 75 : 25} className="w-full" />
            <p className="text-sm text-muted-foreground">
              This may take a few moments while our AI examines your product.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Header with Product Info */}
      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div className="space-y-2">
              <CardTitle className="text-2xl">{data.productName || 'Product Analysis'}</CardTitle>
              <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                {data.brand && (
                  <Badge variant="secondary">{data.brand}</Badge>
                )}
                {data.category && (
                  <Badge variant="outline">{data.category}</Badge>
                )}
                {data.condition && (
                  <Badge variant="outline">Condition: {data.condition}</Badge>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-2">
              {data.confidenceScore && (
                <Badge variant={data.confidenceScore > 0.8 ? 'default' : 'secondary'}>
                  {Math.round(data.confidenceScore * 100)}% Confidence
                </Badge>
              )}
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
          </div>
        </CardHeader>
        {data.imageUrl && (
          <CardContent>
            <div className="flex justify-center">
              <img 
                src={data.imageUrl} 
                alt={data.productName}
                className="max-h-64 rounded-lg object-contain border"
              />
            </div>
          </CardContent>
        )}
      </Card>

      {/* Main Analysis Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Price Estimates */}
        {data.estimatedValue && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <DollarSign className="h-5 w-5" />
                <span>Price Estimates</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm">Low</span>
                  <span className="font-medium">${data.estimatedValue.low}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">Median</span>
                  <span className="font-bold text-lg">${data.estimatedValue.median}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm">High</span>
                  <span className="font-medium">${data.estimatedValue.high}</span>
                </div>
              </div>
              <Separator />
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Recommended Price</p>
                <p className="text-2xl font-bold text-primary">${data.estimatedValue.median}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Top Recommendation */}
        {data.marketplaceRecommendations && data.marketplaceRecommendations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <TrendingUp className="h-5 w-5" />
                <span>Best Platform</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="text-center">
                  <h3 className="font-bold text-lg">{data.marketplaceRecommendations[0].platform}</h3>
                  <div className="flex items-center justify-center space-x-1">
                    {[...Array(5)].map((_, i) => (
                      <Star 
                        key={i} 
                        className={`h-4 w-4 ${
                          i < Math.round(data.marketplaceRecommendations![0].suitability / 2) 
                            ? 'fill-yellow-400 text-yellow-400' 
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                    <span className="ml-2 text-sm">({data.marketplaceRecommendations[0].suitability}/10)</span>
                  </div>
                </div>
                <Separator />
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm">Est. Profit</span>
                    <span className="font-medium text-green-600">
                      ${data.marketplaceRecommendations[0].estimatedProfit}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Platform Fees</span>
                    <span className="text-sm text-muted-foreground">
                      ${data.marketplaceRecommendations[0].fees || 0}
                    </span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground">
                  {data.marketplaceRecommendations[0].reasoning}
                </p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Quick Stats */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Package className="h-5 w-5" />
              <span>Quick Stats</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Analysis ID</p>
                <p className="font-mono text-xs">{analysisId.slice(0, 8)}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Platforms</p>
                <p className="font-medium">{data.marketplaceRecommendations?.length || 0}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Tags</p>
                <p className="font-medium">{data.tags?.length || 0}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Status</p>
                <Badge variant="default" className="text-xs">Completed</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Analysis Tabs */}
      <Card>
        <Tabs defaultValue="recommendations" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="recommendations">Platform Recommendations</TabsTrigger>
            <TabsTrigger value="listing">Listing Content</TabsTrigger>
            <TabsTrigger value="details">Analysis Details</TabsTrigger>
          </TabsList>

          <TabsContent value="recommendations" className="p-6">
            <div className="space-y-4">
              <h3 className="font-semibold">All Platform Recommendations</h3>
              <div className="grid gap-4">
                {data.marketplaceRecommendations?.map((rec, index) => (
                  <Card key={index} className="p-4">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">{rec.platform}</h4>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline">{rec.suitability}/10</Badge>
                        <span className="text-sm font-medium text-green-600">
                          ${rec.estimatedProfit} profit
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{rec.reasoning}</p>
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Platform fees: ${rec.fees || 0}</span>
                      <span>Suitability: {rec.suitability * 10}%</span>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="listing" className="p-6">
            <div className="space-y-6">
              {data.generatedTitle && (
                <div>
                  <h3 className="font-semibold mb-2">Optimized Title</h3>
                  <div className="flex items-center space-x-2">
                    <p className="flex-1 p-3 bg-muted rounded-lg">{data.generatedTitle}</p>
                    <Button size="sm" variant="outline" onClick={() => {
                      copyToClipboard(data.generatedTitle!, "Title copied to clipboard");
                    }}>
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}

              {data.description && (
                <div>
                  <h3 className="font-semibold mb-2">Product Description</h3>
                  <div className="flex space-x-2">
                    <div className="flex-1 p-3 bg-muted rounded-lg">
                      <p className="whitespace-pre-wrap">{data.description}</p>
                    </div>
                    <Button size="sm" variant="outline" onClick={() => {
                      copyToClipboard(data.description!, "Description copied to clipboard");
                    }}>
                      <Copy className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              )}

              {data.tags && data.tags.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Suggested Tags</h3>
                  <div className="flex flex-wrap gap-2">
                    {data.tags.map((tag, index) => (
                      <Badge key={index} variant="secondary">{tag}</Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </TabsContent>

          <TabsContent value="details" className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Product Information</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Name:</span>
                    <span>{data.productName || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Brand:</span>
                    <span>{data.brand || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Category:</span>
                    <span>{data.category || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Condition:</span>
                    <span>{data.condition || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Confidence:</span>
                    <span>{data.confidenceScore ? `${Math.round(data.confidenceScore * 100)}%` : 'N/A'}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="font-semibold mb-3">Analysis Metadata</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Analysis ID:</span>
                    <span className="font-mono text-xs">{analysisId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Created:</span>
                    <span>{data.createdAt ? new Date(data.createdAt).toLocaleDateString() : 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Version:</span>
                    <span>{data.analysisVersion || '1.0'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Status:</span>
                    <Badge variant="default">Completed</Badge>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </Card>

      {/* Action Buttons */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-3 justify-center">
            <Button 
              onClick={handleSaveAnalysis}
              disabled={isSaving || isSaved}
              className="flex items-center space-x-2"
            >
              <Heart className="h-4 w-4" />
              <span>{isSaved ? 'Saved' : isSaving ? 'Saving...' : 'Save Analysis'}</span>
            </Button>

            <Button variant="outline" onClick={() => {
              const analysisText = `Analysis Results for ${data.productName}\n\nPrice Range: $${data.estimatedValue?.low} - $${data.estimatedValue?.high}\nRecommended Price: $${data.estimatedValue?.median}\nBest Platform: ${data.marketplaceRecommendations?.[0]?.platform}\nConfidence: ${Math.round((data.confidenceScore || 0) * 100)}%`;
              copyToClipboard(analysisText, "Analysis copied to clipboard");
            }}>
              <Copy className="h-4 w-4 mr-2" />
              Copy Results
            </Button>

            <Button variant="outline">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>

            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AnalysisResult;