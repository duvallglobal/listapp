
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { ErrorBoundary } from "@/components/ui/error-boundary";

// Auth components
import AuthLayout from "@/components/auth/AuthLayout";
import LoginForm from "@/components/auth/LoginForm";
import SignUpForm from "@/components/auth/SignUpForm";

// Dashboard components  
import { TopNavigation } from "@/components/dashboard/layout/TopNavigation";

// Page components
import HomePage from "@/components/pages/home";
import DashboardPage from "@/components/pages/dashboard";
import AnalysisPage from "@/components/pages/analysis";
import SubscriptionPage from "@/components/pages/subscription";
import SuccessPage from "@/components/pages/success";

// Loading component
function LoadingScreen() {
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading, connectionStatus } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="flex h-screen">
      <aside className="w-64 border-r bg-background">
        <ErrorBoundary fallback={
          <div className="p-4 text-center">
            <p className="text-sm text-muted-foreground">Navigation unavailable</p>
          </div>
        }>
          <TopNavigation user={user} />
        </ErrorBoundary>
      </aside>
      <main className="flex-1 overflow-auto">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </main>
    </div>
  );
}

// Public route wrapper
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingScreen />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/" element={
        <PublicRoute>
          <HomePage />
        </PublicRoute>
      } />
      
      <Route path="/login" element={
        <PublicRoute>
          <AuthLayout>
            <LoginForm />
          </AuthLayout>
        </PublicRoute>
      } />
      
      <Route path="/signup" element={
        <PublicRoute>
          <AuthLayout>
            <SignUpForm />
          </AuthLayout>
        </PublicRoute>
      } />

      {/* Protected routes */}
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      } />
      
      <Route path="/analysis" element={
        <ProtectedRoute>
          <AnalysisPage />
        </ProtectedRoute>
      } />
      
      <Route path="/history" element={
        <ProtectedRoute>
          <DashboardPage />
        </ProtectedRoute>
      } />
      
      <Route path="/subscription" element={
        <ProtectedRoute>
          <SubscriptionPage />
        </ProtectedRoute>
      } />
      
      <Route path="/success" element={
        <ProtectedRoute>
          <SuccessPage />
        </ProtectedRoute>
      } />

      {/* Catch all route */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <Router>
        <AuthProvider>
          <div className="min-h-screen bg-background font-sans antialiased">
            <AppRoutes />
            <Toaster />
          </div>
        </AuthProvider>
      </Router>
    </ErrorBoundary>
  );
}
