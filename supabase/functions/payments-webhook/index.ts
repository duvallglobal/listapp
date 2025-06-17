import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'
import Stripe from 'https://esm.sh/stripe@14.21.0'

const stripe = new Stripe(Deno.env.get('STRIPE_SECRET_KEY') || '', {
  apiVersion: '2023-10-16',
})

const supabaseClient = createClient(
  Deno.env.get('SUPABASE_URL') ?? '',
  Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
)

const cryptoProvider = Stripe.createSubtleCryptoProvider()

serve(async (req) => {
  const signature = req.headers.get('stripe-signature')
  const body = await req.text()

  let event: Stripe.Event

  try {
    event = await stripe.webhooks.constructEventAsync(
      body,
      signature!,
      Deno.env.get('STRIPE_WEBHOOK_SECRET')!,
      undefined,
      cryptoProvider
    )
  } catch (err) {
    console.error('Webhook signature verification failed:', err.message)
    return new Response('Invalid signature', { status: 400 })
  }

  console.log('Processing webhook event:', event.type)

  try {
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutSessionCompleted(event.data.object as Stripe.Checkout.Session)
        break

      case 'customer.subscription.created':
      case 'customer.subscription.updated':
        await handleSubscriptionChanged(event.data.object as Stripe.Subscription)
        break

      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object as Stripe.Subscription)
        break

      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(event.data.object as Stripe.Invoice)
        break

      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object as Stripe.Invoice)
        break

      default:
        console.log(`Unhandled event type: ${event.type}`)
    }

    // Log the webhook event
    await supabaseClient.from('webhook_events').insert({
      stripe_event_id: event.id,
      event_type: event.type,
      data: event.data,
      processed: true
    })

    return new Response('OK', { status: 200 })
  } catch (error) {
    console.error('Error processing webhook:', error)

    // Log the failed webhook event
    await supabaseClient.from('webhook_events').insert({
      stripe_event_id: event.id,
      event_type: event.type,
      data: event.data,
      processed: false
    })

    return new Response('Error processing webhook', { status: 500 })
  }
})

async function handleCheckoutSessionCompleted(session: Stripe.Checkout.Session) {
  const userId = session.metadata?.user_id
  if (!userId) return

  console.log('Checkout completed for user:', userId)

  // The subscription will be handled by the subscription.created event
  // This is mainly for logging and any immediate post-checkout actions
}

async function handleSubscriptionChanged(subscription: Stripe.Subscription) {
  const userId = subscription.metadata?.user_id
  if (!userId) return

  console.log('Subscription changed for user:', userId, 'Status:', subscription.status)

  const subscriptionData = {
    user_id: userId,
    stripe_subscription_id: subscription.id,
    stripe_customer_id: subscription.customer as string,
    status: subscription.status,
    price_id: subscription.items.data[0]?.price.id,
    current_period_start: new Date(subscription.current_period_start * 1000).toISOString(),
    current_period_end: new Date(subscription.current_period_end * 1000).toISOString(),
    cancel_at_period_end: subscription.cancel_at_period_end,
    updated_at: new Date().toISOString()
  }

  // Upsert subscription
  const { error } = await supabaseClient
    .from('subscriptions')
    .upsert(subscriptionData, {
      onConflict: 'stripe_subscription_id',
      ignoreDuplicates: false
    })

  if (error) {
    console.error('Error upserting subscription:', error)
    throw error
  }

  // Update user subscription status
  await supabaseClient
    .from('users')
    .update({ 
      subscription_status: subscription.status,
      updated_at: new Date().toISOString()
    })
    .eq('id', userId)

  // If subscription is active, allocate credits based on the plan
  if (subscription.status === 'active') {
    await allocateCreditsForPlan(userId, subscription.items.data[0]?.price.id)
  }
}

async function handleSubscriptionDeleted(subscription: Stripe.Subscription) {
  const userId = subscription.metadata?.user_id
  if (!userId) return

  console.log('Subscription deleted for user:', userId)

  // Update subscription status
  await supabaseClient
    .from('subscriptions')
    .update({ 
      status: 'canceled',
      updated_at: new Date().toISOString()
    })
    .eq('stripe_subscription_id', subscription.id)

  // Update user status
  await supabaseClient
    .from('users')
    .update({ 
      subscription_status: 'inactive',
      updated_at: new Date().toISOString()
    })
    .eq('id', userId)
}

async function handlePaymentSucceeded(invoice: Stripe.Invoice) {
  const subscriptionId = invoice.subscription as string
  if (!subscriptionId) return

  console.log('Payment succeeded for subscription:', subscriptionId)

  // Get subscription to find user
  const subscription = await stripe.subscriptions.retrieve(subscriptionId)
  const userId = subscription.metadata?.user_id

  if (userId) {
    // Allocate credits for the new billing period
    await allocateCreditsForPlan(userId, invoice.lines.data[0]?.price?.id)
  }
}

async function handlePaymentFailed(invoice: Stripe.Invoice) {
  const subscriptionId = invoice.subscription as string
  if (!subscriptionId) return

  console.log('Payment failed for subscription:', subscriptionId)

  // Get subscription to find user
  const subscription = await stripe.subscriptions.retrieve(subscriptionId)
  const userId = subscription.metadata?.user_id

  if (userId) {
    // Update user status to indicate payment issue
    await supabaseClient
      .from('users')
      .update({ 
        subscription_status: 'past_due',
        updated_at: new Date().toISOString()
      })
      .eq('id', userId)
  }
}

async function allocateCreditsForPlan(userId: string, priceId?: string) {
  if (!priceId) return

  // Define credit allocations for each plan
  const creditAllocations: Record<string, number> = {
    'price_basic_monthly': 50,
    'price_pro_monthly': 200,
    'price_business_monthly': 1000,
    'price_enterprise_monthly': 5000,
  }

  const credits = creditAllocations[priceId]
  if (!credits) return

  console.log(`Allocating ${credits} credits to user ${userId}`)

  // Update user credits
  await supabaseClient
    .from('users')
    .update({ 
      credits: credits.toString(),
      updated_at: new Date().toISOString()
    })
    .eq('id', userId)

  // Log credit allocation
  await supabaseClient
    .from('credit_usage')
    .insert({
      user_id: userId,
      credits_used: -credits, // Negative for credit addition
      credits_remaining: credits,
      action_type: 'subscription_renewal'
    })
}