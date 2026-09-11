import argparse
import time

from simulator.generator import generate_metric
from simulator.scenarios import cpu_spike
from simulator.sender import send_metric


SCENARIOS = {
    "cpu-spike": cpu_spike,
}


def send_and_print(number, total, metric):
    try:
        result = send_metric(metric)
        alert = result.get("alert")

        print(
            f"[{number}/{total}] "
            f"{metric['service']} | "
            f"{metric['metric_name']} | "
            f"{metric['value']} "
            f"→ "
            f"{alert['severity'] if alert else 'OK'}"
        )

    except Exception as exc:
        print(
            f"[{number}/{total}] "
            f"ERROR: {exc}"
        )


def run_random(iterations, interval):
    for number in range(1, iterations + 1):
        metric = generate_metric()

        send_and_print(number, iterations, metric)

        if number < iterations:
            time.sleep(interval)


def run_scenario(name, interval):
    metrics = SCENARIOS[name]()
    total = len(metrics)

    for number, metric in enumerate(metrics, start=1):
        send_and_print(number, total, metric)

        if number < total:
            time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate simulated monitoring telemetry."
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of random metrics to generate.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Seconds between metrics.",
    )

    parser.add_argument(
        "--scenario",
        choices=SCENARIOS.keys(),
        help="Run a deterministic incident scenario.",
    )

    args = parser.parse_args()

    if args.scenario:
        run_scenario(args.scenario, args.interval)
    else:
        run_random(args.iterations, args.interval)
