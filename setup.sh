#!/bin/bash

echo "🚀 NovaOS V2 Setup"
echo "=================="

# Check Python
echo ""
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3."
    exit 1
fi
echo "✅ Python 3 found"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"

# Check API key
echo ""
echo "Checking Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY not set"
    echo ""
    echo "Please set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    echo "Or add to ~/.zshrc for permanent setup:"
    echo "  echo 'export ANTHROPIC_API_KEY=\"your-key-here\"' >> ~/.zshrc"
    echo "  source ~/.zshrc"
else
    echo "✅ API key is set"
fi

# Make CLI executable
echo ""
echo "Making CLI executable..."
chmod +x cli.py
echo "✅ CLI ready"

# Create alias helper
echo ""
echo "Setting up alias..."
echo ""
echo "Add this to your ~/.zshrc for easy access:"
echo "  alias nova='/Users/krissanders/novaos-v2/cli.py'"
echo ""
echo "Then run: source ~/.zshrc"
echo ""

# Test
echo "Testing installation..."
python3 cli.py status > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ NovaOS V2 is ready!"
    echo ""
    echo "Quick start:"
    echo "  ./cli.py status    # System overview"
    echo "  ./cli.py costs     # Cost dashboard"
    echo "  ./cli.py revenue   # Revenue tracking"
    echo ""
    echo "Read QUICKSTART.md for detailed guide"
    echo ""
    echo "🎯 Target: $200K/month | AI costs <5%"
    echo ""
    echo "Let's build! 🚀"
else
    echo "⚠️  Setup complete but test failed"
    echo "Check that ANTHROPIC_API_KEY is set correctly"
fi
