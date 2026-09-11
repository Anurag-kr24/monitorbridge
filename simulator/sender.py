import os

import requests


API_URL = os.getenv(
    "MONITORBRIDGE_URL",
    "http://127.0.0.1:5000/api/metrics",
)


def send_metric(metric):
    response = requests.post(
        API_URL,
        json=metric,
        timeout=5,
    )

    response.raise_for_status()

    return response.json()
