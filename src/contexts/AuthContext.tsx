
import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { User, Session, AuthError } from "@supabase/supabase-js";
import { supabase, testSupabaseConnection, handleSupabaseError } from "@/lib/supabase";
import { toast } from "@/components/ui/use-toast";

interface AuthContextType {
  user: User | null;
  session: Session | null;
  loading: boolean;
  connectionStatus: 'connected' | 'disconnected' | 'checking';
  signUp: (email: string, password: string, fullName?: string) => Promise<{ error: AuthError | null }>;
  signIn: (email: string, password: string) => Promise<{ error: AuthError | null }>;
  signOut: () => Promise<{ error: AuthError | null }>;
  resetPassword: (email: string) => Promise<{ error: AuthError | null }>;
  updateProfile: (updates: { full_name?: string; avatar_url?: string }) => Promise<{ error: any }>;
  retryConnection: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  session: null,
  loading: true,
  connectionStatus: 'checking',
  signUp: async () => ({ error: null }),
  signIn: async () => ({ error: null }),
  signOut: async () => ({ error: null }),
  resetPassword: async () => ({ error: null }),
  updateProfile: async () => ({ error: null }),
  retryConnection: async () => {},
});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  // Test connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    setConnectionStatus('checking');
    try {
      const isConnected = await testSupabaseConnection();
      setConnectionStatus(isConnected ? 'connected' : 'disconnected');
      if (!isConnected) {
        toast({
          title: "Connection Issue",
          description: "Unable to connect to the database. Some features may not work.",
          variant: "destructive",
        });
      }
    } catch (error) {
      console.error('Connection check failed:', error);
      setConnectionStatus('disconnected');
    }
  };

  const retryConnection = async () => {
    await checkConnection();
    if (connectionStatus === 'connected') {
      // Retry getting session if connection is restored
      await getInitialSession();
    }
  };

  const getInitialSession = async () => {
    try {
      const { data: { session }, error } = await supabase.auth.getSession();
      if (error) {
        console.error("Error getting session:", error);
        toast({
          title: "Session Error",
          description: handleSupabaseError(error),
          variant: "destructive",
        });
      } else {
        setSession(session);
        setUser(session?.user ?? null);
      }
    } catch (error) {
      console.error("Error in getInitialSession:", error);
      toast({
        title: "Authentication Error",
        description: "Failed to restore your session. Please log in again.",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only proceed if we have a connection
    if (connectionStatus !== 'connected') {
      setLoading(false);
      return;
    }

    getInitialSession();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log("Auth state changed:", event);
        setSession(session);
        setUser(session?.user ?? null);
        setLoading(false);

        // Handle specific auth events
        switch (event) {
          case 'SIGNED_IN':
            toast({
              title: "Welcome back!",
              description: "You have been successfully signed in.",
            });
            break;
          case 'SIGNED_OUT':
            toast({
              title: "Signed out",
              description: "You have been successfully signed out.",
            });
            break;
          case 'TOKEN_REFRESHED':
            console.log("Token refreshed successfully");
            break;
          case 'USER_UPDATED':
            toast({
              title: "Profile updated",
              description: "Your profile has been updated successfully.",
            });
            break;
          case 'PASSWORD_RECOVERY':
            toast({
              title: "Password reset",
              description: "Please check your email for password reset instructions.",
            });
            break;
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, [connectionStatus]);

  const signUp = async (email: string, password: string, fullName?: string) => {
    if (connectionStatus !== 'connected') {
      const error = new Error('No database connection') as AuthError;
      toast({
        title: "Connection Error",
        description: "Cannot sign up without database connection. Please try again later.",
        variant: "destructive",
      });
      return { error };
    }

    try {
      setLoading(true);
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
          },
        },
      });

      if (error) {
        toast({
          title: "Sign up failed",
          description: handleSupabaseError(error),
          variant: "destructive",
        });
        return { error };
      }

      if (data.user && !data.session) {
        toast({
          title: "Check your email",
          description: "We've sent you a confirmation link.",
        });
      }

      return { error: null };
    } catch (error) {
      console.error("Sign up error:", error);
      const authError = new Error(handleSupabaseError(error)) as AuthError;
      return { error: authError };
    } finally {
      setLoading(false);
    }
  };

  const signIn = async (email: string, password: string) => {
    if (connectionStatus !== 'connected') {
      const error = new Error('No database connection') as AuthError;
      toast({
        title: "Connection Error",
        description: "Cannot sign in without database connection. Please try again later.",
        variant: "destructive",
      });
      return { error };
    }

    try {
      setLoading(true);
      const { error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) {
        toast({
          title: "Sign in failed",
          description: handleSupabaseError(error),
          variant: "destructive",
        });
        return { error };
      }

      return { error: null };
    } catch (error) {
      console.error("Sign in error:", error);
      const authError = new Error(handleSupabaseError(error)) as AuthError;
      return { error: authError };
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    try {
      setLoading(true);
      const { error } = await supabase.auth.signOut();
      
      if (error) {
        toast({
          title: "Sign out failed",
          description: handleSupabaseError(error),
          variant: "destructive",
        });
        return { error };
      }

      return { error: null };
    } catch (error) {
      console.error("Sign out error:", error);
      const authError = new Error(handleSupabaseError(error)) as AuthError;
      return { error: authError };
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (email: string) => {
    if (connectionStatus !== 'connected') {
      const error = new Error('No database connection') as AuthError;
      toast({
        title: "Connection Error",
        description: "Cannot reset password without database connection. Please try again later.",
        variant: "destructive",
      });
      return { error };
    }

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) {
        toast({
          title: "Password reset failed",
          description: handleSupabaseError(error),
          variant: "destructive",
        });
        return { error };
      }

      toast({
        title: "Check your email",
        description: "We've sent you a password reset link.",
      });

      return { error: null };
    } catch (error) {
      console.error("Password reset error:", error);
      const authError = new Error(handleSupabaseError(error)) as AuthError;
      return { error: authError };
    }
  };

  const updateProfile = async (updates: { full_name?: string; avatar_url?: string }) => {
    if (connectionStatus !== 'connected') {
      const error = new Error('No database connection');
      toast({
        title: "Connection Error",
        description: "Cannot update profile without database connection. Please try again later.",
        variant: "destructive",
      });
      return { error };
    }

    try {
      if (!user) throw new Error("No user logged in");

      const { error } = await supabase.auth.updateUser({
        data: updates,
      });

      if (error) {
        toast({
          title: "Profile update failed",
          description: handleSupabaseError(error),
          variant: "destructive",
        });
        return { error };
      }

      // Also update the users table if connected
      try {
        const { error: dbError } = await supabase
          .from('users')
          .update(updates)
          .eq('id', user.id);

        if (dbError) {
          console.error("Database update error:", dbError);
          // Don't fail the whole operation for this
        }
      } catch (dbError) {
        console.error("Database update failed:", dbError);
      }

      return { error: null };
    } catch (error) {
      console.error("Profile update error:", error);
      return { error };
    }
  };

  const value = {
    user,
    session,
    loading,
    connectionStatus,
    signUp,
    signIn,
    signOut,
    resetPassword,
    updateProfile,
    retryConnection,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
