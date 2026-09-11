def test_health(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "healthy",
        "service": "monitorbridge",
    }


def test_ingest_valid_metric(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": 42,
        },
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["metric"]["service"] == "payment-api"
    assert data["metric"]["metric_name"] == "cpu_usage"
    assert data["metric"]["value"] == 42.0
    assert data["alert"] is None


def test_reject_missing_fields(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
        },
    )

    assert response.status_code == 400
    assert "Missing required fields" in response.get_json()["error"]


def test_reject_non_numeric_value(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": "hello",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Metric value must be numeric"


def test_cpu_warning_alert(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": 82,
        },
    )

    assert response.status_code == 201

    alert = response.get_json()["alert"]

    assert alert["severity"] == "warning"
    assert alert["status"] == "OPEN"
    assert alert["value"] == 82.0


def test_cpu_critical_alert(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": 95,
        },
    )

    assert response.status_code == 201

    alert = response.get_json()["alert"]

    assert alert["severity"] == "critical"
    assert alert["status"] == "OPEN"
    assert alert["value"] == 95.0


def test_memory_thresholds(client):
    warning_response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "memory_usage",
            "value": 85,
        },
    )

    critical_response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "memory_usage",
            "value": 95,
        },
    )

    assert warning_response.get_json()["alert"]["severity"] == "warning"
    assert critical_response.get_json()["alert"]["severity"] == "critical"


def test_latency_thresholds(client):
    warning_response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "request_latency",
            "value": 700,
        },
    )

    critical_response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "request_latency",
            "value": 1200,
        },
    )

    assert warning_response.get_json()["alert"]["severity"] == "warning"
    assert critical_response.get_json()["alert"]["severity"] == "critical"


def test_error_rate_thresholds(client):
    warning_response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "error_rate",
            "value": 7,
        },
    )

    critical_response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "error_rate",
            "value": 12,
        },
    )

    assert warning_response.get_json()["alert"]["severity"] == "warning"
    assert critical_response.get_json()["alert"]["severity"] == "critical"


def test_deduplicate_open_alert(client):
    payload = {
        "service": "payment-api",
        "metric_name": "cpu_usage",
        "value": 90,
    }

    first_response = client.post(
        "/api/metrics",
        json=payload,
    )

    second_response = client.post(
        "/api/metrics",
        json={
            **payload,
            "value": 94,
        },
    )

    first_alert = first_response.get_json()["alert"]
    second_alert = second_response.get_json()["alert"]

    assert first_alert["id"] == second_alert["id"]
    assert second_alert["value"] == 94.0

    alerts_response = client.get("/api/alerts")

    assert alerts_response.get_json()["count"] == 1


def test_alert_lifecycle(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": 95,
        },
    )

    alert_id = response.get_json()["alert"]["id"]

    acknowledge_response = client.patch(
        f"/api/alerts/{alert_id}",
        json={"status": "ACKNOWLEDGED"},
    )

    assert acknowledge_response.status_code == 200
    assert acknowledge_response.get_json()["status"] == "ACKNOWLEDGED"

    resolve_response = client.patch(
        f"/api/alerts/{alert_id}",
        json={"status": "RESOLVED"},
    )

    assert resolve_response.status_code == 200
    assert resolve_response.get_json()["status"] == "RESOLVED"


def test_resolved_alert_creates_new_incident(client):
    payload = {
        "service": "payment-api",
        "metric_name": "cpu_usage",
        "value": 95,
    }

    first_response = client.post(
        "/api/metrics",
        json=payload,
    )

    first_alert_id = first_response.get_json()["alert"]["id"]

    client.patch(
        f"/api/alerts/{first_alert_id}",
        json={"status": "RESOLVED"},
    )

    second_response = client.post(
        "/api/metrics",
        json={
            **payload,
            "value": 98,
        },
    )

    second_alert_id = second_response.get_json()["alert"]["id"]

    assert second_alert_id != first_alert_id
    assert second_response.get_json()["alert"]["status"] == "OPEN"


def test_reject_invalid_alert_transition(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": 95,
        },
    )

    alert_id = response.get_json()["alert"]["id"]

    client.patch(
        f"/api/alerts/{alert_id}",
        json={"status": "RESOLVED"},
    )

    invalid_response = client.patch(
        f"/api/alerts/{alert_id}",
        json={"status": "ACKNOWLEDGED"},
    )

    assert invalid_response.status_code == 409
    assert "Invalid status transition" in invalid_response.get_json()["error"]


def test_invalid_alert_status(client):
    response = client.post(
        "/api/metrics",
        json={
            "service": "payment-api",
            "metric_name": "cpu_usage",
            "value": 95,
        },
    )

    alert_id = response.get_json()["alert"]["id"]

    invalid_response = client.patch(
        f"/api/alerts/{alert_id}",
        json={"status": "BOGUS"},
    )

    assert invalid_response.status_code == 400
    assert "Invalid status" in invalid_response.get_json()["error"]


def test_missing_metric_returns_404(client):
    response = client.get("/api/metrics/9999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Metric not found"


def test_missing_alert_returns_404(client):
    response = client.get("/api/alerts/9999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Alert not found"
