#!/bin/bash
# NovaOS V2 Deployment Script

set -e

echo "=================================="
echo "NovaOS V2 Deployment"
echo "=================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Parse arguments
DEPLOY_TARGET=${1:-local}
ACTION=${2:-start}

echo -e "${GREEN}Deployment Target:${NC} $DEPLOY_TARGET"
echo -e "${GREEN}Action:${NC} $ACTION"
echo ""

# Function to check if .env exists
check_env() {
    if [ ! -f .env ]; then
        echo -e "${YELLOW}Warning: .env file not found${NC}"
        echo "Creating .env from .env.example..."
        cp .env.example .env
        echo -e "${RED}IMPORTANT: Edit .env and add your API keys${NC}"
        exit 1
    fi
}

# Function to check Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker not installed${NC}"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: docker-compose not installed${NC}"
        exit 1
    fi
}

# Local deployment
deploy_local() {
    echo "Deploying locally..."

    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 not installed${NC}"
        exit 1
    fi

    # Create virtual environment if needed
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "Installing dependencies..."
    pip install -r requirements.txt

    # Install optional dependencies
    pip install stripe sendgrid tweepy beautifulsoup4 requests psutil

    # Create data directories
    mkdir -p data logs

    echo -e "${GREEN}Local deployment ready!${NC}"
    echo ""
    echo "To start workers: ./nova workers start"
    echo "To enable autonomous mode: ./nova autonomous enable"
    echo "To start dashboard: ./nova dashboard start"
}

# Docker deployment
deploy_docker() {
    echo "Deploying with Docker..."

    check_docker

    if [ "$ACTION" == "start" ]; then
        echo "Building and starting containers..."
        docker-compose up -d --build

        echo -e "${GREEN}Docker deployment started!${NC}"
        echo ""
        echo "View logs: docker-compose logs -f"
        echo "View status: docker-compose ps"
        echo "Stop: docker-compose down"

    elif [ "$ACTION" == "stop" ]; then
        echo "Stopping containers..."
        docker-compose down

    elif [ "$ACTION" == "restart" ]; then
        echo "Restarting containers..."
        docker-compose restart

    elif [ "$ACTION" == "logs" ]; then
        docker-compose logs -f

    elif [ "$ACTION" == "status" ]; then
        docker-compose ps
    fi
}

# AWS deployment
deploy_aws() {
    echo "Deploying to AWS..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        echo -e "${RED}Error: AWS CLI not installed${NC}"
        exit 1
    fi

    # Build Docker image
    echo "Building Docker image..."
    docker build -t novaos-v2:latest .

    # Tag for ECR
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    AWS_REGION=${AWS_REGION:-us-east-1}
    ECR_REPO="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/novaos-v2"

    echo "Tagging image for ECR..."
    docker tag novaos-v2:latest $ECR_REPO:latest

    # Login to ECR
    echo "Logging in to ECR..."
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO

    # Push to ECR
    echo "Pushing to ECR..."
    docker push $ECR_REPO:latest

    echo -e "${GREEN}AWS deployment complete!${NC}"
    echo "Image pushed to: $ECR_REPO:latest"
}

# Cloud deployment (generic)
deploy_cloud() {
    echo "Deploying to cloud..."

    # Build production image
    docker build -t novaos-v2:production .

    echo -e "${GREEN}Production image built!${NC}"
    echo "Tag and push to your container registry"
}

# Main deployment logic
main() {
    check_env

    case $DEPLOY_TARGET in
        local)
            deploy_local
            ;;
        docker)
            deploy_docker
            ;;
        aws)
            deploy_aws
            ;;
        cloud)
            deploy_cloud
            ;;
        *)
            echo -e "${RED}Unknown deployment target: $DEPLOY_TARGET${NC}"
            echo "Valid targets: local, docker, aws, cloud"
            exit 1
            ;;
    esac
}

# Show help
if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "NovaOS V2 Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [target] [action]"
    echo ""
    echo "Targets:"
    echo "  local   - Deploy locally (default)"
    echo "  docker  - Deploy with Docker Compose"
    echo "  aws     - Deploy to AWS ECS"
    echo "  cloud   - Build for cloud deployment"
    echo ""
    echo "Actions (Docker only):"
    echo "  start   - Start containers (default)"
    echo "  stop    - Stop containers"
    echo "  restart - Restart containers"
    echo "  logs    - View logs"
    echo "  status  - View status"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh local"
    echo "  ./deploy.sh docker start"
    echo "  ./deploy.sh docker logs"
    echo "  ./deploy.sh aws"
    exit 0
fi

main
