#!/bin/bash
# Quick test script for Milton Overton AI Publicist

echo "=================================="
echo "Milton Overton AI Publicist"
echo "Quick System Test"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the milton-publicist directory"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating from template..."
    cp .env.template .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY=sk-ant-xxxxx"
    echo "   - DATABASE_URL=postgresql://..."
    echo ""
    echo "Press Enter after you've updated .env..."
    read
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || source venv/Scripts/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Run system test
echo "Running system test..."
echo ""
python scripts/test_system.py

echo ""
echo "=================================="
echo "Test complete!"
echo "=================================="
