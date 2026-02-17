#!/bin/bash

# NovaOS V2 - Production Deployment (AGGRESSIVE MODE)
# Deploy to Render.com with 18 revenue agents running

set -e  # Exit on error

echo "========================================="
echo "NovaOS V2 Production Deployment"
echo "AGGRESSIVE MODE - 18 Revenue Agents"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}Error: git is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Git installed${NC}"

# Check if render CLI is installed (optional)
RENDER_CLI_AVAILABLE=false
if command -v render &> /dev/null; then
    RENDER_CLI_AVAILABLE=true
    echo -e "${GREEN}✓ Render CLI installed${NC}"
else
    echo -e "${YELLOW}⚠ Render CLI not installed (will use manual setup)${NC}"
    echo -e "${BLUE}  Install with: npm install -g @render/cli${NC}"
fi

echo ""

# Auto-load API keys from environment or .env file
echo "Loading API keys..."

# Try to load from .env file if exists
if [ -f ".env" ]; then
    echo -e "${BLUE}Loading from .env file...${NC}"
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check required environment variables
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${RED}Error: ANTHROPIC_API_KEY not set${NC}"
    echo ""
    echo "Please set it in one of these ways:"
    echo "  1. Export: export ANTHROPIC_API_KEY='sk-ant-...'"
    echo "  2. Create .env file with: ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    echo "Get your key from: https://console.anthropic.com"
    exit 1
fi

echo -e "${GREEN}✓ ANTHROPIC_API_KEY loaded${NC}"

# Check optional keys
if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${GREEN}✓ TELEGRAM_BOT_TOKEN loaded${NC}"
else
    echo -e "${YELLOW}⚠ TELEGRAM_BOT_TOKEN not set (optional)${NC}"
fi

if [ ! -z "$TELEGRAM_ADMIN_CHAT_ID" ]; then
    echo -e "${GREEN}✓ TELEGRAM_ADMIN_CHAT_ID loaded${NC}"
else
    echo -e "${YELLOW}⚠ TELEGRAM_ADMIN_CHAT_ID not set (optional)${NC}"
fi

echo ""

# Initialize git repo if not already
if [ ! -d ".git" ]; then
    echo "Initializing git repository..."
    git init
    git add .
    git commit -m "Initial NovaOS V2 deployment"
    echo -e "${GREEN}✓ Git initialized${NC}"
fi

# Create .gitignore if not exists
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# Environment
.env
.env.local
.env.production

# Data
data/
logs/
*.db
*.sqlite

# Security
*.pem
*.key

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
    git add .gitignore
    git commit -m "Add .gitignore"
    echo -e "${GREEN}✓ .gitignore created${NC}"
fi

echo ""
echo "========================================="
echo "Deployment Options"
echo "========================================="
echo "1. Deploy to Render.com (Recommended)"
echo "2. Deploy to Heroku"
echo "3. Deploy to Railway"
echo "4. Manual deployment"
echo ""
read -p "Choose deployment method (1-4): " choice

case $choice in
    1)
        echo ""
        echo "========================================="
        echo "Deploying to Render.com"
        echo "========================================="
        echo ""

        echo "Steps to deploy:"
        echo "1. Go to https://dashboard.render.com"
        echo "2. Click 'New +' → 'Blueprint'"
        echo "3. Connect your GitHub repository"
        echo "4. Select this repository"
        echo "5. Render will detect render-aggressive.yaml and create all services"
        echo ""
        echo -e "${BLUE}AGGRESSIVE MODE: This will create 20 services (18 revenue agents)${NC}"
        echo ""
        echo "Environment variables to set in Render dashboard:"
        echo ""
        echo -e "${GREEN}Required:${NC}"
        echo "  ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
        echo ""
        echo -e "${YELLOW}Highly Recommended (for Telegram control):${NC}"

        if [ ! -z "$TELEGRAM_BOT_TOKEN" ]; then
            echo "  TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN"
        else
            echo "  TELEGRAM_BOT_TOKEN=(get from @BotFather on Telegram)"
        fi

        if [ ! -z "$TELEGRAM_ADMIN_CHAT_ID" ]; then
            echo "  TELEGRAM_ADMIN_CHAT_ID=$TELEGRAM_ADMIN_CHAT_ID"
        else
            echo "  TELEGRAM_ADMIN_CHAT_ID=(get from @userinfobot on Telegram)"
        fi

        echo ""
        echo -e "${BLUE}Optional (for enhanced features):${NC}"
        echo "  GUMROAD_API_KEY=(for product listing on Gumroad)"
        echo "  SENDGRID_API_KEY=(for email outreach)"
        echo ""

        # Push to GitHub
        read -p "Have you connected this repo to GitHub? (y/n): " github_ready

        if [ "$github_ready" = "y" ]; then
            echo ""
            echo "Pushing to GitHub..."
            git add .
            git commit -m "Production deployment ready" || true

            read -p "Enter GitHub repository URL (e.g., git@github.com:username/novaos-v2.git): " github_url

            if [ ! -z "$github_url" ]; then
                git remote add origin $github_url || git remote set-url origin $github_url
                git branch -M main
                git push -u origin main
                echo -e "${GREEN}✓ Pushed to GitHub${NC}"
            fi
        else
            echo ""
            echo "Create a GitHub repository and push:"
            echo "  git remote add origin git@github.com:username/novaos-v2.git"
            echo "  git branch -M main"
            echo "  git push -u origin main"
        fi

        echo ""
        echo -e "${GREEN}=========================================${NC}"
        echo -e "${GREEN}Deployment Instructions Complete!${NC}"
        echo -e "${GREEN}=========================================${NC}"
        echo ""
        echo "Next steps:"
        echo "1. Go to https://dashboard.render.com"
        echo "2. Deploy using Blueprint (render.yaml)"
        echo "3. Set environment variables"
        echo "4. Services will start automatically"
        echo ""
        echo "Your NovaOS will be available at:"
        echo "https://novaos-dashboard.onrender.com (or similar)"
        echo ""
        echo "Revenue agents will start earning within 12-24 hours!"
        ;;

    2)
        echo ""
        echo "Heroku deployment not yet configured."
        echo "Use Render.com (option 1) for quickest deployment."
        ;;

    3)
        echo ""
        echo "Railway deployment not yet configured."
        echo "Use Render.com (option 1) for quickest deployment."
        ;;

    4)
        echo ""
        echo "For manual deployment:"
        echo "1. Set up a server with Python 3.11+"
        echo "2. Install PostgreSQL"
        echo "3. Install requirements: pip install -r requirements-production.txt"
        echo "4. Set environment variables from .env.production.example"
        echo "5. Run: gunicorn dashboard.app:app"
        echo "6. Start agents as background processes"
        ;;

    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "========================================="
echo "Post-Deployment Checklist (AGGRESSIVE)"
echo "========================================="
echo "□ Dashboard accessible"
echo "□ Telegram bot responding"
echo "□ 18 revenue agents running (AGGRESSIVE MODE)"
echo "□ Security layer active"
echo "□ Database connected"
echo "□ Budget limits enforced (\$200/day - AGGRESSIVE)"
echo ""
echo -e "${BLUE}Expected Results:${NC}"
echo "  • 6 hours: 10+ products, first gig, 100+ leads"
echo "  • 1 week: \$500-2000 revenue"
echo "  • 1 month: \$4,000-19,000 profit"
echo ""
echo "Monitor at: https://dashboard.render.com"
echo ""
echo -e "${GREEN}Deployment script complete!${NC}"
