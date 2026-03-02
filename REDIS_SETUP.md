# Redis Setup for NovaOS Autonomous System

NovaOS uses Redis for pub/sub coordination between the market discovery engine and product builder.

## Option 1: Upstash Redis (Recommended - Free Tier)

**Why Upstash:**
- Free tier: 10,000 commands/day (plenty for our needs)
- Global edge locations
- TLS encryption
- No credit card required
- Serverless (pay only for what you use)

### Setup Steps:

1. **Create Upstash Account**
   - Go to: https://console.upstash.com/
   - Sign up with GitHub (easiest)

2. **Create Redis Database**
   - Click "Create Database"
   - Name: `novaos-production`
   - Type: Regional (cheaper)
   - Region: Choose closest to your Render region (US East for most)
   - Primary Region: `us-east-1`
   - Click "Create"

3. **Get Connection URL**
   - On database page, click "Connect"
   - Copy the **TLS (Redis URL)** - looks like:
     ```
     rediss://:AbCdEf123...@endpoint.upstash.io:6379
     ```

4. **Add to Render**
   - Go to Render dashboard: https://dashboard.render.com/
   - Open your NovaOS service
   - Go to "Environment" tab
   - Add environment variable:
     - Key: `REDIS_URL`
     - Value: `rediss://:AbCdEf123...@endpoint.upstash.io:6379`
   - Click "Save Changes"
   - Service will auto-redeploy

5. **Verify Connection**
   - Check Render logs for: "Connected to Redis"
   - Check Upstash dashboard for connection activity

## Option 2: Local Redis (Development Only)

For local testing:

```bash
# Install Redis (Mac)
brew install redis

# Start Redis server
redis-server

# In another terminal, test connection
redis-cli ping
# Should respond: PONG
```

Set in local `.env`:
```
REDIS_URL=redis://localhost:6379
```

## How It Works

### Architecture:

```
┌─────────────────────┐
│ Market Discovery    │
│ Worker              │
│                     │
│ 1. Scans Reddit     │
│ 2. Scores opps      │
│ 3. Publishes to     │
│    novaos:opportunities
└──────────┬──────────┘
           │
           │ Redis Pub/Sub
           │
           ▼
┌─────────────────────┐
│ Product Builder     │
│ Worker              │
│                     │
│ 1. Listens on       │
│    novaos:opportunities
│ 2. Builds product   │
│ 3. Publishes to     │
│    novaos:insights  │
└─────────────────────┘
```

### Redis Channels:

1. **`novaos:opportunities`** (discovery → builder)
   - Discovery publishes scored opportunities here
   - Builder subscribes and receives them
   - Message format:
     ```json
     {
       "timestamp": "2026-03-01T15:00:00",
       "opportunity": {
         "problem": "AI email automation for law firms",
         "price": 299,
         "estimated_customers": 100,
         "scores": {
           "total_score": 89,
           "decision": "BUILD"
         }
       },
       "action": "build_product"
     }
     ```

2. **`novaos:insights`** (builder → dashboard)
   - Builder publishes completed products here
   - Dashboard can subscribe to show progress
   - Message format:
     ```json
     {
       "timestamp": "2026-03-01T16:30:00",
       "event": "product_built",
       "product": "AI email automation for law firms",
       "output_dir": "/path/to/product",
       "status": "deployed",
       "profit_potential": 358800
     }
     ```

## Cost Monitoring

**Upstash Free Tier:**
- 10,000 commands/day
- Our usage (estimated):
  - Discovery worker runs every 6 hours = 4x/day
  - Each discovery publishes ~5 opportunities = 20 publishes/day
  - Builder listens continuously = ~100 commands/day
  - **Total: ~150 commands/day** (well under 10,000 limit)

**Cost if we exceed free tier:**
- ~$0.20 per 100K commands
- At 10x our usage (1,500 commands/day) = $0.09/month
- Still essentially free

## Troubleshooting

### "Connection refused" error:
- Check REDIS_URL is correct (starts with `rediss://` for TLS)
- Verify Upstash database is active
- Check Render environment variables are saved

### "Authentication failed" error:
- Redis URL includes password after `:` like `rediss://:PASSWORD@endpoint`
- Copy full URL from Upstash, don't edit it

### Workers not communicating:
- Check both workers are running (Render logs)
- Verify they're using same REDIS_URL
- Test Redis connection: `redis-cli -u $REDIS_URL ping`

### High latency:
- Use Upstash region closest to Render
- Consider upgrading to Upstash Pro for better performance
- Check Upstash dashboard for connection metrics

## Security Notes

- ✅ Always use TLS connection (`rediss://` not `redis://`)
- ✅ Never commit Redis URL to git
- ✅ Use Render environment variables (encrypted at rest)
- ✅ Upstash automatically rotates passwords
- ✅ Use IP whitelisting if needed (Upstash Pro)

## Next Steps

After Redis is configured:

1. Deploy NovaOS to Render (will use Redis automatically)
2. Check logs for "Connected to Redis"
3. Market Discovery will start finding opportunities
4. Product Builder will start building autonomously
5. Monitor Upstash dashboard for activity

## Support

- Upstash Docs: https://docs.upstash.com/redis
- Upstash Discord: https://upstash.com/discord
- NovaOS Issues: Create issue in repo if Redis integration problems
