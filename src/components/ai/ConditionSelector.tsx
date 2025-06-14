import { useState } from "react";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { Card, CardContent } from "@/components/ui/card";

export type ProductCondition =
  | "new"
  | "like_new"
  | "excellent"
  | "good"
  | "fair"
  | "poor";

interface ConditionSelectorProps {
  selectedCondition: ProductCondition;
  onConditionChange: (condition: ProductCondition) => void;
  className?: string;
}

interface ConditionOption {
  value: ProductCondition;
  label: string;
  description: string;
}

const conditionOptions: ConditionOption[] = [
  {
    value: "new",
    label: "New",
    description: "Brand new, unused, unworn, in original packaging",
  },
  {
    value: "like_new",
    label: "Like New",
    description:
      "Mint condition, no signs of wear, may not have original packaging",
  },
  {
    value: "excellent",
    label: "Excellent",
    description: "Minimal signs of wear, fully functional, no repairs needed",
  },
  {
    value: "good",
    label: "Good",
    description: "Some signs of wear, fully functional, minor cosmetic issues",
  },
  {
    value: "fair",
    label: "Fair",
    description:
      "Noticeable wear, fully functional but may have cosmetic issues",
  },
  {
    value: "poor",
    label: "Poor",
    description: "Heavy wear, may have functional issues, sold as-is",
  },
];

export default function ConditionSelector({
  selectedCondition,
  onConditionChange,
  className = "",
}: ConditionSelectorProps) {
  return (
    <Card className={className}>
      <CardContent className="pt-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Item Condition</h3>
          <p className="text-sm text-gray-500">
            Select the condition that best describes your item
          </p>

          <RadioGroup
            value={selectedCondition}
            onValueChange={(value) =>
              onConditionChange(value as ProductCondition)
            }
            className="space-y-3"
          >
            {conditionOptions.map((option) => (
              <div key={option.value} className="flex items-start space-x-2">
                <RadioGroupItem
                  value={option.value}
                  id={option.value}
                  className="mt-1"
                />
                <div className="grid gap-1">
                  <Label htmlFor={option.value} className="font-medium">
                    {option.label}
                  </Label>
                  <p className="text-sm text-gray-500">{option.description}</p>
                </div>
              </div>
            ))}
          </RadioGroup>
        </div>
      </CardContent>
    </Card>
  );
}
