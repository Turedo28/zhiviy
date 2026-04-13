#!/bin/bash

# HealthTrack Setup Verification Script

echo "=================================="
echo "HealthTrack Setup Verification"
echo "=================================="
echo ""

# Check .env file
echo "1. Checking environment configuration..."
if [ -f .env ]; then
  echo "   ✓ .env file exists"

  # Check required variables
  required_vars=(
    "TELEGRAM_BOT_TOKEN"
    "TELEGRAM_BOT_USERNAME"
    "WHOOP_CLIENT_ID"
    "WHOOP_CLIENT_SECRET"
    "ANTHROPIC_API_KEY"
    "SECRET_KEY"
  )

  for var in "${required_vars[@]}"; do
    if grep -q "^${var}=" .env; then
      echo "   ✓ ${var} is configured"
    else
      echo "   ✗ ${var} is missing"
    fi
  done
else
  echo "   ✗ .env file not found. Run: cp .env.example .env"
fi
echo ""

# Check Docker
echo "2. Checking Docker installation..."
if command -v docker &> /dev/null; then
  echo "   ✓ Docker is installed: $(docker --version)"
else
  echo "   ✗ Docker not installed"
fi
echo ""

# Check Docker Compose
echo "3. Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
  echo "   ✓ Docker Compose installed: $(docker-compose --version)"
else
  echo "   ✗ Docker Compose not installed"
fi
echo ""

# Check Python
echo "4. Checking Python..."
if command -v python3 &> /dev/null; then
  py_version=$(python3 --version)
  echo "   ✓ Python found: ${py_version}"
else
  echo "   ✗ Python 3 not installed"
fi
echo ""

# Check Node.js
echo "5. Checking Node.js..."
if command -v node &> /dev/null; then
  node_version=$(node --version)
  echo "   ✓ Node.js found: ${node_version}"
else
  echo "   ✗ Node.js not installed"
fi
echo ""

# Check project structure
echo "6. Checking project structure..."
directories=(
  "backend"
  "frontend"
  "bot"
  "backend/app"
  "backend/app/models"
  "backend/app/api"
  "backend/alembic"
  "frontend/app"
  "frontend/components"
  "frontend/lib"
)

for dir in "${directories[@]}"; do
  if [ -d "$dir" ]; then
    echo "   ✓ ${dir}/"
  else
    echo "   ✗ ${dir}/ missing"
  fi
done
echo ""

# Check important files
echo "7. Checking critical files..."
files=(
  "docker-compose.yml"
  "backend/requirements.txt"
  "backend/app/main.py"
  "backend/alembic.ini"
  "frontend/package.json"
  "frontend/next.config.js"
  "bot/main.py"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "   ✓ ${file}"
  else
    echo "   ✗ ${file} missing"
  fi
done
echo ""

echo "=================================="
echo "Verification Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Configure .env with your credentials"
echo "2. Start Docker: docker-compose up -d"
echo "3. Setup backend: cd backend && pip install -r requirements.txt && alembic upgrade head"
echo "4. Start backend: uvicorn app.main:app --reload"
echo "5. Setup frontend: cd frontend && npm install && npm run dev"
echo "6. Start bot: cd bot && python main.py"
echo ""
