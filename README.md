Weather API Application

A simple asynchronous REST API built with FastAPI that fetches current weather data, caches results in a database, logs query history, and includes a basic IP-based rate limiter. 

Weather Fetching: Retrieves current weather for a specified city via the `/get_weather` endpoint.
Database Caching: To minimize external API calls, successful responses are stored in a PostgreSQL database with a 5-minute expiration (TTL). If the same city is requested within this window, data is served directly from the local DB.
History Log: The `/history` endpoint tracks all handled requests. It supports offset pagination (`page` and `size` parameters) and case-insensitive substring filtering by city name (using SQL `ILIKE`).
In-Memory Rate Limiter: A simple custom middleware that limits requests from a single IP address (default is 30 requests per minute) using an in-memory dictionary. If exceeded, it returns a `429 Too Many Requests` status.

Tech Stack

* Python 3.12+
* FastAPI / Uvicorn
* SQLAlchemy 2.0 (Async) & `asyncpg`
* PostgreSQL 15
* Pytest & `httpx` (for integration tests)
* Docker & Docker Compose

Getting Started (Docker)

The application and database are containerized together. The web container is configured to start after the database port becomes available.

1. **Clone the repository and navigate to the root directory.**
2. **Create a local `.env` file:**
   ```bash
   cp .env.example .env

Open the .env file and past:
* `DB_USER=`
* `DB_PASS=`
* `DB_HOST=`
* `DB_PORT=`
* `DB_NAME=`
* `API_KEY=`
* `DB_URL=postgresql+asyncpg://user/pass@host:port/db_name`

Run the app:
  `docker-compose up --build`

**Running tests locally**
In the project core create virtual environment, install requirements.txt, execute pytest:
 * `python -m venv venv && source venv/bin/activate`
 * `pip install -r requirements.txt`
 * `python -m pytest -v`
