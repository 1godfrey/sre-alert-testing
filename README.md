# sre-alert-testing

A small practice harness for SRE alerting and incident-dashboard
configuration. The FastAPI backend exposes a handful of endpoints that
simulate different SLA tiers - each request independently succeeds (HTTP
200) or fails (a configured error status code) according to a target
uptime percentage. Point your monitoring stack (Prometheus/Alertmanager,
Grafana, UptimeRobot, PagerDuty, etc.) at these endpoints to practice
configuring alert thresholds, burn-rate alerts, and incident dashboards
against realistic-ish error rates.

A minimal React frontend shows live observed-vs-target uptime for each
endpoint.

## Simulated endpoints

| Name     | Path           | Target uptime | Error status code |
|----------|----------------|---------------|--------------------|
| tier-99  | `/sim/tier-99` | 99%           | 500                |
| tier-95  | `/sim/tier-95` | 95%           | 503                |
| tier-75  | `/sim/tier-75` | 75%           | 503                |

Each is configured in [`backend/config/endpoints.yaml`](backend/config/endpoints.yaml) -
add, remove, or retarget endpoints there (no code changes needed).

## API overview

| Method | Path        | Description                                                            |
|--------|-------------|-------------------------------------------------------------------------|
| GET    | `/health`   | Always returns 200. Confirms the harness itself is reachable.          |
| GET    | `/`         | Lists configured simulated endpoints (`name`, `path`, `target_uptime`).|
| GET    | `/sim/*`    | Simulated endpoints - see table above.                                  |
| GET    | `/stats`    | JSON: per-endpoint request counts and observed success ratio.          |
| GET    | `/metrics`  | Prometheus exposition format, for scraping.                            |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate     # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

The API is now at http://localhost:8000 (interactive docs at
http://localhost:8000/docs).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 - it polls `/health` and `/stats` on the backend
every few seconds. Set `VITE_API_BASE_URL` (see `frontend/.env.example`) if
the backend isn't on `http://localhost:8000`.

## Configuration

Backend settings are read from environment variables / a `.env` file (see
[`.env.example`](.env.example)):

| Variable                     | Default                     | Description                                         |
|-------------------------------|------------------------------|------------------------------------------------------|
| `APP_HOST`                    | `0.0.0.0`                    | Bind host for uvicorn                                |
| `APP_PORT`                    | `8000`                       | Bind port for uvicorn                                |
| `LOG_LEVEL`                   | `info`                       | uvicorn log level                                    |
| `ENDPOINTS_CONFIG_PATH`       | `config/endpoints.yaml`      | Path to the simulated-endpoints config               |
| `DEFAULT_ERROR_STATUS_CODE`   | `503`                        | Fallback error code for endpoints that don't set one |
| `CORS_ALLOWED_ORIGINS`        | `http://localhost:5173`      | Comma-separated list of allowed CORS origins         |

## Testing

```bash
cd backend
pytest -v
```

Tests cover config validation, the probabilistic simulation logic
(deterministic via dependency-injected randomness), and the `/stats` /
`/metrics` endpoints.

## Running with Docker

```bash
docker build -t sre-alert-testing-backend ./backend
docker run -p 8000:8000 sre-alert-testing-backend
```

## Deploying to EC2

See [`docs/deployment.md`](docs/deployment.md) for running the backend on
an EC2 instance with Docker, plus optional DuckDNS setup.

## License

[MIT](LICENSE)
