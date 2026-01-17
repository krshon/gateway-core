# API Gateway

A simplified API Gateway built using FastAPI to understand how backend systems handle
authentication, rate limiting, and request observability at a central entry point.

The project focuses on implementing these cross-cutting concerns using middleware,
similar to real-world production backends.

## Current Features
- Global request interception using FastAPI middleware
- Request logging (HTTP method and endpoint)
- Request latency measurement
- JWT-based authentication enforced at the gateway level
- Protected routes using Authorization headers
- Per-user rate limiting to prevent abuse

## Planned Features
- Structured logging and metrics
- Cloud deployment

## Tech Stack
FastAPI · Python · Uvicorn · JWT
