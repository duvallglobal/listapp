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
import { Separator } from "@/components/ui/separator";
import { CheckCircle2, Loader2, CreditCard } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { supabase } from "../../../supabase/supabase";
import { useAuth } from "../../../supabase/auth";
import TopNavigation from "../dashboard/layout/TopNavigation";
import Sidebar from "../dashboard/layout/Sidebar";
import SubscriptionInfo from "../dashboard/SubscriptionInfo";

interface Plan {
  id: string;
  object: string;
  active: boolean;
  amount: number;
  currency: string;
  interval: string;
  interval_count: number;
  product: string;
  created: number;
  livemode: boolean;
}

export default function SubscriptionPage() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [plans, setPlans] = useState<Plan[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingPlanId, setProcessingPlanId] = useState<string | null>(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    setLoading(true);
    try {
      const { data, error } = await supabase.functions.invoke(
        "supabase-functions-get-plans",
      );

      if (error) throw error;
      setPlans(data || []);
    } catch (error) {
      console.error("Failed to fetch plans:", error);
      toast({
        title: "Error loading plans",
        description: "There was a problem loading subscription plans.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCheckout = async (priceId: string) => {
    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please sign in to subscribe to a plan.",
        variant: "destructive",
      });
      return;
    }

    setProcessingPlanId(priceId);
    try {
      const { data, error } = await supabase.functions.invoke(
        "supabase-functions-create-checkout",
        {
          body: {
            price_id: priceId,
            user_id: user.id,
            return_url: `${window.location.origin}/dashboard`,
          },
          headers: {
            "X-Customer-Email": user.email || "",
          },
        },
      );

      if (error) throw error;

      if (data?.url) {
        toast({
          title: "Redirecting to checkout",
          description: "You'll be redirected to complete your purchase.",
        });
        window.location.href = data.url;
      } else {
        throw new Error("No checkout URL returned");
      }
    } catch (error) {
      console.error("Error creating checkout session:", error);
      toast({
        title: "Checkout failed",
        description: "There was an error creating your checkout session.",
        variant: "destructive",
      });
    } finally {
      setProcessingPlanId(null);
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: currency.toUpperCase(),
      minimumFractionDigits: 2,
    }).format(amount / 100);
  };

  const getPlanFeatures = (planType: string) => {
    const basicFeatures = [
      "20 analyses per month",
      "Basic price estimation",
      "Standard marketplace recommendations",
      "Email support",
    ];

    const proFeatures = [
      "50 analyses per month",
      "Advanced price estimation with trends",
      "Priority marketplace recommendations",
      "Automated listing generation",
      "Analytics dashboard",
      "Priority support",
    ];

    const businessFeatures = [
      "100 analyses per month",
      "Advanced price estimation with trends",
      "Custom marketplace integrations",
      "Bulk processing capabilities",
      "Advanced analytics & reporting",
      "Priority support",
    ];

    const enterpriseFeatures = [
      "Unlimited analyses",
      "Real-time market data integration",
      "Custom marketplace integrations",
      "Bulk processing capabilities",
      "Advanced analytics & reporting",
      "Dedicated account manager",
      "API access",
    ];

    if (planType.includes("enterprise")) return enterpriseFeatures;
    if (planType.includes("business")) return businessFeatures;
    if (planType.includes("pro")) return proFeatures;
    return basicFeatures;
  };

  return (
    <div className="min-h-screen bg-white">
      <TopNavigation />

      <div className="flex pt-16">
        <Sidebar activeItem="Settings" />

        <main className="flex-1 overflow-auto p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-800">
              Subscription Management
            </h1>
            <p className="text-gray-600">
              Manage your subscription and billing information
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <SubscriptionInfo />
            </div>

            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-xl flex items-center gap-2">
                    <CreditCard className="h-5 w-5" />
                    Available Plans
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {loading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin h-8 w-8 border-4 border-primary border-t-transparent rounded-full mx-auto mb-4"></div>
                      <p className="text-gray-500">
                        Loading subscription plans...
                      </p>
                    </div>
                  ) : plans.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-gray-500">
                        No subscription plans available.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {plans.map((plan) => (
                        <Card
                          key={plan.id}
                          className="border-2 hover:border-primary transition-colors"
                        >
                          <CardHeader className="pb-2">
                            <div className="flex justify-between items-start">
                              <div>
                                <Badge className="mb-2">
                                  {plan.interval_count === 1
                                    ? "Monthly"
                                    : `${plan.interval_count} ${plan.interval}s`}
                                </Badge>
                                <CardTitle>
                                  {plan.product.includes("basic")
                                    ? "Basic"
                                    : plan.product.includes("pro")
                                      ? "Pro"
                                      : plan.product.includes("business")
                                        ? "Business"
                                        : "Enterprise"}
                                </CardTitle>
                              </div>
                              <div className="text-right">
                                <span className="text-2xl font-bold">
                                  {formatCurrency(plan.amount, plan.currency)}
                                </span>
                                <span className="text-gray-500">
                                  /{plan.interval}
                                </span>
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <Separator className="my-4" />
                            <ul className="space-y-2">
                              {getPlanFeatures(plan.product).map(
                                (feature, index) => (
                                  <li
                                    key={index}
                                    className="flex items-start gap-2"
                                  >
                                    <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                                    <span>{feature}</span>
                                  </li>
                                ),
                              )}
                            </ul>
                          </CardContent>
                          <CardFooter>
                            <Button
                              className="w-full"
                              onClick={() => handleCheckout(plan.id)}
                              disabled={processingPlanId === plan.id}
                            >
                              {processingPlanId === plan.id ? (
                                <>
                                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                  Processing...
                                </>
                              ) : (
                                "Subscribe"
                              )}
                            </Button>
                          </CardFooter>
                        </Card>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
