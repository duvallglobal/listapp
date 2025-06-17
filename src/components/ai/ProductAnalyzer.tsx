import React, { useState, useCallback } from 'react';
import { Upload, Camera, AlertCircle, CheckCircle, Loader2, X, Plus } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useToast } from '@/components/ui/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import ImageUploader from './ImageUploader';
import ConditionSelector from './ConditionSelector';
import AnalysisLoading from './AnalysisLoading';
import AnalysisResult from './AnalysisResult';
import { analysisService, AnalysisRequest, AnalysisResult as AnalysisResultType } from '@/services/analysisService';

export default function ProductAnalyzer() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [condition, setCondition] = useState<string>('');
  const [estimatedCost, setEstimatedCost] = useState<string>('');
  const [notes, setNotes] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResultType | null>(null);
  const [analysisId, setAnalysisId] = useState<string>('');
  const [error, setError] = useState<string>('');
  const [progress, setProgress] = useState(0);

  const { user } = useAuth();
  const { toast } = useToast();

  const handleFileSelect = useCallback((file: File) => {
    if (selectedFiles.length >= 5) {
      toast({
        title: "Maximum files reached",
        description: "You can upload up to 5 images per analysis.",
        variant: "destructive"
      });
      return;
    }

    // Check if file already exists
    if (selectedFiles.some(f => f.name === file.name && f.size === file.size)) {
      toast({
        title: "Duplicate file",
        description: "This image has already been selected.",
        variant: "destructive"
      });
      return;
    }

    setSelectedFiles(prev => [...prev, file]);
    setError('');
  }, [selectedFiles, toast]);

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleAnalyze = async () => {
    if (selectedFiles.length === 0 || !condition || !user) {
      setError('Please select at least one image and condition before analyzing.');
      return;
    }

    setIsAnalyzing(true);
    setError('');
    setProgress(0);

    try {
      // Start progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 10;
        });
      }, 800);

      // Submit analysis request (using first file for now)
      const request: AnalysisRequest = {
        imageFile: selectedFiles[0],
        condition,
        estimatedCost: estimatedCost ? parseFloat(estimatedCost) : undefined,
        notes: notes || undefined
      };

      const submittedAnalysisId = await analysisService.submitAnalysis(request, user.id);
      setAnalysisId(submittedAnalysisId);

      // Poll for results
      const pollInterval = setInterval(async () => {
        try {
          const result = await analysisService.getAnalysis(submittedAnalysisId);

          if (result && (result.status === 'completed' || result.status === 'failed')) {
            clearInterval(pollInterval);
            clearInterval(progressInterval);
            setProgress(100);
            setAnalysisResult(result);
            setIsAnalyzing(false);

            if (result.status === 'failed') {
              setError(result.error || 'Analysis failed');
            } else {
              toast({
                title: "Analysis complete!",
                description: "Your product has been successfully analyzed."
              });
            }
          }
        } catch (pollError) {
          console.error('Polling error:', pollError);
        }
      }, 2000);

      // Cleanup after 5 minutes
      setTimeout(() => {
        clearInterval(progressInterval);
        clearInterval(pollInterval);
        if (isAnalyzing) {
          setError('Analysis timed out. Please try again.');
          setIsAnalyzing(false);
          setProgress(0);
        }
      }, 300000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Analysis failed');
      setIsAnalyzing(false);
      setProgress(0);
      toast({
        title: "Analysis failed",
        description: err instanceof Error ? err.message : 'Unknown error occurred',
        variant: "destructive"
      });
    }
  };

  const handleSaveAnalysis = async (data: AnalysisResultType) => {
    try {
      await analysisService.saveAnalysisToFavorites(data.id);
      toast({
        title: "Analysis saved",
        description: "Analysis has been saved to your favorites."
      });
    } catch (error) {
      toast({
        title: "Save failed",
        description: "Failed to save analysis to favorites.",
        variant: "destructive"
      });
    }
  };

  const handleReset = () => {
    setSelectedFiles([]);
    setCondition('');
    setEstimatedCost('');
    setNotes('');
    setAnalysisResult(null);
    setAnalysisId('');
    setError('');
    setProgress(0);
    setIsAnalyzing(false);
  };

  if (analysisResult) {
    return (
      <div className="w-full max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Analysis Results</h2>
          <Button onClick={handleReset} variant="outline">
            <Plus className="h-4 w-4 mr-2" />
            Analyze Another
          </Button>
        </div>
        <AnalysisResult 
          analysisId={analysisId}
          data={analysisResult}
          onSave={handleSaveAnalysis}
        />
      </div>
    );
  }

  if (isAnalyzing) {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <AnalysisLoading progress={progress} />
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Camera className="h-6 w-6" />
            <span>Product Analysis</span>
          </CardTitle>
          <CardDescription>
            Upload photos of your product and get AI-powered pricing and marketplace recommendations.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Image Upload Section */}
          <div className="space-y-3">
            <Label className="text-base font-medium">
              Product Images {selectedFiles.length > 0 && `(${selectedFiles.length}/5)`}
            </Label>
            <ImageUploader onFileSelect={handleFileSelect} />

            {/* Selected Files Display */}
            {selectedFiles.length > 0 && (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={URL.createObjectURL(file)}
                      alt={`Selected ${index + 1}`}
                      className="w-full h-24 object-cover rounded-lg border"
                    />
                    <Button
                      size="sm"
                      variant="destructive"
                      className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => removeFile(index)}
                    >
                      <X className="h-3 w-3" />
                    </Button>
                    <div className="absolute bottom-1 left-1">
                      <Badge variant="secondary" className="text-xs">
                        {index === 0 ? 'Main' : `${index + 1}`}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {selectedFiles.length > 0 && (
              <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span>{selectedFiles.length} image{selectedFiles.length > 1 ? 's' : ''} selected</span>
              </div>
            )}
          </div>

          {/* Condition Selection */}
          <div className="space-y-3">
            <Label className="text-base font-medium">Product Condition</Label>
            <ConditionSelector onConditionSelect={setCondition} />
          </div>

          {/* Optional Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <Label htmlFor="estimated-cost">Purchase Price (Optional)</Label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground">$</span>
                <Input
                  id="estimated-cost"
                  type="number"
                  placeholder="0.00"
                  value={estimatedCost}
                  onChange={(e) => setEstimatedCost(e.target.value)}
                  className="pl-8"
                  step="0.01"
                  min="0"
                />
              </div>
              <p className="text-xs text-muted-foreground">
                What you paid for this item (helps with profit calculations)
              </p>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes">Additional Notes (Optional)</Label>
            <Textarea
              id="notes"
              placeholder="Brand, model, special features, defects, etc..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
            />
            <p className="text-xs text-muted-foreground">
              Include any details that might help with the analysis
            </p>
          </div>

          {/* Analysis Button */}
          <div className="flex justify-center pt-4">
            <Button
              onClick={handleAnalyze}
              disabled={selectedFiles.length === 0 || !condition || isAnalyzing || !user}
              size="lg"
              className="min-w-[200px]"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Camera className="h-4 w-4 mr-2" />
                  Analyze Product
                </>
              )}
            </Button>
          </div>

          {!user && (
            <Alert>
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                Please sign in to analyze products and save your results.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>
    </div>
  );
}