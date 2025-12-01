# Dogo Onsen Backend

FastAPI project that powers the Dogo Onsen employee panel with async SQLModel, Postgres, Alembic, and Docker. It now exposes CRUD routes for services and employees [WIP].

## Want to learn how to build this?

Check out the [post](https://testdriven.io/blog/fastapi-sqlmodel/).

## Want to use this project?

```sh
docker-compose up -d --build
docker-compose exec web alembic upgrade head
```

Sanity check: [http://localhost:8004/ping](http://localhost:8004/ping)

## Manual commands

- Create migration inside running container:
  `docker compose exec web alembic revision --autogenerate -m "v1"`
- Apply migrations inside running container:
  `docker compose exec web alembic upgrade head`
- Undo last migration:
  `docker compose exec web alembic downgrade -1`
- Reset all migrations (downgrade to base):
  `docker compose exec web alembic downgrade base`

## pgAdmin (web UI for Postgres)

- The compose setup includes `pgadmin` exposed on port `8080`.
- Default credentials:
  - Email: `admin@local`
  - Password: `admin`
- To connect to the database from pgAdmin add a new server with these settings:
  - Host: `db`
  - Port: `5432`
  - Maintenance DB: `postgres` (or `foo` if you prefer)
  - Username: `postgres`
  - Password: `postgres`

## Usage example (compose)

```sh
# bring containers up
docker compose up -d --build

# open pgAdmin in your browser: http://localhost:8080
```

Security note:

- The pgAdmin credentials above are intended for local development only. Change them in `docker-compose.yml` for production or restrict access to the service.

## Want to watch logs?

```sh
docker logs dogo-onsen-backend-web-1 --follow
```

## Tests

Unit tests are included under `project/tests/unit/` and exercise service logic, inventory helpers, employee flows and the device cookie middleware.

- How to run locally (recommended):
  - Create a Python environment and install dev requirements:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -r project/requirements-dev.txt
    ```
  - Run pytest from the `project/` folder:
    ```bash
    cd project
    pytest -q
    ```

- Run inside Docker (same environment used during development):

  ```bash
  cd /path/to/dogo-onsen-backend
  docker-compose build tests
  docker-compose run --rm tests
  ```

What tests were added

- `test_service_service.py` — service availability and time-slot helpers
- `test_service_create.py` — service creation logic
- `test_inventory_item.py` & `test_inventory_create.py` — inventory listing and creation helpers
- `test_employee_service.py`, `test_employee_create_unique.py`, `test_employee_process_clerk_webhook.py` — employee creation and Clerk webhook handling
- `test_device_cookie_middleware.py` — middleware that parses device cookie

Test tooling notes

- Tests use `pytest`, `pytest-asyncio` and `pytest-mock`. A shared `conftest.py` fixture provides a mocked `AsyncSession` to avoid hitting a real database during unit tests.

CI (GitHub Actions)

- A workflow was added to run these tests on push and pull requests: `.github/workflows/backend-tests.yml` (runs Python 3.11 and executes `pytest`).

Performance tests

Performance tests use [k6](https://k6.io/) to validate backend API endpoints directly.

- **Location**: `tests/performance/load_test.js`
- **Run locally**:
  ```bash
  # Ensure backend is running on http://localhost:8004
  k6 run tests/performance/load_test.js
  ```
- **Scenarios**:
  - Read load: Ramping VUs reading employee list.
  - Write load: Constant VUs creating new employees.
  
- **CI**: Runs via `.github/workflows/performance-tests.yml`.
