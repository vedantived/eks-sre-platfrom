# EKS SRE Platform

## Project Purpose

EKS SRE Platform (originally scaffolded as "SRE Demo API") is a small,
realistic e-commerce-style REST API (users, products, orders) built as the
foundation for a production-style SRE demonstration project. It is
intentionally simple as a *business* application — the point is not the
domain logic, it's that the codebase is clean and structured enough to
later be containerized, deployed to AWS EKS, and used to demonstrate real
SRE practices: metrics, dashboards, SLI/SLO, error budgets, alerting,
autoscaling, load testing, failure injection, and incident response.

This repository currently covers **Phase 1 only**: a working Flask backend
running locally against SQLite, with a full test suite. No Docker,
Kubernetes, Terraform, AWS, or CI/CD is included yet — those come in later
phases (see [Future SRE Extensions](#future-sre-extensions) below).

## Architecture

The app uses the Flask **application factory** pattern, so the app can be
constructed with different configuration (development, testing, and later
production) without global state.

```
run.py                        -> loads .env, calls create_app(), runs dev server
app/__init__.py                -> create_app(): wires config, db, blueprints, logging
app/config.py                  -> Config / TestConfig, read from environment variables
app/extensions.py              -> shared SQLAlchemy `db` instance
app/models/                    -> User, Product, Order (SQLAlchemy models + relationships)
app/routes/                    -> Flask blueprints (HTTP layer only: parse, validate, respond)
app/services/order_service.py  -> order creation business logic + DB transaction
app/validation.py              -> reusable request validation helpers
app/error_handlers.py          -> typed exceptions (ValidationError, NotFoundError,
                                   ConflictError) + centralized JSON error responses
pytest.ini                     -> puts the project root on sys.path so plain `pytest` works
```

Routes stay thin: they parse the request, call validation helpers or a
service, and return a JSON response. The order-creation transaction (check
stock, deduct stock, create order, commit/rollback) lives in
`app/services/order_service.py` so it isn't tied to Flask and can be reused
or tested independently.

Because the database URL is fully driven by the `DATABASE_URL` environment
variable, swapping SQLite for Amazon RDS in a later phase requires no
application code changes.

## Development Environment

This project is developed and run inside **WSL (Ubuntu)**, not directly on
Windows, so the terminal and Python tooling behave the same way they will
later in Docker/EKS (Linux end to end). The project lives at:

```
~/projects/eks-sre-platform
```

which is inside WSL's native Linux filesystem (`/home/<user>/projects/...`),
**not** under `/mnt/c/...`. Keeping it off the Windows-mounted drive avoids
slow filesystem access and file-lock issues (e.g. from OneDrive sync).

If you ever need to reopen this project in VS Code:

```bash
cd ~/projects/eks-sre-platform
code .
```

This opens a VS Code window connected to WSL (green `WSL: Ubuntu` badge in
the bottom-left corner) with this folder as the root.

## Prerequisites

- WSL2 with an Ubuntu distribution
- Python 3.11+ (developed and tested on Python 3.12, inside WSL)
- `python3-venv` and `python3-pip` (one-time system setup, see below)

One-time system setup inside WSL, if not already installed:

```bash
sudo apt update && sudo apt install -y python3-venv python3-pip
```

## Virtual Environment Setup

From the project directory:

```bash
cd ~/projects/eks-sre-platform
python3 -m venv venv
source venv/bin/activate
```

A virtual environment (`venv`) is a private, isolated copy of Python and
its installed packages, scoped to just this project — it keeps this
project's dependencies from clashing with anything else on the system.
It is **not portable**: it hardcodes absolute paths to itself, so if the
project folder is ever moved or renamed, delete `venv/` and recreate it
with the two commands above followed by the install step below.

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

Copy the example file and adjust if needed:

```bash
cp .env.example .env
```

| Variable       | Default                    | Description                                   |
|----------------|-----------------------------|------------------------------------------------|
| `FLASK_ENV`    | `development`               | Runtime environment label                       |
| `DATABASE_URL` | `sqlite:///sre_demo.db`     | SQLAlchemy database URL. Point this at Amazon RDS (e.g. `postgresql://...`) in later phases with no code changes. |

Never commit a real `.env` file — it is already excluded via `.gitignore`.

## Database Setup

No manual migration step is required for local development. On startup,
`create_app()` calls `db.create_all()`, which creates any missing SQLite
tables automatically (stored under `instance/` by default).

## How to Run the Application

```bash
cd ~/projects/eks-sre-platform
source venv/bin/activate
python run.py
```

The API is served at `http://127.0.0.1:5000`. Keep this terminal open —
it prints a live log line for every request it handles (method, path,
status code, duration), which is useful for watching the app behave in
real time and is the format later phases will ship to Fluent Bit / ELK.

To stop the server, press `Ctrl+C` in that terminal.

## API Endpoints

**Every endpoint below except `/health` and `/ready` is prefixed with `/api`.**
A very common mistake (and the cause of most "why am I getting a 404"
questions) is requesting `/users` or `/orders` instead of `/api/users` or
`/api/orders` — see [Troubleshooting](#troubleshooting) below.

| Method | Path                  | Description                          |
|--------|------------------------|----------------------------------------|
| GET    | `/health`              | Liveness check (no DB access)          |
| GET    | `/ready`               | Readiness check (verifies DB access)   |
| POST   | `/api/users`           | Create a user                          |
| GET    | `/api/users`           | List all users                         |
| GET    | `/api/users/<id>`      | Get a single user                      |
| POST   | `/api/products`        | Create a product                       |
| GET    | `/api/products`        | List all products                      |
| GET    | `/api/products/<id>`   | Get a single product                   |
| POST   | `/api/orders`          | Create an order                        |
| GET    | `/api/orders`          | List all orders                        |
| GET    | `/api/orders/<id>`     | Get a single order                     |

### Status Codes

- `200` — successful GET
- `201` — successful creation
- `400` — invalid request (validation failure, e.g. insufficient stock)
- `404` — resource not found, **or the URL path itself doesn't exist**
- `409` — conflict (e.g. duplicate email)
- `500` — unexpected server error (no stack trace exposed)

## How to Access the APIs

The server must be running first — see
[How to Run the Application](#how-to-run-the-application). Everything
below assumes it's already up at `http://127.0.0.1:5000`.

### Base URL

- **From inside WSL** (a terminal), or **from your Windows browser**,
  `http://127.0.0.1:5000` works for both — WSL2 automatically forwards
  `localhost` between Windows and the Linux VM.
- WSL's internal IP (shown by `hostname -I`, e.g. `172.24.103.76`) also
  works from a Windows browser, but that IP can change whenever WSL
  restarts. Prefer `127.0.0.1` so you don't have to look it up again.

### Ways to call the API

1. **curl**, from a WSL terminal — fastest for both `GET` and `POST`,
   and what all examples below use.
2. **A browser**, for `GET` requests only (typing a URL is a `GET`).
   Good for quickly checking `/health`, `/ready`, `/api/users`,
   `/api/products`, `/api/orders`, or `/api/users/1`.
3. **Postman / Insomnia / Thunder Client**, if you prefer a GUI —
   point it at `http://127.0.0.1:5000`, set the method (`GET`/`POST`),
   and for `POST` requests set the body type to **raw / JSON** and the
   `Content-Type: application/json` header.

### Health & Readiness

```bash
curl http://127.0.0.1:5000/health
# {"status": "healthy"}

curl http://127.0.0.1:5000/ready
# {"status": "ready"}
```

### Users

**Create a user:**
```bash
curl -X POST http://127.0.0.1:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Nayan", "email": "nayan@example.com"}'
```
```json
{
  "id": 1,
  "name": "Nayan",
  "email": "nayan@example.com",
  "created_at": "2026-08-11T09:11:52.761424"
}
```

**List all users:**
```bash
curl http://127.0.0.1:5000/api/users
```

**Get a single user by id:**
```bash
curl http://127.0.0.1:5000/api/users/1
```

### Products

**Create a product:**
```bash
curl -X POST http://127.0.0.1:5000/api/products \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 57800, "stock": 10}'
```
```json
{
  "id": 1,
  "name": "Laptop",
  "price": 57800.0,
  "stock": 10,
  "created_at": "2026-08-11T09:12:03.112233"
}
```

**List all products:**
```bash
curl http://127.0.0.1:5000/api/products
```

**Get a single product by id:**
```bash
curl http://127.0.0.1:5000/api/products/1
```

### Orders

**Create an order** (requires an existing `user_id` and `product_id`,
and enough stock — placing this reduces the product's `stock`):
```bash
curl -X POST http://127.0.0.1:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product_id": 1, "quantity": 2}'
```
```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 1,
  "quantity": 2,
  "total_price": 115600.0,
  "status": "confirmed",
  "created_at": "2026-08-11T09:12:32.312522"
}
```

**List all orders:**
```bash
curl http://127.0.0.1:5000/api/orders
```

**Get a single order by id:**
```bash
curl http://127.0.0.1:5000/api/orders/1
```

### Error responses

These are correct, expected responses — not bugs — demonstrating the
centralized JSON error handling:

```bash
# Non-existent resource -> 404
curl -i http://127.0.0.1:5000/api/users/999
# HTTP/1.1 404 NOT FOUND
# {"error": "User not found"}

# Duplicate email -> 409
curl -i -X POST http://127.0.0.1:5000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Someone", "email": "nayan@example.com"}'
# HTTP/1.1 409 CONFLICT
# {"error": "A user with email 'nayan@example.com' already exists"}

# Ordering more than available stock -> 400
curl -i -X POST http://127.0.0.1:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "product_id": 1, "quantity": 9999}'
# HTTP/1.1 400 BAD REQUEST
# {"error": "Insufficient stock for product 'Laptop': requested 9999, available 8"}
```

Use `curl -i` (as above) instead of plain `curl` when you want to see the
HTTP status code in the response along with the JSON body.

## How to Run Tests

Tests run against an isolated in-memory SQLite database (see
`tests/conftest.py` / `TestConfig`), so they never touch your local
`sre_demo.db`.

```bash
cd ~/projects/eks-sre-platform
source venv/bin/activate
pytest -v
```

`pytest.ini` (in the project root) sets `pythonpath = .`, which is what
lets the bare `pytest` command find the `app` package. Without it, only
`python -m pytest` would work, because `-m` automatically adds the current
directory to Python's import path while a bare `pytest` invocation does not.

## Expected Test Result

All 24 tests should pass:

```
======================= 24 passed in 0.5s =======================
```

## Troubleshooting

**"I'm getting 404 on `/users`, `/orders`, or `/`"**
This is expected, not a bug. Every resource endpoint lives under `/api/...`
(e.g. `/api/users`, not `/users`). There is also no route for `/` at all —
this is a pure API with no homepage. Double-check the path against the
[API Endpoints](#api-endpoints) table above.

**"`ERR_CONNECTION_REFUSED` in the browser"**
The server isn't running. Start it with `python run.py` (see
[How to Run the Application](#how-to-run-the-application)) and keep that
terminal open.

**"I renamed/moved the project folder and now nothing works"**
`venv/` hardcodes absolute paths to itself and breaks when the folder is
renamed or moved. Delete it and recreate:
```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Also clear any stale bytecode cache referencing the old path:
```bash
find . -type d -name "__pycache__" -not -path "./venv/*" -exec rm -rf {} +
rm -rf .pytest_cache
```

## What to Verify Manually Before Moving to Phase 2

1. `python run.py` starts without errors and logs a clean startup line.
2. `GET /health` returns `200 {"status": "healthy"}`.
3. `GET /ready` returns `200 {"status": "ready"}` while the DB is reachable.
4. Creating a user, product, and order via `curl` (or Postman) works end to
   end, and the product's `stock` decreases after an order is placed.
5. Creating a user with a duplicate email returns `409`.
6. Requesting a non-existent user/product/order returns `404` with a JSON
   `{"error": "..."}` body (never an HTML error page).
7. Creating an order with insufficient stock returns `400` and does **not**
   change the product's stock (i.e. the transaction rolled back correctly).
8. The console log output is readable, one line per request, with method,
   path, and status.
9. `pytest -v` passes all 24 tests locally.

Phase 1 is complete once all of the above are verified — and they have been.

## Future SRE Extensions

The following are explicitly **out of scope** for Phase 1 and will be added
in later phases, without requiring a rewrite of this application:

1. Docker
2. AWS ECR
3. Terraform
4. AWS VPC
5. EKS
6. Kubernetes
7. Helm
8. GitHub Actions
9. Argo CD
10. Prometheus
11. Grafana
12. ELK
13. SLI/SLO
14. Error Budgets
15. Alerting
16. HPA (Horizontal Pod Autoscaling)
17. Load Testing
18. Failure Injection
19. Incident Management
20. RCA / Postmortems

The application code is intentionally structured (application factory,
thin routes, isolated service layer, environment-driven config) so that
future additions such as `/metrics`, `/load`, `/slow`, `/error`, and
`/db-test` endpoints can be added cleanly later.
# eks-sre-platfrom
