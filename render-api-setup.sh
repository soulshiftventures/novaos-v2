#!/bin/bash

# NovaOS V2 - Render API Environment Variables Setup
# Automatically sets environment variables via Render API

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Render API - Auto Environment Setup                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠ jq is not installed (required for JSON parsing)${NC}"
    echo "Install with:"
    echo "  macOS: brew install jq"
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  CentOS/RHEL: sudo yum install jq"
    echo ""
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    source .env
fi

# Check for required variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}✗ ANTHROPIC_API_KEY not found in .env${NC}"
    exit 1
fi

# Check for Render API key
if [ -z "$RENDER_API_KEY" ]; then
    echo -e "${YELLOW}⚠ RENDER_API_KEY not set${NC}"
    echo ""
    echo "To automatically configure environment variables, you need a Render API key."
    echo ""
    echo "Get your API key:"
    echo "  1. Go to: https://dashboard.render.com/u/settings#api-keys"
    echo "  2. Create a new API key"
    echo "  3. Copy the key"
    echo ""
    read -s -p "Paste your Render API key: " RENDER_API_KEY
    echo ""

    if [ -z "$RENDER_API_KEY" ]; then
        echo -e "${RED}✗ Render API key required${NC}"
        exit 1
    fi

    # Save to .env
    echo "RENDER_API_KEY=$RENDER_API_KEY" >> .env
    echo -e "${GREEN}✓ API key saved${NC}"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Fetching Render Services"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Get list of services
SERVICES=$(curl -s -X GET \
    "https://api.render.com/v1/services" \
    -H "Authorization: Bearer $RENDER_API_KEY" \
    -H "Accept: application/json")

# Check if API call succeeded
if echo "$SERVICES" | jq -e . >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Successfully connected to Render API${NC}"
else
    echo -e "${RED}✗ Failed to connect to Render API${NC}"
    echo "Response: $SERVICES"
    exit 1
fi

# Extract service IDs for NovaOS services
SERVICE_IDS=$(echo "$SERVICES" | jq -r '.[] | select(.service.name | startswith("novaos") or startswith("product-creator") or startswith("content-arbitrage") or startswith("lead-gen")) | .service.id')

if [ -z "$SERVICE_IDS" ]; then
    echo -e "${YELLOW}⚠ No NovaOS services found${NC}"
    echo "Please deploy first using: ./deploy-one-command.sh"
    exit 1
fi

SERVICE_COUNT=$(echo "$SERVICE_IDS" | wc -l | tr -d ' ')
echo -e "${BLUE}Found $SERVICE_COUNT NovaOS services${NC}"
echo ""

# Prepare environment variables JSON
ENV_VARS=()
ENV_VARS+=("{\"key\":\"ANTHROPIC_API_KEY\",\"value\":\"$ANTHROPIC_API_KEY\"}")

if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
    ENV_VARS+=("{\"key\":\"TELEGRAM_BOT_TOKEN\",\"value\":\"$TELEGRAM_BOT_TOKEN\"}")
fi

if [ ! -z "$TELEGRAM_ADMIN_CHAT_ID" ]; then
    ENV_VARS+=("{\"key\":\"TELEGRAM_ADMIN_CHAT_ID\",\"value\":\"$TELEGRAM_ADMIN_CHAT_ID\"}")
fi

if [ ! -z "$GUMROAD_API_KEY" ]; then
    ENV_VARS+=("{\"key\":\"GUMROAD_API_KEY\",\"value\":\"$GUMROAD_API_KEY\"}")
fi

if [ ! -z "$SENDGRID_API_KEY" ]; then
    ENV_VARS+=("{\"key\":\"SENDGRID_API_KEY\",\"value\":\"$SENDGRID_API_KEY\"}")
fi

# Budget limits (AGGRESSIVE MODE)
ENV_VARS+=("{\"key\":\"NOVAOS_DAILY_BUDGET\",\"value\":\"200.0\"}")
ENV_VARS+=("{\"key\":\"NOVAOS_HOURLY_BUDGET\",\"value\":\"30.0\"}")
ENV_VARS+=("{\"key\":\"NOVAOS_EMERGENCY_THRESHOLD\",\"value\":\"250.0\"}")
ENV_VARS+=("{\"key\":\"NOVAOS_SECURITY_LEVEL\",\"value\":\"STRICT\"}")

echo "═══════════════════════════════════════════════════════════"
echo "Setting Environment Variables"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Set environment variables for each service
for SERVICE_ID in $SERVICE_IDS; do
    # Get service name
    SERVICE_NAME=$(curl -s -X GET \
        "https://api.render.com/v1/services/$SERVICE_ID" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        | jq -r '.name')

    echo -e "${BLUE}⚙  Configuring: $SERVICE_NAME${NC}"

    # Build JSON payload
    ENV_JSON=$(printf '%s\n' "${ENV_VARS[@]}" | jq -s '.')

    # Update environment variables
    RESPONSE=$(curl -s -X PUT \
        "https://api.render.com/v1/services/$SERVICE_ID/env-vars" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"envVars\": $ENV_JSON}")

    # Check if successful
    if echo "$RESPONSE" | jq -e '.[] | select(.key == "ANTHROPIC_API_KEY")' >/dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Environment variables set${NC}"
    else
        echo -e "${YELLOW}  ⚠ Warning: May have failed${NC}"
        echo "  Response: $RESPONSE"
    fi

    # Trigger redeploy to apply new env vars
    echo -e "${BLUE}  ⚙  Triggering redeploy...${NC}"
    DEPLOY_RESPONSE=$(curl -s -X POST \
        "https://api.render.com/v1/services/$SERVICE_ID/deploys" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"clearCache": false}')

    if echo "$DEPLOY_RESPONSE" | jq -e '.id' >/dev/null 2>&1; then
        echo -e "${GREEN}  ✓ Redeploy triggered${NC}"
    else
        echo -e "${YELLOW}  ⚠ Redeploy may have failed${NC}"
    fi

    echo ""
done

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ENVIRONMENT VARIABLES CONFIGURED!                         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

echo -e "${GREEN}✓ All services configured with environment variables${NC}"
echo -e "${GREEN}✓ Redeployments triggered${NC}"
echo ""
echo -e "${BLUE}Services will restart with new configuration (5-10 minutes)${NC}"
echo ""
echo "Monitor at: https://dashboard.render.com"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}AUTOMATIC CONFIGURATION COMPLETE!${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
