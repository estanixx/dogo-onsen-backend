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

## Configuration

Environment variables:

- `DATABASE_URL`: Postgres DSN (defaults to the compose service).
- `CORS_ALLOW_ORIGINS`: Comma-separated origins allowed to call the API. Defaults to `http://localhost:3000` so the Next.js app can talk to the backend via the new API routes.

## Employee API

| Method | Path                   | Description                         |
|--------|------------------------|-------------------------------------|
| GET    | `/employee`            | List employees (supports filters).  |
| POST   | `/employee`            | Create a new employee entry.        |
| GET    | `/employee/{id}`       | Retrieve an employee by ID.         |
| PUT    | `/employee/{id}`       | Update employee fields.             |
| DELETE | `/employee/{id}`       | Remove an employee.                 |
| GET    | `/employee/clerk/{id}` | Look up an employee by Clerk user.  |

Filtering supported via query parameters: `role`, `access_status`, and `clerk_id`.

Manual commands

- Create migration inside running container:
  `docker compose exec web alembic revision --autogenerate -m "describe change"`
- Apply migrations inside running container:
  `docker compose exec web alembic upgrade head`

pgAdmin (web UI for Postgres)

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

Usage example (compose):

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
