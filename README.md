# Habits Tracker

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
