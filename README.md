# FastAir — Multi-Service Flight Booking & Ops

A production-like demo of an airline system with **two React frontends** (Customers & Staff), **two FastAPI backends** (Users & Staff), **PostgreSQL** databases, and **Celery workers** for notifications — all orchestrated with **Docker Compose**.

---

## ✨ Features at a glance

* **Customers**

  * Browse flights, book, pay, see dashboard
  * Email tickets with embedded **QR-code**
* **Staff**

  * Role-based panels: **Supervisor**, **Check-in**, **Gate**
  * Create flights, assign seats, check-in & boarding flows
* **Platform**

  * JWT auth with access/refresh
  * Stripe Payment Intents + webhook
  * Celery workers for emails & staff sync
  * Postgres per service

---

## 📦 Repo layout (high level)

```
services/
  users_service/         # FastAPI (customers)
  staff_service/         # FastAPI (staff)
notifications_service/ # Celery workers (emails, staff sync)
frontend/
  customer/              # React app (customers)
  staff/                 # React app (staff)
scripts/
  cli.py                 # seeding/maintenance helpers
```

---

## 🚀 Quick start

### 1) Run all services (dev)

```bash
docker compose --profile dev up
```

This brings up:

* users-service + users workers
* staff-service + staff workers
* Postgres DBs
* Frontends (if configured in the compose)

> Access:
>
> * Customer app: `http://localhost:5173`
> * Staff app:    `http://localhost:5174`
> * Users API:    `http://localhost:8001/api/v1`
> * Staff API:    `http://localhost:8003/api/v1/staff`

### 2) Apply migrations (users DB)

```bash
docker compose --profile dev run --rm users-dev \
  alembic -c services/users_service/app/alembic.ini upgrade head
```

### 3) Seed demo data

```bash
docker compose run --rm users-dev \
  python -m scripts.cli seed --db users --flush --flights 60 --days 14
```

### 4) Stripe webhook (local)

```bash
stripe listen --forward-to http://localhost:8001/api/v1/payments/stripe/webhook
```

### 5) Confirm a test PaymentIntent

```bash
stripe payment_intents confirm {pi_number} --payment-method pm_card_visa
```

### 6) Run in production profile (minimal)

```bash
docker compose --profile prod up
```

---

## 🔐 Auth & roles

* **Customers**: HTTP-only cookies, same-site.
* **Staff**: Same pattern, plus **role** claim (`SUPERVISOR`, `CHECKIN_MANAGER`, `GATE_MANAGER`) used by the staff UI to show the right panels/buttons.

> ⚠️ If you rebuild containers without persistent token store, **refresh tokens are lost** and you’ll get `401` on refresh until users log in again. Use a persistent Redis volume if you want refresh tokens to survive restarts.

---

## 🧭 Staff UI role-based navigation

The staff frontend reads the **role** returned by `/auth/login` and conditionally renders:

* **Supervisor**: flights CRUD, revenue, staff management
* **Check-in manager**: check-in panel, passenger lists
* **Gate manager**: boarding panel, scanned passengers

(You can keep shared components and guard menus/routes with role checks rather than duplicating pages.)

---

## 🛠️ Useful commands (recap)

**Apply migrations**

```bash
docker compose --profile dev run --rm users-dev \
  alembic -c services/users_service/app/alembic.ini upgrade head
```

**Seed data**

```bash
docker compose run --rm users-dev \
  python -m scripts.cli seed --db users --flush --flights 60 --days 14
```

**Run everything (dev)**

```bash
docker compose --profile dev up
```

**Run (prod)**

```bash
docker compose --profile prod up
```

**Start Stripe webhook**

```bash
stripe listen --forward-to http://localhost:8001/api/v1/payments/stripe/webhook
```

**Confirm payment intent**

```bash
stripe payment_intents confirm {pi_number} --payment-method pm_card_visa
```

---

## ⚙️ Environment

Create `.env` files per service (see defaults in settings). Typical variables:

```
POSTGRES_USER=fastair
POSTGRES_PASSWORD=fastair
POSTGRES_DB=fastair_users
POSTGRES_HOST=users_db
POSTGRES_PORT=5432

JWT_SECRET=supersecret
STRIPE_SECRET_KEY=sk_test_...
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
EMAIL_FROM="FastAir <noreply@fastair.test>"
```

> For **persistent tokens** across restarts, run Redis with a **volume** and point your TokenStore to it.

---

## 🧪 Troubleshooting

* **401 on `/auth/refresh` after container rebuild**

  * Refresh tokens were stored in memory or ephemeral Redis → they’re gone.
    ➜ Use Redis with a volume *or* accept forced re-login after deployments.

* **`MissingGreenlet` / async lazy loads**

  * Ensure you eagerly load relations in async routes: `selectinload/joinedload` on the **same** statement and don’t touch lazy relationships outside the session scope.

* **Pydantic validation for UUID**

  * If your DTO expects `str` but model has `UUID`, either cast in the schema (`field_serializer`) or set `from_attributes=True` and change field type to `UUID`.

---

## 📜 License

MIT (or your choice).
