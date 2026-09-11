from app.services.thresholds import get_rule


def evaluate_metric(metric):
    rule = get_rule(metric.metric_name)

    if rule is None:
        return None

    value = metric.value
    warning_threshold = rule["warning"]
    critical_threshold = rule["critical"]

    if value >= critical_threshold:
        severity = "critical"
        severity_score = 1.0
    elif value >= warning_threshold:
        severity = "warning"
        severity_score = round(
            value / critical_threshold,
            3,
        )
    else:
        return None

    return {
        "service": metric.service,
        "metric_name": metric.metric_name,
        "value": metric.value,
        "severity": severity,
        "severity_score": severity_score,
        "message": (
            f"{metric.metric_name} for {metric.service} "
            f"requires attention."
        ),
    }
