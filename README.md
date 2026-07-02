# Habits Tracker

Personal log tracker that turns free-form text messages into structured records.

Write what you did in plain language — the app is able to parse an expense, activity, event.

## Roadmap

- [ ] Database migrations (Alembic)
- [ ] Analytics and stats (spending by category, activity trends, streaks)
- [ ] Correction flow — review and confirm what the LLM parsed before saving

## Setup

1. Clone the repository
```bash
   git clone https://github.com/nrzhenev/habit_tracker.git
   cd habits-tracker
```

2. Copy the environment file and fill in the values
```bash
   cp .env.example .env
```

3. Install dependencies
```bash
   uv sync
```

## Running

### With Docker

```bash
docker compose -f compose.dev.yaml up --build
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`.

## Environment

"POSTGRES_HOST"
"POSTGRES_PORT"
"POSTGRES_USER"
"POSTGRES_PASSWORD"
"POSTGRES_DB"
"SECRET_KEY" - JWT secret key
"GROQ_API_KEY" - Your GROQ LLM API key

## API testing

Ready-to-use request collection for [Bruno](https://www.usebruno.com/) is available in `bruno/`.

1. From terminal open `bruno/` folder as a collection
```bash
   bruno bruno
```
2. Select the `local` environment (or create your own based on `environments/`)
3. Register a user via `Auth → Register`, then log in to get an access token
