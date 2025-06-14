import { Loader2 } from "lucide-react";
import { Progress } from "@/components/ui/progress";

interface AnalysisLoadingProps {
  stage: number;
  className?: string;
}

export default function AnalysisLoading({
  stage = 1,
  className = "",
}: AnalysisLoadingProps) {
  const stages = [
    {
      title: "Processing Images",
      description: "Analyzing your product photos...",
    },
    {
      title: "Identifying Product",
      description: "Detecting brand, type, and features...",
    },
    {
      title: "Researching Market Data",
      description: "Finding comparable items and pricing...",
    },
    {
      title: "Calculating Optimal Price",
      description: "Determining the best price range...",
    },
    {
      title: "Analyzing Marketplaces",
      description: "Finding the most profitable platform...",
    },
    {
      title: "Generating Listing Content",
      description: "Creating optimized title and description...",
    },
    {
      title: "Finalizing Results",
      description: "Putting everything together...",
    },
  ];

  const currentStage = stages[Math.min(stage - 1, stages.length - 1)];
  const progressValue = (stage / stages.length) * 100;

  return (
    <div
      className={`flex flex-col items-center justify-center p-8 ${className}`}
    >
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <h2 className="text-2xl font-bold">{currentStage.title}</h2>
          <p className="text-gray-500 mt-2">{currentStage.description}</p>
        </div>

        <div className="space-y-2">
          <Progress value={progressValue} className="h-2" />
          <p className="text-sm text-gray-500 text-center">
            Step {stage} of {stages.length}
          </p>
        </div>

        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
          <h3 className="text-sm font-medium mb-2">While you wait...</h3>
          <p className="text-sm text-gray-600">
            Our AI is analyzing multiple data points to provide you with the
            most accurate pricing and marketplace recommendations. This
            typically takes 15-30 seconds.
          </p>
        </div>
      </div>
    </div>
  );
}
