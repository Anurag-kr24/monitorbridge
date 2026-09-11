import argparse
import time

from simulator.generator import generate_metric
from simulator.sender import send_metric


def run(iterations, interval):
    for number in range(1, iterations + 1):
        metric = generate_metric()

        try:
            result = send_metric(metric)
            alert = result.get("alert")

            print(
                f"[{number}/{iterations}] "
                f"{metric['service']} | "
                f"{metric['metric_name']} | "
                f"{metric['value']} "
                f"→ "
                f"{alert['severity'] if alert else 'OK'}"
            )

        except Exception as exc:
            print(
                f"[{number}/{iterations}] "
                f"ERROR: {exc}"
            )

        if number < iterations:
            time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate simulated monitoring telemetry."
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of metrics to generate.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between metrics.",
    )

    args = parser.parse_args()

    run(
        iterations=args.iterations,
        interval=args.interval,
    )
