apply migration

```bash
  docker compose --profile dev run --rm users-dev \ 
  alembic -c services/users_service/app/alembic.ini upgrade head
```

seed data

```bash
  docker compose run --rm users-dev \              
  python -m scripts.cli seed --db users --flush --flights 60 --days 14
```

run

```bash
  docker compose --profile prod up
```