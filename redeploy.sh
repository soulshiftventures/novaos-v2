#!/bin/bash

# NovaOS V2 - One-Command Redeploy
# Push changes and trigger Render.com redeploy

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  NovaOS V2 - Redeploy with Enhanced Agents                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if there are changes
if [[ -z $(git status -s) ]]; then
    echo -e "${YELLOW}No changes to deploy${NC}"
    exit 0
fi

echo -e "${BLUE}Changes detected:${NC}"
git status -s
echo ""

# Commit changes
echo -e "${BLUE}Committing changes...${NC}"
git add .
git commit -m "Enhanced agents with GitHub best practices + incremental spawning"

# Push to GitHub
echo -e "${BLUE}Pushing to GitHub...${NC}"
git push origin main

echo ""
echo -e "${GREEN}✓ Code pushed to GitHub${NC}"
echo ""

# Render will auto-deploy on git push (if auto-deploy enabled)
echo "═══════════════════════════════════════════════════════════"
echo "Render.com Auto-Deploy"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "Your services will auto-redeploy in 2-5 minutes"
echo ""
echo "Monitor at: https://dashboard.render.com"
echo ""
echo "Services to watch:"
echo "  • novaos-dashboard"
echo "  • novaos-telegram-bot"
echo "  • product-creator-ai-ml"
echo "  • content-arbitrage-upwork"
echo "  • lead-gen-saas"
echo ""

# Create deployment timestamp
cat > .last-deploy << EOF
Deployed: $(date)
Commit: $(git rev-parse --short HEAD)
Branch: $(git branch --show-current)

Enhanced Features:
  ✓ GitHub best practices injected
  ✓ Proven system prompts
  ✓ Incremental spawning enabled
  ✓ Revenue optimization patterns

Status: Deploying...
Check: https://dashboard.render.com
EOF

echo -e "${GREEN}✓ Redeploy initiated!${NC}"
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Enhanced agents deploying...                              ║"
echo "║  Check Telegram in 10 minutes: /status                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
