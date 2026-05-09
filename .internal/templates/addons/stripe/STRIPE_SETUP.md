# Stripe Setup Guide

## Prerequisites

1. Create a Stripe account at https://stripe.com
2. Get your API keys from Dashboard > Developers > API keys

## Environment Setup

```bash
# Client-side (already in .env.example)
EXPO_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Server-side (Firebase Functions config)
firebase functions:config:set stripe.secret_key="sk_test_..." stripe.webhook_secret="whsec_..."
```

## Stripe Webhook (Local Testing)

1. Install Stripe CLI: https://stripe.com/docs/stripe-cli
2. Forward webhook events to your local Functions emulator:
   ```bash
   stripe listen --forward-to localhost:5001/{project-id}/{region}/stripeWebhook
   ```
3. Trigger test events:
   ```bash
   stripe trigger checkout.session.completed
   ```

## Test Cards

- Success: `4242424242424242`
- Decline: `4000000000000002`
- Auth required: `4000002500003155`
