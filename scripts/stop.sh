#!/bin/bash

# Salla Price Optimizer - Stop Script

echo "🛑 Stopping Salla Price Optimizer..."
echo ""

# Stop all services
docker-compose down

echo ""
echo "✅ All services stopped"
echo ""
echo "💡 To start again, run: ./start.sh"
echo "💡 To remove all data, run: docker-compose down -v"
echo ""
