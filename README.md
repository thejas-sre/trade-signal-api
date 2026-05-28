# trade-signal-api

A Python FastAPI service that processes and caches trading signals using Redis.
This service is the common application used across all infrastructure projects
in this portfolio — providing a realistic workload for benchmarking, observability,
CI/CD validation, and Kubernetes operations.

## Status

> Work in progress — full implementation coming shortly.

## What This Project Demonstrates

- Python FastAPI service with Redis cache integration
- Prometheus metrics endpoint for observability integration
- Multi-stage Docker build for production deployment
- Kubernetes-ready with health and readiness probes

## Stack

Python · FastAPI · Redis · Docker · Kubernetes · Prometheus

## Related Projects

All infrastructure projects in this portfolio operate on this service:
- [redis-performance-toolkit](https://github.com/thejas-sre/redis-performance-toolkit)
- [observability-stack](https://github.com/thejas-sre/observability-stack)
- [release-validation-pipeline](https://github.com/thejas-sre/release-validation-pipeline)
- [terraform-drift-detector](https://github.com/thejas-sre/terraform-drift-detector)
- [kubernetes-ops-runbook](https://github.com/thejas-sre/kubernetes-ops-runbook)
