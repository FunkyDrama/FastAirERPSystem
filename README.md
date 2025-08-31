apply migration

```bash
  docker compose --profile dev run --rm users-dev alembic -c services/users_service/app/alembic.ini upgrade head
```

seed data

```bash
  docker compose run --rm users-dev python -m scripts.cli seed --db users --flush --flights 60 --days 14
```

run

```bash
  docker compose --profile prod up
```

confirm payment intent
```bash
  stripe payment_intents confirm {pi_number} --payment-method pm_card_visa
```

start stripe webhook

```bash
  stripe listen --forward-to http://localhost:8001/api/v1/payments/stripe/webhook
```

run all services

```bash
  docker compose --profile dev up
```