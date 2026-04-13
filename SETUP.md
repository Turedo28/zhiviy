# HealthTrack Setup Guide

## Project Overview

HealthTrack is a comprehensive health tracking platform featuring:
- **Next.js Frontend**: Modern dark-themed UI with real-time nutrition tracking
- **FastAPI Backend**: Async Python API with Claude AI integration
- **Telegram Bot**: Aiogram-based bot for on-the-go meal logging
- **Database**: PostgreSQL 15 with Redis caching
- **AI Integration**: Claude Vision for food photo analysis

## Architecture

```
healthtrack/
├── frontend/              # Next.js 14 app (port 3000)
├── backend/              # FastAPI app (port 8000)
│   ├── app/
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   └── core/         # Config, DB, security
│   └── alembic/          # Database migrations
├── bot/                  # Aiogram telegram bot
├── docker-compose.yml    # PostgreSQL + Redis
└── .env.example          # Environment template
```

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- Telegram Bot (get from @BotFather)
- Claude API key (from https://console.anthropic.com)

## Quick Start

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and fill in:
# - TELEGRAM_BOT_TOKEN
# - ANTHROPIC_API_KEY
# - Other service credentials
```

### 2. Database & Cache

```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify containers are running
docker ps
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000`
API docs: `http://localhost:8000/docs`

### 4. Frontend Setup

```bash
cd frontend

# Copy environment
cp .env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
# NEXT_PUBLIC_TELEGRAM_BOT_ID=your_bot_id

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend available at `http://localhost:3000`

### 5. Telegram Bot Setup

```bash
cd bot

# Install dependencies (use same venv as backend or create new one)
pip install python-dotenv aiogram httpx

# Run bot
python main.py
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/telegram` - Telegram login
- `GET /api/v1/auth/me` - Current user info

### Users
- `GET /api/v1/users/me` - Get profile
- `PUT /api/v1/users/me` - Update profile
- `PUT /api/v1/users/me/onboarding` - Complete onboarding

### Meals
- `GET /api/v1/meals` - List meals
- `POST /api/v1/meals` - Create meal
- `POST /api/v1/meals/analyze` - Analyze food photo
- `DELETE /api/v1/meals/{id}` - Delete meal

### Integrations
- `GET /api/v1/integrations/whoop/auth-url` - WHOOP OAuth
- `GET /api/v1/integrations/whoop/callback` - OAuth callback
- `GET /api/v1/integrations/whoop/status` - Connection status
- `POST /api/v1/integrations/whoop/sync` - Manual sync

## Database Schema

### Core Tables
- **users**: User profiles with health metrics
- **meals**: Nutrition logs
- **water_logs**: Hydration tracking
- **supplements**: Supplement management
- **body_metrics_history**: Historical body data

### WHOOP Integration
- **whoop_tokens**: OAuth tokens
- **whoop_sleep**: Sleep data
- **whoop_recovery**: Recovery scores
- **whoop_workouts**: Training data

### Reports & Recommendations
- **blood_tests**: Blood work uploads
- **biomarkers**: Extracted blood markers
- **weekly_reports**: Automated reports
- **recommendations**: Personalized advice

## Key Features

### Food Photo Analysis
- Upload meal photos via web or Telegram
- Claude Vision AI extracts nutrition info
- Support for multiple languages (UK/EN)

### Health Integration
- WHOOP API integration for sleep, recovery, training
- Blood work photo parsing
- Body metrics tracking

### Smart Recommendations
- AI-powered personalized health advice
- Based on nutrition, sleep, activity data
- Delivered via Telegram & web dashboard

### Telegram Bot
- /start - Welcome & language selection
- Add Meal - Photo-based meal logging
- Statistics - Daily health summary
- Settings - Preference management

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests
cd frontend
npm test
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Revert last migration
alembic downgrade -1
```

### Frontend Build

```bash
cd frontend
npm run build
npm start
```

## Deployment

### Docker Build

```bash
# Backend
docker build -t healthtrack-backend ./backend

# Frontend
docker build -t healthtrack-frontend ./frontend

# Bot
docker build -t healthtrack-bot ./bot
```

### Production Environment

Update `.env` with production values:
```
DEBUG=false
API_BASE_URL=https://api.healthtrack.com
FRONTEND_URL=https://healthtrack.com
SECRET_KEY=<generate-random-secret>
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify credentials in .env
# DATABASE_URL=postgresql+asyncpg://healthtrack:healthtrack_dev@localhost:5432/healthtrack
```

### API Errors
```bash
# Check backend logs
docker logs healthtrack_postgres

# Verify migrations ran
alembic current
```

### Frontend Issues
```bash
# Clear Next.js cache
rm -rf frontend/.next

# Reinstall dependencies
cd frontend && npm install

# Check API connectivity
curl http://localhost:8000/health
```

## Security Notes

- Never commit `.env` file
- Rotate `SECRET_KEY` in production
- Use HTTPS in production
- Validate all user inputs
- Store sensitive data encrypted
- Use environment variables for secrets

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at `/api/v1/docs`
3. Check backend logs for errors
4. Verify all services are running: `docker ps`
