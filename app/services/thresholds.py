METRIC_RULES = {
    "cpu_usage": {
        "unit": "percent",
        "warning": 75.0,
        "critical": 90.0,
    },
    "memory_usage": {
        "unit": "percent",
        "warning": 80.0,
        "critical": 92.0,
    },
    "error_rate": {
        "unit": "percent",
        "warning": 5.0,
        "critical": 10.0,
    },
    "request_latency": {
        "unit": "milliseconds",
        "warning": 500.0,
        "critical": 1000.0,
    },
}


def get_rule(metric_name):
    return METRIC_RULES.get(metric_name)
