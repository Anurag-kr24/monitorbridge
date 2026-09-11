import logging

from flask import Blueprint, jsonify, request

from app.database import db
from app.models.alert import Alert
from app.models.metric import Metric
from app.services.alerts import evaluate_metric
from app.services.monitoring import create_metric


api = Blueprint("api", __name__)
logger = logging.getLogger(__name__)


ALLOWED_STATUS_TRANSITIONS = {
    "OPEN": {"ACKNOWLEDGED", "RESOLVED"},
    "ACKNOWLEDGED": {"RESOLVED"},
    "RESOLVED": set(),
}


@api.get("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "monitorbridge"
    })


@api.post("/metrics")
def ingest_metric():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    try:
        metric = create_metric(data)

        db.session.add(metric)
        db.session.flush()

        alert_data = evaluate_metric(metric)
        alert = None

        if alert_data:
            alert = (
                Alert.query
                .filter_by(
                    service=alert_data["service"],
                    metric_name=alert_data["metric_name"],
                    status="OPEN",
                )
                .first()
            )

            if alert:
                alert.value = alert_data["value"]
                alert.severity = alert_data["severity"]
                alert.severity_score = alert_data["severity_score"]
                alert.message = alert_data["message"]

                logger.info(
                    "Existing alert updated: id=%s service=%s metric=%s",
                    alert.id,
                    alert.service,
                    alert.metric_name,
                )

            else:
                alert = Alert(
                    service=alert_data["service"],
                    metric_name=alert_data["metric_name"],
                    value=alert_data["value"],
                    severity=alert_data["severity"],
                    severity_score=alert_data["severity_score"],
                    message=alert_data["message"],
                )

                db.session.add(alert)

                logger.info(
                    "New alert created: service=%s metric=%s severity=%s",
                    alert.service,
                    alert.metric_name,
                    alert.severity,
                )

        db.session.commit()

        logger.info(
            "Metric ingested: service=%s metric=%s value=%s alert=%s",
            metric.service,
            metric.metric_name,
            metric.value,
            alert is not None,
        )

        return jsonify({
            "metric": metric.to_dict(),
            "alert": alert.to_dict() if alert else None,
        }), 201

    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400

    except Exception:
        db.session.rollback()

        logger.exception(
            "Unexpected error while ingesting metric"
        )

        return jsonify({
            "error": "Internal server error"
        }), 500


@api.get("/metrics")
def get_metrics():
    metrics = (
        Metric.query
        .order_by(Metric.timestamp.desc())
        .limit(100)
        .all()
    )

    return jsonify({
        "count": len(metrics),
        "metrics": [
            metric.to_dict()
            for metric in metrics
        ],
    })


@api.get("/metrics/<int:metric_id>")
def get_metric(metric_id):
    metric = db.session.get(Metric, metric_id)

    if metric is None:
        return jsonify({
            "error": "Metric not found"
        }), 404

    return jsonify(metric.to_dict())


@api.post("/evaluate")
def evaluate():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Request body must contain valid JSON"
        }), 400

    try:
        metric = create_metric(data)
        alert = evaluate_metric(metric)

        return jsonify({
            "alert": alert,
            "requires_attention": alert is not None,
        })

    except ValueError as exc:
        return jsonify({
            "error": str(exc)
        }), 400


@api.get("/alerts")
def get_alerts():
    alerts = (
        Alert.query
        .order_by(Alert.created_at.desc())
        .limit(100)
        .all()
    )

    return jsonify({
        "count": len(alerts),
        "alerts": [
            alert.to_dict()
            for alert in alerts
        ],
    })


@api.get("/alerts/<int:alert_id>")
def get_alert(alert_id):
    alert = db.session.get(Alert, alert_id)

    if alert is None:
        return jsonify({
            "error": "Alert not found"
        }), 404

    return jsonify(alert.to_dict())


@api.patch("/alerts/<int:alert_id>")
def update_alert_status(alert_id):
    alert = db.session.get(Alert, alert_id)

    if alert is None:
        return jsonify({
            "error": "Alert not found"
        }), 404

    data = request.get_json(silent=True)

    if not data or "status" not in data:
        return jsonify({
            "error": "Request must contain a status"
        }), 400

    new_status = str(data["status"]).upper().strip()

    if new_status not in {"OPEN", "ACKNOWLEDGED", "RESOLVED"}:
        return jsonify({
            "error": "Invalid status. Use OPEN, ACKNOWLEDGED, or RESOLVED"
        }), 400

    current_status = alert.status

    if new_status == current_status:
        return jsonify({
            "error": f"Alert is already {current_status}"
        }), 409

    allowed_transitions = ALLOWED_STATUS_TRANSITIONS[current_status]

    if new_status not in allowed_transitions:
        return jsonify({
            "error": (
                f"Invalid status transition: "
                f"{current_status} -> {new_status}"
            )
        }), 409

    alert.status = new_status

    try:
        db.session.commit()

        logger.info(
            "Alert status changed: id=%s %s -> %s",
            alert.id,
            current_status,
            new_status,
        )

        return jsonify(alert.to_dict())

    except Exception:
        db.session.rollback()

        logger.exception(
            "Failed to update alert status: id=%s",
            alert_id,
        )

        return jsonify({
            "error": "Internal server error"
        }), 500
