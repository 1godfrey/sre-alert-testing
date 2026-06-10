# Deployment (EC2 + Docker + DuckDNS)

This covers running the backend container on a single EC2 instance, with an
optional DuckDNS hostname so you don't have to remember an IP address. The
React frontend can be built as static files and served separately (or
skipped entirely if you only need the API for alerting practice).

## 1. Overview

- One EC2 instance running the FastAPI backend in a Docker container,
  listening on port 8000 (or proxied behind port 80/443).
- Stats/metrics are kept in memory (see [Limitations](#7-limitations)) - no
  database needed.
- DuckDNS is optional and just gives the instance a stable hostname when
  its public IP can change (e.g. you're not paying for an Elastic IP).

## 2. Prerequisites

- An AWS account and an EC2 instance (a `t3.micro`/`t2.micro` on the free
  tier is plenty for this).
- Docker installed on the instance (Amazon Linux 2023: `sudo dnf install -y
  docker && sudo systemctl enable --now docker`; then add your user to the
  `docker` group or use `sudo` for the commands below).
- Security group inbound rules: allow TCP 22 (SSH, ideally restricted to
  your IP) and TCP 8000 (or 80/443 if you add a reverse proxy).

## 3. Build and run the backend container

From the repo root, on your machine or on the instance after cloning:

```bash
docker build -t sre-alert-testing-backend ./backend
docker run -d \
  --name sre-alert-testing \
  --restart unless-stopped \
  -p 8000:8000 \
  sre-alert-testing-backend
```

Check it's up:

```bash
curl http://localhost:8000/health
```

### Customizing endpoints without rebuilding

`backend/config/endpoints.yaml` is baked into the image. To change the
simulated tiers without rebuilding, mount your own copy over it:

```bash
docker run -d \
  --name sre-alert-testing \
  --restart unless-stopped \
  -p 8000:8000 \
  -v "$(pwd)/backend/config/endpoints.yaml:/app/config/endpoints.yaml:ro" \
  sre-alert-testing-backend
```

Other settings (`DEFAULT_ERROR_STATUS_CODE`, `CORS_ALLOWED_ORIGINS`, etc. -
see `.env.example`) can be passed with `--env-file .env` or `-e KEY=value`.

## 4. Running on EC2

1. SSH into the instance.
2. Install Docker (see [Prerequisites](#2-prerequisites)).
3. Clone this repo (or just copy `backend/`).
4. Build and run as in step 3, above.
5. Confirm from your own machine: `curl http://<ec2-public-ip>:8000/health`.

## 5. DuckDNS setup (optional)

1. Create a free subdomain at https://www.duckdns.org (e.g.
   `sre-alert-testing.duckdns.org`) pointed at your EC2 instance's public IP.
2. If the instance has a static **Elastic IP**, you're done - just update
   the DuckDNS record once.
3. If the IP can change (e.g. instance stop/start without an Elastic IP),
   add a cron job on the instance to keep DuckDNS updated:

   ```bash
   # /etc/cron.d/duckdns - runs every 5 minutes
   */5 * * * * root curl -fsS "https://www.duckdns.org/update?domains=YOURDOMAIN&token=YOURTOKEN&ip=" >/dev/null
   ```

### Optional: reverse proxy + TLS (future work)

For a real `https://sre-alert-testing.duckdns.org/health` URL, put nginx or
Caddy in front of the container on ports 80/443 and obtain a certificate via
Let's Encrypt (Caddy does this automatically). Not required for local
alerting tools that can hit `http://<ip-or-host>:8000` directly.

## 6. Updating the deployment

```bash
git pull
docker build -t sre-alert-testing-backend ./backend
docker stop sre-alert-testing && docker rm sre-alert-testing
docker run -d --name sre-alert-testing --restart unless-stopped -p 8000:8000 sre-alert-testing-backend
```

## 7. Limitations

- **In-memory stats**: `/stats` and `/metrics` counters live in process
  memory. They reset on container restart/redeploy and won't be consistent
  if you run more than one `uvicorn` worker. Run with a single worker
  (the default `CMD` in the Dockerfile already does this) - this tool is a
  practice harness, not a production service.
- **No persistence/auth**: there's no database and no authentication. Don't
  expose it more broadly than your own monitoring tools need.
