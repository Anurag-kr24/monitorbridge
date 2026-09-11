# MonitorBridge

A lightweight monitoring and incident-management service built with Python, Flask, SQLAlchemy, and SQLite.

MonitorBridge ingests service telemetry through a REST API, validates and persists metrics, evaluates threshold-based conditions, and manages the resulting alerts through an incident lifecycle.

## Architecture

```text
Simulated Telemetry
        |
        v
   REST API (Flask)
        |
        +--> Validation
        |
        +--> SQLite Persistence
        |
        +--> Threshold Evaluation
                    |
                    v
              Alert Management
                    |
          +---------+---------+
          |                   |
          v                   v
      REST API             SQLite
Features
REST API for metric ingestion and retrieval
Metric validation and structured API errors
SQLite persistence using SQLAlchemy
Threshold-based alert evaluation
Warning and critical severity levels
Alert deduplication for active incidents
Alert lifecycle:
OPEN
ACKNOWLEDGED
RESOLVED
Request ID tracing through X-Request-ID
Structured logging
Deterministic incident simulation
Automated API tests with pytest
Supported Metrics
Metric	Warning	Critical	Unit
cpu_usage	75	90	percent
memory_usage	80	92	percent
error_rate	5	10	percent
request_latency	500	1000	milliseconds
Project Structure
monitorbridge/
├── app/
│   ├── models/
│   │   ├── alert.py
│   │   └── metric.py
│   ├── services/
│   │   ├── alerts.py
│   │   ├── monitoring.py
│   │   └── thresholds.py
│   ├── utils/
│   │   ├── errors.py
│   │   ├── logging_config.py
│   │   └── request_id.py
│   ├── config.py
│   ├── database.py
│   └── routes.py
├── simulator/
│   ├── generator.py
│   ├── scenarios.py
│   ├── sender.py
│   └── run.py
├── tests/
│   ├── conftest.py
│   └── test_api.py
├── .env.example
├── requirements.txt
├── run.py
└── README.md
Setup

Create and activate a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Create a local environment file:

cp .env.example .env
Run the API

Start the Flask application:

python run.py

The API will be available at:

http://127.0.0.1:5000

Health check:

curl http://127.0.0.1:5000/api/health

Example response:

{
  "service": "monitorbridge",
  "status": "healthy"
}
API
Ingest a metric

POST /api/metrics

Example:

curl -X POST http://127.0.0.1:5000/api/metrics \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payment-api",
    "metric_name": "cpu_usage",
    "value": 94
  }'

The response contains the persisted metric and any generated alert.

List metrics

GET /api/metrics

curl http://127.0.0.1:5000/api/metrics
Get a metric

GET /api/metrics/<id>

curl http://127.0.0.1:5000/api/metrics/1
Evaluate a metric without persisting it

POST /api/evaluate

curl -X POST http://127.0.0.1:5000/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "service": "payment-api",
    "metric_name": "cpu_usage",
    "value": 94
  }'
List alerts

GET /api/alerts

curl http://127.0.0.1:5000/api/alerts
Get an alert

GET /api/alerts/<id>

curl http://127.0.0.1:5000/api/alerts/1
Update alert status

PATCH /api/alerts/<id>

Valid lifecycle:

OPEN -> ACKNOWLEDGED -> RESOLVED

Example:

curl -X PATCH http://127.0.0.1:5000/api/alerts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "ACKNOWLEDGED"}'

Then:

curl -X PATCH http://127.0.0.1:5000/api/alerts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "RESOLVED"}'

Invalid lifecycle transitions are rejected with HTTP 409.

Structured Errors

API errors use a consistent structure:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Metric value must be numeric",
    "request_id": "..."
  }
}

This provides both a machine-readable error code and a request ID that can be used to trace the request.

Request IDs

Every API response contains an X-Request-ID header.

If the client does not provide one, MonitorBridge generates a UUID automatically.

curl -i http://127.0.0.1:5000/api/health

Clients can also provide their own request ID:

curl -i \
  -H "X-Request-ID: test-request-123" \
  http://127.0.0.1:5000/api/health
Telemetry Simulator

The simulator can generate random monitoring telemetry:

python -m simulator.run --iterations 10 --interval 0.5

It sends generated metrics to the running MonitorBridge API over HTTP.

Controlled Incident Scenario

A deterministic CPU spike scenario is available for repeatable testing:

python -m simulator.run --scenario cpu-spike --interval 0.5

The scenario progresses through normal, warning, critical, and recovery states:

42  -> OK
58  -> OK
82  -> WARNING
94  -> CRITICAL
96  -> CRITICAL
72  -> OK
48  -> OK
41  -> OK

Repeated critical readings for the same service and metric are deduplicated into the existing open incident.

After an incident is resolved, a later recurrence creates a new incident.

Testing

Run the complete test suite:

pytest -q

Current test coverage includes:

Health endpoint
Metric ingestion
Request validation
Numeric validation
Threshold evaluation
Multiple metric types
Alert deduplication
Alert lifecycle
Invalid lifecycle transitions
Invalid alert statuses
Missing resources
Structured validation errors
Request ID behavior
Configuration

Configuration is controlled through environment variables.

Example:

APP_ENV=development
DATABASE_URL=sqlite:///monitorbridge.db
ALERT_THRESHOLD=0.75
Engineering Goals

MonitorBridge is intentionally designed as a small but production-oriented backend rather than a simple CRUD application.

The project emphasizes:

Clear separation of concerns
REST API design
Validation
Persistence
Incident state management
Observability
Automated testing
Repeatable integration testing
Maintainable project structure
License

This project is for educational and portfolio purposes.

## Docker

MonitorBridge can be run as a containerized production-style service using Docker and Gunicorn.

Build the image:

```bash
docker build -t monitorbridge .
    docker build -t monitorbridge .
    ```

    Run the container:

    ```bash
    docker run --rm -p 5000:5000 monitorbridge
    ```

    Or start it using Docker Compose:

    ```bash
    docker compose up --build
    ```

    Health check:

    ```bash
    curl http://127.0.0.1:5000/api/health
    ```

    The container exposes port `5000` and uses a Docker health check against the application's health endpoint.

    Gunicorn is used as the production WSGI server instead of Flask's development server.

    Stop the Compose deployment:

    ```bash
    docker compose down
    ```
    EOF

## API Documentation

MonitorBridge exposes interactive API documentation using Swagger.

After starting the application, open:

```text
http://127.0.0.1:5000/api/docs/

The generated API specification is available at:

```text
http://127.0.0.1:5000/api/openapi.json

The generated API specification is available at:

```text
http://127.0.0.1:5000/api/openapi.json
The documentation provides an interactive interface for exploring and testing the REST API endpoints.

Docker

MonitorBridge can be run as a containerized production-style service using Docker and Gunicorn.

Build the image:

docker build -t monitorbridge .

Run the container:

docker run --rm -p 5000:5000 monitorbridge

Or start it using Docker Compose:

docker compose up --build

Health check:

curl http://127.0.0.1:5000/api/health

The container exposes port 5000 and uses a health check against the application's health endpoint.

Gunicorn is used as the production WSGI server instead of Flask's development server.

Stop the Compose deployment:

docker compose down
Engineering Goals

MonitorBridge is intentionally designed as a small but production-oriented backend rather than a simple CRUD application.

The project emphasizes:

Clear separation of concerns
REST API design
Validation
Persistence
Incident state management
Observability
Automated testing
Repeatable integration testing
Maintainable project structure
License

This project is for educational and portfolio purposes.
