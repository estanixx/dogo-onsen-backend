docker compose exec web alembic downgrade base
rm -rf project/migrations/versions/*.py
docker compose exec web alembic revision --autogenerate -m "v1"
docker compose exec web alembic upgrade head