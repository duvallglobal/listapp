import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Camera, History, CreditCard, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";
import TopNavigation from "../dashboard/layout/TopNavigation";
import Sidebar from "../dashboard/layout/Sidebar";
import DashboardGrid from "../dashboard/DashboardGrid";
import ActivityFeed from "../dashboard/ActivityFeed";
import TaskBoard from "../dashboard/TaskBoard";
import SubscriptionInfo from "../dashboard/SubscriptionInfo";
import AnalysisHistory from "../dashboard/AnalysisHistory";

export default function UserDashboard() {
  const [activeTab, setActiveTab] = useState("overview");

  return (
    <div className="min-h-screen bg-white">
      <TopNavigation />

      <div className="flex pt-16">
        <Sidebar activeItem="Dashboard" />

        <main className="flex-1 overflow-auto p-6">
          <div className="mb-6">
            <h1 className="text-2xl font-bold text-gray-800">
              PriceVision AI Dashboard
            </h1>
            <p className="text-gray-600">
              Welcome to your AI-powered price intelligence platform
            </p>
          </div>

          <Tabs
            value={activeTab}
            onValueChange={setActiveTab}
            className="w-full"
          >
            <TabsList className="grid w-full max-w-md grid-cols-3 mb-6">
              <TabsTrigger value="overview" className="text-sm">
                Overview
              </TabsTrigger>
              <TabsTrigger value="analysis" className="text-sm">
                Recent Analyses
              </TabsTrigger>
              <TabsTrigger value="subscription" className="text-sm">
                Subscription
              </TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2">
                  <Card>
                    <CardHeader>
                      <CardTitle>Quick Actions</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <Link to="/analysis">
                          <Button
                            className="w-full h-auto py-6 flex flex-col items-center justify-center gap-2"
                            variant="outline"
                          >
                            <Camera className="h-8 w-8 text-primary" />
                            <div className="text-center">
                              <h3 className="font-medium">New Analysis</h3>
                              <p className="text-xs text-gray-500">
                                Analyze product photos
                              </p>
                            </div>
                          </Button>
                        </Link>

                        <Link to="/analysis?tab=history">
                          <Button
                            className="w-full h-auto py-6 flex flex-col items-center justify-center gap-2"
                            variant="outline"
                          >
                            <History className="h-8 w-8 text-primary" />
                            <div className="text-center">
                              <h3 className="font-medium">Analysis History</h3>
                              <p className="text-xs text-gray-500">
                                View past analyses
                              </p>
                            </div>
                          </Button>
                        </Link>
                      </div>
                    </CardContent>
                  </Card>

                  <div className="mt-6">
                    <Card>
                      <CardHeader>
                        <CardTitle>Recent Analyses</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <DashboardGrid />
                      </CardContent>
                    </Card>
                  </div>
                </div>

                <div className="md:col-span-1">
                  <SubscriptionInfo
                    onUpgrade={() => setActiveTab("subscription")}
                  />

                  <Card className="mt-6">
                    <CardHeader>
                      <CardTitle>Recent Activity</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <ActivityFeed
                        activities={[
                          {
                            id: "1",
                            type: "update",
                            user: {
                              name: "System",
                              avatar:
                                "https://api.dicebear.com/7.x/avataaars/svg?seed=System",
                            },
                            content: "Analyzed Vintage Leather Jacket",
                            timestamp: "5m ago",
                          },
                          {
                            id: "2",
                            type: "comment",
                            user: {
                              name: "You",
                              avatar:
                                "https://api.dicebear.com/7.x/avataaars/svg?seed=You",
                            },
                            content: "Saved analysis to history",
                            timestamp: "15m ago",
                          },
                          {
                            id: "3",
                            type: "commit",
                            user: {
                              name: "System",
                              avatar:
                                "https://api.dicebear.com/7.x/avataaars/svg?seed=System",
                            },
                            content: "Subscription renewed",
                            timestamp: "1d ago",
                          },
                        ]}
                      />
                    </CardContent>
                  </Card>
                </div>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>Getting Started</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-lg">
                      <div className="h-8 w-8 bg-blue-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        1
                      </div>
                      <div>
                        <h4 className="font-medium">Upload Product Photos</h4>
                        <p className="text-sm text-gray-600">
                          Take clear photos of items you want to analyze
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-green-50 rounded-lg">
                      <div className="h-8 w-8 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        2
                      </div>
                      <div>
                        <h4 className="font-medium">Get AI Analysis</h4>
                        <p className="text-sm text-gray-600">
                          Our AI identifies products and estimates market value
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 p-4 bg-purple-50 rounded-lg">
                      <div className="h-8 w-8 bg-purple-500 text-white rounded-full flex items-center justify-center text-sm font-medium">
                        3
                      </div>
                      <div>
                        <h4 className="font-medium">List & Sell</h4>
                        <p className="text-sm text-gray-600">
                          Use generated titles and descriptions to list on
                          recommended platforms
                        </p>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analysis">
              <AnalysisHistory />
            </TabsContent>

            <TabsContent value="subscription">
              <div className="max-w-3xl mx-auto">
                <SubscriptionInfo />

                <div className="mt-6 text-center">
                  <Link to="/subscription">
                    <Button className="gap-2">
                      Manage Subscription
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}
