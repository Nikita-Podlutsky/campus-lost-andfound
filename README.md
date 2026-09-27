# Campus Lost & Found

Приложение для поиска и публикации потерянных и найденных вещей.

Backend написан на FastAPI, PostgreSQL, SQLAlchemy и Alembic.

## Запуск backend

Нужны Python 3.11+, Docker Desktop и uv.

Если uv не установлен:

```powershell
winget install --id=astral-sh.uv -e
```

Из корня проекта выполните:

```powershell
Set-Location .\backend

uv sync --extra dev

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
}

docker desktop start
docker compose up -d db

uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Команда docker compose up -d db запускает PostgreSQL и создаёт пустую базу. Команда uv run alembic upgrade head создаёт в ней таблицы, внешние ключи и индексы.

Параметры подключения находятся в backend/.env. Пример без реальных секретов находится в backend/.env.example.

После запуска:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Проверка

В отдельном терминале:

```powershell
Set-Location .\backend

uv run alembic current
uv run alembic check
uv run pytest -p no:cacheprovider
uv run ruff check .

Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/health/db
```

Остановить PostgreSQL:

```powershell
docker compose down
```

Удалить PostgreSQL вместе с локальными данными:

```powershell
docker compose down -v
```

## API

Базовый адрес: /api/v1.

- Пользователи: /users
- Категории: /categories
- Объявления: /listings
- Проверка API: /health
- Проверка базы: /health/db

Для пользователей, категорий и объявлений реализованы создание, чтение, изменение и удаление.

## Frontend

Из корня проекта:

```powershell
npm install
npm run dev
```

Frontend доступен по адресу http://127.0.0.1:5173. Сейчас он использует моковые данные и ещё не подключён к backend.
