import random


SERVICES = [
    "payment-api",
    "order-api",
    "user-api",
]

METRICS = [
    "cpu_usage",
    "memory_usage",
    "request_latency",
    "error_rate",
]


def generate_metric():
    service = random.choice(SERVICES)
    metric_name = random.choice(METRICS)

    if metric_name == "cpu_usage":
        value = random.uniform(20, 98)

    elif metric_name == "memory_usage":
        value = random.uniform(30, 97)

    elif metric_name == "request_latency":
        value = random.uniform(100, 1300)

    else:
        value = random.uniform(0, 15)

    return {
        "service": service,
        "metric_name": metric_name,
        "value": round(value, 2),
    }
