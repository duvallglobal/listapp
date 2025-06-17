
# Supabase Setup Guide for Price Intelligence Platform

This guide will walk you through setting up Supabase for the Price Intelligence Platform application.

## Prerequisites

- A Supabase account (sign up at https://supabase.com)
- Basic understanding of SQL and database concepts

## Step 1: Create a New Supabase Project

1. Log in to your Supabase dashboard
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `price-intelligence-platform`
   - **Database Password**: Choose a strong password (save this!)
   - **Region**: Choose the region closest to your users
5. Click "Create new project"
6. Wait for the project to be created (usually 2-3 minutes)

## Step 2: Get Your Project Credentials

1. In your project dashboard, go to Settings > API
2. Copy the following values:
   - **Project URL**: `https://your-project.supabase.co`
   - **Anon/Public Key**: `eyJ...` (starts with eyJ)
   - **Service Role Key**: `eyJ...` (different from anon key)
3. Go to Settings > General and copy:
   - **Project ID**: Used for CLI and advanced features

## Step 3: Configure Environment Variables

Create a `.env` file in your project root with the following:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-key-here
SUPABASE_PROJECT_ID=your-project-id

# Add other environment variables as needed...
```

**Important**: Replace the placeholder values with your actual Supabase credentials.

## Step 4: Set Up Database Schema

1. In your Supabase dashboard, go to the SQL Editor
2. Run the complete schema migration located in `supabase/migrations/20240101000001_complete_application_schema.sql`
3. This will create:
   - All necessary tables (users, subscriptions, analysis_history, etc.)
   - Row Level Security (RLS) policies
   - Storage buckets
   - Functions and triggers

## Step 5: Configure Authentication

1. Go to Authentication > Settings in your Supabase dashboard
2. Configure the following settings:

### Site URL
- **Site URL**: `http://localhost:5173` (for development)
- **Additional Redirect URLs**: Add your production domain when ready

### Email Settings
- Enable "Enable email confirmations" if you want email verification
- Customize email templates under Authentication > Email Templates

### Providers (Optional)
- Configure OAuth providers (Google, GitHub, etc.) if needed
- Each provider requires API keys from the respective service

## Step 6: Set Up Storage

The migration script automatically creates storage buckets, but you can verify:

1. Go to Storage in your Supabase dashboard
2. You should see two buckets:
   - `analysis-images`: For product analysis images
   - `user-avatars`: For user profile pictures

### Storage Policies
The migration script sets up proper RLS policies for storage, ensuring users can only access their own files.

## Step 7: Configure Stripe Integration (Optional)

If you plan to use paid subscriptions:

1. Get your Stripe API keys from the Stripe dashboard
2. Add them to your environment variables:
   ```env
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   ```
3. Set up Stripe products and prices in your Stripe dashboard
4. Update the subscription tier configurations in your application

## Step 8: Set Up Edge Functions (Optional)

For advanced features like payment processing:

1. Install Supabase CLI: `npm install -g @supabase/cli`
2. Login: `supabase login`
3. Link your project: `supabase link --project-ref your-project-id`
4. Deploy functions: `supabase functions deploy`

## Step 9: Test Your Setup

1. Start your development server: `npm run dev`
2. Try to sign up for a new account
3. Verify the user appears in Authentication > Users
4. Check that the user record is created in the `users` table
5. Test basic functionality like creating an analysis

## Step 10: Production Deployment

When ready for production:

1. Update environment variables with production values
2. Update Site URL in Authentication settings
3. Configure custom domain if using one
4. Set up monitoring and alerts
5. Configure backup policies

## Security Considerations

### Row Level Security (RLS)
- All tables have RLS enabled
- Users can only access their own data
- Service role bypasses RLS for admin operations

### API Keys
- Never expose your service role key in frontend code
- Use environment variables for all sensitive data
- Rotate keys regularly

### Storage Security
- Files are organized by user ID
- Proper access policies prevent unauthorized access

## Troubleshooting Common Issues

### Connection Issues
- Verify your project URL and API keys
- Check if your project is paused (free tier limitation)
- Ensure proper network connectivity

### Authentication Issues
- Check Site URL configuration
- Verify email settings if using email confirmation
- Review RLS policies if having permission issues

### Database Issues
- Run migrations in the correct order
- Check for syntax errors in SQL
- Verify table relationships and constraints

## Support and Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Discord Community](https://discord.supabase.com)
- [GitHub Issues](https://github.com/supabase/supabase/issues)

## Next Steps

After completing this setup:

1. Test all authentication flows
2. Verify database operations
3. Test file uploads
4. Configure monitoring
5. Set up CI/CD pipeline
6. Plan for scaling and optimization

Your Supabase backend is now ready for the Price Intelligence Platform!
