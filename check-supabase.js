
import { createClient } from '@supabase/supabase-js'
import * as dotenv from 'dotenv'

dotenv.config()

const supabaseUrl = process.env.VITE_SUPABASE_URL
const supabaseAnonKey = process.env.VITE_SUPABASE_ANON_KEY

console.log('Checking Supabase configuration...')
console.log('URL:', supabaseUrl ? 'Set' : 'Missing')
console.log('Anon Key:', supabaseAnonKey ? 'Set' : 'Missing')

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('❌ Supabase environment variables are not set properly')
  process.exit(1)
}

try {
  const supabase = createClient(supabaseUrl, supabaseAnonKey)
  
  // Test connection
  const { data, error } = await supabase
    .from('users')
    .select('count')
    .limit(1)
  
  if (error) {
    console.error('❌ Database connection failed:', error.message)
  } else {
    console.log('✅ Database connection successful')
  }
  
  // Test auth
  const { data: authData, error: authError } = await supabase.auth.getSession()
  
  if (authError) {
    console.error('❌ Auth service error:', authError.message)
  } else {
    console.log('✅ Auth service is working')
  }
  
} catch (error) {
  console.error('❌ Connection failed:', error)
}
