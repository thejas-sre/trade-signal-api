# trade-signal-api

A Python FastAPI service that processes and caches trading signals using Redis.
This service is the common application used across all infrastructure projects
in this portfolio — providing a realistic workload for Redis benchmarking,
observability, CI/CD validation, and Kubernetes operations.

---

## Problem Statement

A trading signal processing service requires a low-latency cache layer to serve
repeated signal lookups without hitting the database on every request. Before
Redis could be placed in the critical path, its performance had to be empirically
validated. Once deployed, the service needed real-time observability, automated
release gating, and Kubernetes-based infrastructure.

---

## Architecture

    signal_generator.py
            |
            v
      trade-signal-api (FastAPI)
            |
            +---> Redis (bounded connection pool, TTL-based expiry)
            |
            +---> /metrics (Prometheus scrape endpoint)
            |
            +---> /health (liveness + readiness probe target)

---

## How To Run

Prerequisites: Docker, Docker Compose, Python 3.12

Start the service:

    git clone https://github.com/thejas-sre/trade-signal-api.git
    cd trade-signal-api
    docker compose -f docker/docker-compose.yml up --build
    curl http://localhost:8000/health

Send a signal:

    curl -X POST http://localhost:8000/signals \
      -H "Content-Type: application/json" \
      -d '{"symbol":"AAPL","action":"BUY","confidence":0.87,"timestamp":"2025-01-15T10:30:00Z"}'

Run load generator:

    pip install -r requirements.txt
    python load_generator/signal_generator.py

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| /signals | POST | Accept signal payload, write to Redis with TTL, return signal ID |
| /signals/{id} | GET | Read signal from Redis cache, return result or 404 |
| /signals/batch/lookup | GET | Batch lookup — read-heavy Redis workload |
| /health | GET | Service health with Redis connectivity check |
| /metrics | GET | Prometheus metrics — latency, cache hit rate, error rate |

---

## What This Project Demonstrates

- FastAPI service with Redis cache integration using a bounded connection pool
- Prometheus metrics endpoint exposing request latency, cache hit rate, error rate
- PII sanitizer stripping sensitive fields before any log output
- Multi-stage Docker build for lean production images
- Kubernetes-ready manifests with liveness and readiness probes
- Realistic load generator producing 10 signals per second for benchmark workloads

---

## Compliance Considerations

- sanitizer.py strips PII-adjacent fields before any log output
- No signal payload content reaches log files — only metadata is logged
- Connection pool size is configurable to prevent resource exhaustion
- All configuration via environment variables — no secrets in code

---

## Related Projects

All infrastructure projects in this portfolio operate on this service:

| Project | What It Does |
|---|---|
| redis-performance-toolkit | Validates Redis cache performance before production |
| observability-stack | Monitors this service in real time |
| release-validation-pipeline | Gates every deployment of this service |
| terraform-drift-detector | Protects the AWS infrastructure it runs on |
| kubernetes-ops-runbook | Documents how to operate this service on Kubernetes |
