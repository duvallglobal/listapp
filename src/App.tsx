import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { ErrorBoundary } from "@/components/ui/error-boundary";
import { useState } from "react";

// Layout Components
import Sidebar from "@/components/dashboard/layout/Sidebar";
import TopNavigation from "@/components/dashboard/layout/TopNavigation";

// Pages
import HomePage from "@/components/pages/home";
import DashboardPage from "@/components/pages/dashboard";
import SubscriptionPage from "@/components/pages/subscription";
import ProductAnalyzer from "@/components/ai/ProductAnalyzer";
import AnalysisHistory from "@/components/dashboard/AnalysisHistory";

// Auth Components
import AuthLayout from "@/components/auth/AuthLayout";
import LoginForm from "@/components/auth/LoginForm";
import SignUpForm from "@/components/auth/SignUpForm";

// Protected Route Wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }

  return <>{children}</>;
}

// Dashboard Layout Wrapper
function DashboardLayout({ children }: { children: React.ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  return (
    <div className="flex h-screen bg-background">
      <Sidebar 
        collapsed={sidebarCollapsed} 
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)} 
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <TopNavigation />
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  );
}

function AppRoutes() {
  const { user } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={user ? <Navigate to="/dashboard" replace /> : <HomePage />} />
      <Route path="/auth" element={<AuthLayout />}>
        <Route path="login" element={<LoginForm />} />
        <Route path="signup" element={<SignUpForm />} />
      </Route>

      {/* Protected Dashboard Routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardLayout>
            <DashboardPage />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/analyze" element={
        <ProtectedRoute>
          <DashboardLayout>
            <ProductAnalyzer />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/history" element={
        <ProtectedRoute>
          <DashboardLayout>
            <AnalysisHistory />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/subscription" element={
        <ProtectedRoute>
          <DashboardLayout>
            <SubscriptionPage />
          </DashboardLayout>
        </ProtectedRoute>
      } />

      {/* Placeholder routes for new features */}
      <Route path="/analytics" element={
        <ProtectedRoute>
          <DashboardLayout>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Analytics Dashboard</h2>
              <p className="text-muted-foreground">Coming soon...</p>
            </div>
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/profile" element={
        <ProtectedRoute>
          <DashboardLayout>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Profile Management</h2>
              <p className="text-muted-foreground">Coming soon...</p>
            </div>
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/notifications" element={
        <ProtectedRoute>
          <DashboardLayout>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Notifications</h2>
              <p className="text-muted-foreground">Coming soon...</p>
            </div>
          </DashboardLayout>
        </ProtectedRoute>
      } />

      <Route path="/settings" element={
        <ProtectedRoute>
          <DashboardLayout>
            <div className="text-center py-12">
              <h2 className="text-2xl font-bold mb-4">Settings</h2>
              <p className="text-muted-foreground">Coming soon...</p>
            </div>
          </DashboardLayout>
        </ProtectedRoute>
      } />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="min-h-screen bg-background">
            <AppRoutes />
            <Toaster />
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;