import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { CreditCard, Zap, Calendar, AlertCircle } from "lucide-react";
import { supabase } from "../../../supabase/supabase";
import { useAuth } from "../../../supabase/auth";
import { format } from "date-fns";
import { useToast } from "@/components/ui/use-toast";

interface SubscriptionData {
  id: string;
  status: string;
  current_period_end: number;
  cancel_at_period_end: boolean;
  price_id: string;
  interval: string;
  amount: number;
  currency: string;
}

interface UserData {
  credits: string;
  subscription: string | null;
}

interface SubscriptionInfoProps {
  onUpgrade?: () => void;
  className?: string;
}

export default function SubscriptionInfo({
  onUpgrade,
  className = "",
}: SubscriptionInfoProps) {
  const { user } = useAuth();
  const { toast } = useToast();
  const [subscription, setSubscription] = useState<SubscriptionData | null>(
    null,
  );
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user) {
      fetchSubscriptionData();
    }
  }, [user]);

  const fetchSubscriptionData = async () => {
    if (!user) return;

    setLoading(true);
    try {
      // Fetch user data
      const { data: userData, error: userError } = await supabase
        .from("users")
        .select("credits, subscription")
        .eq("user_id", user.id)
        .single();

      if (userError) throw userError;
      setUserData(userData);

      // If user has a subscription, fetch its details
      if (userData.subscription) {
        const { data: subData, error: subError } = await supabase
          .from("subscriptions")
          .select("*")
          .eq("id", userData.subscription)
          .single();

        if (subError) throw subError;
        setSubscription(subData);
      }
    } catch (error) {
      console.error("Error fetching subscription data:", error);
      toast({
        title: "Error loading subscription",
        description:
          "There was a problem loading your subscription information.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleManageSubscription = async () => {
    if (!user) return;

    try {
      // In a real implementation, this would redirect to a customer portal
      // For now, we'll just show a toast
      toast({
        title: "Subscription management",
        description: "You would be redirected to manage your subscription.",
      });
    } catch (error) {
      console.error("Error managing subscription:", error);
      toast({
        title: "Error",
        description: "There was a problem accessing subscription management.",
        variant: "destructive",
      });
    }
  };

  const getPlanName = (priceId: string): string => {
    // In a real implementation, this would map price IDs to plan names
    const planMap: Record<string, string> = {
      price_basic: "Basic Plan",
      price_pro: "Pro Plan",
      price_business: "Business Plan",
      price_enterprise: "Enterprise Plan",
    };

    return planMap[priceId] || "Free Trial";
  };

  const getCreditsInfo = () => {
    if (!userData) return { current: 0, total: 2, percent: 0 };

    const current = parseInt(userData.credits || "0");
    let total = 2; // Default for free trial

    if (subscription) {
      // Set total based on plan
      if (subscription.price_id.includes("basic")) total = 20;
      else if (subscription.price_id.includes("pro")) total = 50;
      else if (subscription.price_id.includes("business")) total = 100;
      else if (subscription.price_id.includes("enterprise")) total = 999; // Unlimited
    }

    const percent = Math.min(100, Math.max(0, (current / total) * 100));

    return { current, total, percent };
  };

  const formatCurrency = (amount: number, currency: string = "usd") => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency.toUpperCase(),
    }).format(amount / 100);
  };

  const creditsInfo = getCreditsInfo();

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="text-xl flex items-center gap-2">
          <CreditCard className="h-5 w-5" />
          Subscription
        </CardTitle>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="text-center py-4">
            <div className="animate-spin h-6 w-6 border-4 border-primary border-t-transparent rounded-full mx-auto mb-2"></div>
            <p className="text-gray-500">Loading subscription data...</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="font-medium text-lg">
                  {subscription
                    ? getPlanName(subscription.price_id)
                    : "Free Trial"}
                </h3>
                {subscription && (
                  <p className="text-sm text-gray-500">
                    {formatCurrency(subscription.amount, subscription.currency)}
                    /{subscription.interval}
                  </p>
                )}
              </div>
              <Badge
                variant={
                  subscription?.status === "active" ? "default" : "outline"
                }
                className={
                  subscription?.status === "active" ? "bg-green-500" : ""
                }
              >
                {subscription?.status === "active" ? "Active" : "Free Trial"}
              </Badge>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <h4 className="text-sm font-medium flex items-center gap-1">
                  <Zap className="h-4 w-4" />
                  Analysis Credits
                </h4>
                <span className="text-sm">
                  {creditsInfo.current} /{" "}
                  {creditsInfo.total === 999 ? "∞" : creditsInfo.total}
                </span>
              </div>
              <Progress value={creditsInfo.percent} className="h-2" />
            </div>

            {subscription && (
              <div className="bg-gray-50 p-4 rounded-lg space-y-3">
                <div className="flex items-center gap-1 text-sm">
                  <Calendar className="h-4 w-4 text-gray-500" />
                  <span className="text-gray-700">
                    Renews on{" "}
                    {format(
                      new Date(subscription.current_period_end * 1000),
                      "MMMM d, yyyy",
                    )}
                  </span>
                </div>

                {subscription.cancel_at_period_end && (
                  <div className="flex items-start gap-2 text-sm bg-amber-50 p-2 rounded border border-amber-200">
                    <AlertCircle className="h-4 w-4 text-amber-500 mt-0.5" />
                    <span>
                      Your subscription will end on{" "}
                      {format(
                        new Date(subscription.current_period_end * 1000),
                        "MMMM d, yyyy",
                      )}
                      .
                    </span>
                  </div>
                )}
              </div>
            )}

            <Separator />

            <div className="space-y-2">
              <h4 className="font-medium">Plan Features</h4>
              <ul className="space-y-1 text-sm">
                {subscription ? (
                  subscription.price_id.includes("enterprise") ? (
                    <>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Unlimited analyses per month
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Advanced market data integration
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Bulk processing capabilities
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Dedicated account manager
                      </li>
                    </>
                  ) : subscription.price_id.includes("business") ? (
                    <>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        100 analyses per month
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Advanced price estimation with trends
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Custom marketplace integrations
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Priority support
                      </li>
                    </>
                  ) : subscription.price_id.includes("pro") ? (
                    <>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        50 analyses per month
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Advanced price estimation
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Priority marketplace recommendations
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Email support
                      </li>
                    </>
                  ) : (
                    <>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        20 analyses per month
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Basic price estimation
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Standard marketplace recommendations
                      </li>
                      <li className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                        Email support
                      </li>
                    </>
                  )
                ) : (
                  <>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                      2 free analyses
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                      Basic price estimation
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary"></span>
                      Standard marketplace recommendations
                    </li>
                  </>
                )}
              </ul>
            </div>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between">
        {subscription ? (
          <Button
            variant="outline"
            onClick={handleManageSubscription}
            className="w-full"
          >
            Manage Subscription
          </Button>
        ) : (
          <Button onClick={onUpgrade} className="w-full">
            Upgrade Now
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}
