# HealthTrack — Швидкий старт

## Крок 1: Підготовка

### Встанови необхідне:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (для PostgreSQL + Redis)
- [Node.js 18+](https://nodejs.org/) (для фронтенду)
- [Python 3.11+](https://www.python.org/downloads/) (для бекенду та бота)
- [Git](https://git-scm.com/)

## Крок 2: Налаштування .env

```bash
cd healthtrack
cp .env.example .env
```

Відкрий `.env` і заповни свої ключі:
```
TELEGRAM_BOT_TOKEN=<твій токен від @BotFather>
TELEGRAM_BOT_USERNAME=<username бота без @>
WHOOP_CLIENT_ID=<Client ID з developer-dashboard.whoop.com>
WHOOP_CLIENT_SECRET=<Client Secret>
ANTHROPIC_API_KEY=<API ключ з console.anthropic.com>
SECRET_KEY=<будь-який рандомний рядок 32+ символів>
```

## Крок 3: Запуск БД

```bash
docker-compose up -d
```

Перевір що працює:
```bash
docker ps  # має показати healthtrack_postgres і healthtrack_redis
```

## Крок 4: Бекенд

```bash
cd backend

# Створи віртуальне середовище
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows

# Встанови залежності
pip install -r requirements.txt

# Створи першу міграцію
alembic revision --autogenerate -m "initial_tables"

# Застосуй міграцію
alembic upgrade head

# Запусти сервер
uvicorn app.main:app --reload --port 8000
```

Перевір: http://localhost:8000/docs (Swagger UI)

## Крок 5: Фронтенд

```bash
cd frontend

# Встанови залежності
npm install

# Запусти dev-сервер
npm run dev
```

Перевір: http://localhost:3000

## Крок 6: Telegram бот

```bash
cd bot

# Активуй те саме venv або створи нове
pip install -r requirements.txt

# Запусти бота
python main.py
```

## Перевірка

1. http://localhost:3000 — Landing page з Warm Ember дизайном
2. http://localhost:8000/docs — API документація
3. http://localhost:8000/health — Health check
4. Напиши `/start` своєму боту в Telegram

## Структура проекту

```
healthtrack/
├── docker-compose.yml      # PostgreSQL + Redis
├── .env                    # Твої секрети (не коміть!)
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI додаток
│   │   ├── core/           # Config, DB, Security
│   │   ├── models/         # SQLAlchemy моделі
│   │   ├── api/v1/         # REST endpoints
│   │   └── services/       # Бізнес-логіка
│   ├── alembic/            # Міграції БД
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js сторінки
│   ├── components/         # React компоненти
│   ├── lib/                # Утиліти, API клієнт
│   └── package.json
└── bot/
    ├── main.py             # Aiogram бот
    ├── handlers/           # Обробники команд
    ├── keyboards/          # Клавіатури
    └── i18n/               # Переклади
```
