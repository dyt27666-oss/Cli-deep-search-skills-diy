#!/usr/bin/env python3
"""Token-safe per-run metric summary for /deep-search.

Usage:
    python scripts/_deep_search_metric_query.py <job-id> --metrics-path outputs/<platform>/all-metrics-long.csv

Reads the configured metrics CSV in a single pass and prints at most 20 summary
rows: metric, chart, n, last_step, last_value, max_value.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
from pathlib import Path
from typing import Dict, Tuple

MAX_ROWS = 20
ILLUSTRATIVE_DEFAULT_PATH = "outputs/<platform>/all-metrics-long.csv"


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def _to_int(value: str) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return -1


def _fmt(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.10g}"


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize metrics for one job/run without loading a large CSV into context.",
        epilog=(
            "Set --metrics-path or DEEP_SEARCH_METRICS_PATH. "
            f"Example path: {ILLUSTRATIVE_DEFAULT_PATH}"
        ),
    )
    parser.add_argument("job_id", help="Job/run identifier to filter, matched against job_id or platform-specific job identifier columns.")
    parser.add_argument(
        "--metrics-path",
        default=os.environ.get("DEEP_SEARCH_METRICS_PATH"),
        help="Path to the long-form metrics CSV. Falls back to DEEP_SEARCH_METRICS_PATH.",
    )
    return parser.parse_args(argv[1:])


def main(argv: list[str]) -> int:
    args = _parse_args(argv)
    job_id = str(args.job_id)

    if not args.metrics_path:
        print("metric\tchart\tn\tlast_step\tlast_value\tmax_value")
        print(
            "# metrics path is not configured. Pass --metrics-path PATH or set "
            "DEEP_SEARCH_METRICS_PATH. Example: "
            f"{ILLUSTRATIVE_DEFAULT_PATH}",
            file=os.sys.stderr,
        )
        return 1

    metrics_path = Path(args.metrics_path)
    if not metrics_path.exists():
        print("metric\tchart\tn\tlast_step\tlast_value\tmax_value")
        print(
            f"# metrics file not found: {metrics_path}. Pass --metrics-path PATH or set "
            "DEEP_SEARCH_METRICS_PATH to your exported metrics CSV.",
            file=os.sys.stderr,
        )
        return 1

    summaries: Dict[Tuple[str, str], dict] = {}

    with metrics_path.open("r", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            row_job_id = row.get("job_id") or row.get("run_id") or row.get("id", "")
            if str(row_job_id) != job_id:
                continue

            metric = row.get("metric") or "<unknown>"
            chart = row.get("chart") or row.get("series") or "<unknown>"
            key = (metric, chart)
            step = _to_int(row.get("step", ""))
            value = _to_float(row.get("value", ""))

            item = summaries.setdefault(
                key,
                {
                    "n": 0,
                    "last_step": -1,
                    "last_value": math.nan,
                    "max_value": math.nan,
                },
            )
            item["n"] += 1
            if step >= item["last_step"]:
                item["last_step"] = step
                item["last_value"] = value
            if not math.isnan(value) and (math.isnan(item["max_value"]) or value > item["max_value"]):
                item["max_value"] = value

    rows = [
        (metric, chart, data["n"], data["last_step"], data["last_value"], data["max_value"])
        for (metric, chart), data in summaries.items()
    ]
    rows.sort(key=lambda r: (-r[2], r[0], r[1]))

    print("metric\tchart\tn\tlast_step\tlast_value\tmax_value")
    for metric, chart, n, last_step, last_value, max_value in rows[:MAX_ROWS]:
        print(f"{metric}\t{chart}\t{n}\t{last_step}\t{_fmt(last_value)}\t{_fmt(max_value)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(os.sys.argv))
