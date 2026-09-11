from app.models.metric import Metric


def create_metric(data):
    required_fields = ["service", "metric_name", "value"]

    missing = [
        field for field in required_fields
        if field not in data
    ]

    if missing:
        raise ValueError(
            f"Missing required fields: {', '.join(missing)}"
        )

    try:
        value = float(data["value"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Metric value must be numeric") from exc

    if not data["service"].strip():
        raise ValueError("Service name cannot be empty")

    if not data["metric_name"].strip():
        raise ValueError("Metric name cannot be empty")

    return Metric(
        service=data["service"].strip(),
        metric_name=data["metric_name"].strip(),
        value=value,
    )
