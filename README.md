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
  `docker compose exec web alembic revision --autogenerate -m "describe change"`
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

## Usage example (compose):

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
