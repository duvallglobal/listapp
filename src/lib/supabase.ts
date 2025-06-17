
import { createClient } from "@supabase/supabase-js";

// Validate environment variables
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl) {
  throw new Error(
    "Missing VITE_SUPABASE_URL environment variable. Please add it to your .env file."
  );
}

if (!supabaseAnonKey) {
  throw new Error(
    "Missing VITE_SUPABASE_ANON_KEY environment variable. Please add it to your .env file."
  );
}

// Validate URL format
try {
  new URL(supabaseUrl);
} catch {
  throw new Error(
    "Invalid VITE_SUPABASE_URL format. Please ensure it's a valid URL (e.g., https://your-project.supabase.co)"
  );
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
  },
  db: {
    schema: 'public',
  },
  global: {
    headers: {
      'x-my-custom-header': 'price-intelligence-platform',
    },
  },
});

// Connection test utility with retry logic
export const testSupabaseConnection = async (retries = 3): Promise<boolean> => {
  for (let i = 0; i < retries; i++) {
    try {
      const { data, error } = await supabase.from('users').select('count').limit(1);
      if (error) {
        console.error(`Supabase connection test failed (attempt ${i + 1}):`, error.message);
        if (i === retries - 1) return false;
        // Wait before retry (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
        continue;
      }
      console.log('Supabase connection successful');
      return true;
    } catch (err) {
      console.error(`Supabase connection error (attempt ${i + 1}):`, err);
      if (i === retries - 1) return false;
      await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
    }
  }
  return false;
};

// Enhanced error handling for specific error types
export const handleSupabaseError = (error: any) => {
  if (error?.code === 'PGRST301') {
    return 'Database connection timeout. Please try again.';
  }
  if (error?.code === 'PGRST116') {
    return 'No data found.';
  }
  if (error?.message?.includes('JWT')) {
    return 'Session expired. Please log in again.';
  }
  if (error?.message?.includes('fetch')) {
    return 'Network error. Please check your connection.';
  }
  return error?.message || 'An unexpected error occurred.';
};
