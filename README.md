# MonitorBridge

> A production-oriented monitoring and incident management REST API built with Python and Flask.

MonitorBridge is a backend service that simulates application telemetry, validates incoming metrics, evaluates threshold-based conditions, persists monitoring data, and manages the lifecycle of generated incidents.

The project was designed as a compact demonstration of backend engineering practices including REST API design, persistence, validation, observability, automated testing, and containerized deployment.

---

## Architecture

```text
                    Simulated Telemetry
                           |
                           v
                    REST API (Flask)
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
        Validation     Persistence   Threshold
                         (SQLite)    Evaluation
                                          |
                                          v
                                   Alert Management
                                          |
                              +-----------+-----------+
                              |                       |
                              v                       v
                         REST API                  SQLite
```

---

## Key Features

- REST API for metric ingestion and retrieval
- Metric validation with structured API errors
- SQLite persistence using SQLAlchemy
- Threshold-based alert evaluation
- Warning and critical severity levels
- Alert deduplication for active incidents
- Explicit alert lifecycle management
- Request ID tracing through `X-Request-ID`
- Request timing and structured logging
- Deterministic incident simulation
- Automated API tests with pytest
- Interactive Swagger API documentation
- Docker and Docker Compose support
- Gunicorn production WSGI server
- Environment-based configuration
- Clear separation of API, service, model, and utility layers

---

## Supported Metrics

| Metric | Warning | Critical | Unit |
|---|---:|---:|---|
| `cpu_usage` | 75 | 90 | percent |
| `memory_usage` | 80 | 92 | percent |
| `error_rate` | 5 | 10 | percent |
| `request_latency` | 500 | 1000 | milliseconds |

Threshold evaluation produces either:

- `OK` — metric is below the warning threshold
- `WARNING` — metric has crossed the warning threshold
- `CRITICAL` — metric has crossed the critical threshold

---

## Alert Lifecycle

Alerts follow an explicit state machine:

```text
OPEN
  |
  v
ACKNOWLEDGED
  |
  v
RESOLVED
```

Invalid state transitions are rejected by the API with HTTP `409 Conflict`.

Active alerts are deduplicated by service and metric. Repeated critical readings for the same active incident do not create unnecessary duplicate incidents.

Once an incident is resolved, a later recurrence creates a new alert.

---

## Project Structure

```text
monitorbridge/
├── app/
│   ├── models/
│   │   ├── alert.py
│   │   └── metric.py
│   │
│   ├── services/
│   │   ├── alerts.py
│   │   ├── monitoring.py
│   │   └── thresholds.py
│   │
│   ├── utils/
│   │   ├── errors.py
│   │   ├── logging_config.py
│   │   └── request_id.py
│   │
│   ├── config.py
│   ├── database.py
│   └── routes.py
│
├── simulator/
│   ├── generator.py
│   ├── scenarios.py
│   ├── sender.py
│   └── run.py
│
├── tests/
│   ├── conftest.py
│   └── test_api.py
│
├── .env.example
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.py
└── README.md
```

---

# Getting Started

## Requirements

- Python 3.10+
- pip
- Git

Docker is optional.

---

## Local Installation

Clone the repository:

```bash
git clone https://github.com/Anurag-kr24/monitorbridge.git
cd monitorbridge
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

---

# Running the API

Start the Flask application:

```bash
python run.py
```

The API will be available at:

```text
http://127.0.0.1:5000
```

---

## Health Check

```bash
curl http://127.0.0.1:5000/api/health
```

Example response:

```json
{
  "service": "monitorbridge",
  "status": "healthy"
}
```

---

# API Documentation

MonitorBridge exposes interactive Swagger documentation.

After starting the application, open:

```text
http://127.0.0.1:5000/api/docs/
```

The generated API specification is available at:

```text
http://127.0.0.1:5000/api/openapi.json
```

The Swagger interface provides an interactive way to explore and test the available REST endpoints.

---

# REST API

## Ingest a Metric

### `POST /api/metrics`

Example:

```bash
curl -X POST http://127.0.0.1:5000/api/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payment-api",
    "metric_name": "cpu_usage",
    "value": 94
  }'
```

The API validates and persists the metric and evaluates it against the configured threshold rules.

The response contains the persisted metric and any generated alert.

---

## List Metrics

### `GET /api/metrics`

```bash
curl http://127.0.0.1:5000/api/metrics
```

---

## Get a Metric

### `GET /api/metrics/<id>`

```bash
curl http://127.0.0.1:5000/api/metrics/1
```

---

## Evaluate a Metric

### `POST /api/evaluate`

This endpoint evaluates a metric without persisting it.

```bash
curl -X POST http://127.0.0.1:5000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payment-api",
    "metric_name": "cpu_usage",
    "value": 94
  }'
```

---

## List Alerts

### `GET /api/alerts`

```bash
curl http://127.0.0.1:5000/api/alerts
```

---

## Get an Alert

### `GET /api/alerts/<id>`

```bash
curl http://127.0.0.1:5000/api/alerts/1
```

---

## Update Alert Status

### `PATCH /api/alerts/<id>`

Valid lifecycle:

```text
OPEN -> ACKNOWLEDGED -> RESOLVED
```

Example:

```bash
curl -X PATCH http://127.0.0.1:5000/api/alerts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "ACKNOWLEDGED"}'
```

Then:

```bash
curl -X PATCH http://127.0.0.1:5000/api/alerts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED"}'
```

Invalid lifecycle transitions return HTTP `409 Conflict`.

---

# Structured Error Handling

API errors use a consistent machine-readable structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Metric value must be numeric",
    "request_id": "..."
  }
}
```

This provides:

- A stable error code for clients
- A human-readable error message
- A request ID for tracing and debugging

---

# Request ID Tracing

Every API response contains an `X-Request-ID` header.

If the client does not provide one, MonitorBridge automatically generates a UUID.

Example:

```bash
curl -i http://127.0.0.1:5000/api/health
```

Clients can also provide their own request ID:

```bash
curl -i \
  -H "X-Request-ID: test-request-123" \
  http://127.0.0.1:5000/api/health
```

The request ID is included in application logs, allowing individual API requests to be traced through the service.

---

# Observability

MonitorBridge records structured request logs containing:

- Timestamp
- Log level
- Logger name
- Request ID
- HTTP method
- Request path
- HTTP status code
- Request duration

Example:

```text
2026-09-11 15:03:44 | INFO | monitorbridge.request |
request_id=test-observability-123 |
GET /api/health |
status=200 |
duration_ms=0.12
```

This provides basic request-level observability without requiring an external monitoring platform.

---

# Telemetry Simulator

MonitorBridge includes a telemetry simulator capable of generating monitoring data and sending it to the running API over HTTP.

## Random Telemetry

Generate ten metrics with a 0.5 second interval:

```bash
python -m simulator.run --iterations 10 --interval 0.5
```

---

## Deterministic Incident Scenario

A controlled CPU spike scenario is available for repeatable testing:

```bash
python -m simulator.run --scenario cpu-spike --interval 0.5
```

The scenario progresses through normal, warning, critical, and recovery states:

```text
42  -> OK
58  -> OK
82  -> WARNING
94  -> CRITICAL
96  -> CRITICAL
72  -> OK
48  -> OK
41  -> OK
```

This makes the alerting behavior deterministic and easy to reproduce during development or demonstration.

---

# Testing

Run the complete test suite:

```bash
pytest -q
```

Current test suite:

```text
18 passed
```

The tests cover:

- Health endpoint
- Metric ingestion
- Request validation
- Numeric validation
- Threshold evaluation
- Multiple metric types
- Alert creation
- Alert deduplication
- Alert lifecycle
- Invalid lifecycle transitions
- Invalid alert statuses
- Missing resources
- Structured validation errors
- Request ID behavior
- API behavior and persistence

---

# Docker

MonitorBridge can be run as a containerized service using Docker and Gunicorn.

## Build the Image

```bash
docker build -t monitorbridge .
```

## Run the Container

```bash
docker run --rm -p 5000:5000 monitorbridge
```

## Docker Compose

Start the complete service:

```bash
docker compose up --build
```

Health check:

```bash
curl http://127.0.0.1:5000/api/health
```

The container exposes port `5000` and uses a Docker health check against the application's health endpoint.

Gunicorn is used as the production WSGI server instead of the Flask development server.

Stop the Compose deployment:

```bash
docker compose down
```

---

# Configuration

Configuration is controlled through environment variables.

Example `.env`:

```text
APP_ENV=development
DATABASE_URL=sqlite:///monitorbridge.db
ALERT_THRESHOLD=0.75
```

Available configuration includes:

| Variable | Purpose | Default |
|---|---|---|
| `APP_ENV` | Application environment | `development` |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///monitorbridge.db` |
| `ALERT_THRESHOLD` | Alert configuration value | `0.75` |

---

# Engineering Principles

MonitorBridge is intentionally designed as a small but production-oriented backend rather than a simple CRUD application.

The project emphasizes:

### Separation of Concerns

API routes, business logic, persistence models, configuration, and utilities are kept in separate modules.

### REST API Design

The service exposes resource-oriented HTTP endpoints for metrics and alerts.

### Validation

Incoming telemetry is validated before it reaches persistence or alert evaluation.

### Incident State Management

Alerts follow an explicit lifecycle with validation of state transitions.

### Observability

Request IDs, structured logging, and request timing provide basic request-level tracing.

### Automated Testing

The API is covered by an automated pytest test suite.

### Repeatable Integration Testing

Deterministic simulator scenarios make incident behavior reproducible.

### Containerization

Docker and Gunicorn provide a production-style deployment path.

### Maintainability

The project favors small, focused modules and explicit business logic over unnecessary framework complexity.

---

# Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend development |
| Flask | REST API |
| SQLAlchemy | ORM and persistence |
| SQLite | Relational database |
| pytest | Automated testing |
| Flasgger | Swagger/OpenAPI documentation |
| Gunicorn | Production WSGI server |
| Docker | Containerization |
| Git | Version control |

---

# Project Status

MonitorBridge is a completed portfolio project demonstrating a production-oriented monitoring and incident management backend.

The project intentionally focuses on a practical engineering workflow:

```text
Telemetry
   ↓
API
   ↓
Validation
   ↓
Persistence
   ↓
Evaluation
   ↓
Incident Management
   ↓
Observability
   ↓
Testing
   ↓
Containerized Deployment
```

---

# License

This project is for educational and portfolio purposes.
