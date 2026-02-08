#!/bin/bash

# Salla Price Optimizer - Quick Start Script
# This script helps you get started quickly with Docker

set -e

echo "🛍️  Salla Price Optimizer - Docker Quick Start"
echo "================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed!"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker is installed"
echo "✅ Docker Compose is installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file and add your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - TAVILY_API_KEY"
    echo ""
    read -p "Press Enter after you've updated .env file..."
fi

# Verify API keys are set
if ! grep -q "OPENAI_API_KEY=sk-" .env; then
    echo "⚠️  Warning: OPENAI_API_KEY not set in .env"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🔨 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Access Points:"
echo "   - API:       http://localhost:8000"
echo "   - OAuth:     http://localhost:8000/oauth/authorize"
echo "   - Dashboard: http://localhost:8501"
echo "   - Flower:    http://localhost:5555"
echo "   - API Docs:  http://localhost:8000/docs"
echo ""
echo "📋 Useful Commands:"
echo "   - View logs:    docker-compose logs -f"
echo "   - Stop:         docker-compose down"
echo "   - Restart:      docker-compose restart"
echo ""
echo "📚 Documentation:"
echo "   - DOCKER_DEPLOYMENT.md"
echo "   - SAAS_DEPLOYMENT_GUIDE.md"
echo ""
echo "🎉 Ready to onboard your first store!"
echo "   Visit: http://localhost:8000/oauth/authorize"
echo ""
