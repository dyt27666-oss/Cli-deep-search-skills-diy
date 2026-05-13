#!/usr/bin/env python3
"""Token-safe per-job metric summary for /deep-search.

Usage:
    python scripts/_deep_search_metric_query.py <jobInternalId>

Reads outputs/taiji-output/training/all-metrics-long.csv in a single pass and
prints at most 20 summary rows: metric, chart, n, last_step, last_value, max_value.
"""

from __future__ import annotations

import csv
import math
import sys
from pathlib import Path
from typing import Dict, Tuple

MAX_ROWS = 20
METRICS_PATH = Path("outputs/taiji-output/training/all-metrics-long.csv")


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


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] in {"-h", "--help"}:
        print("usage: python scripts/_deep_search_metric_query.py <jobInternalId>", file=sys.stderr)
        return 2

    job_internal_id = str(argv[1])
    if not METRICS_PATH.exists():
        print(f"metric\tchart\tn\tlast_step\tlast_value\tmax_value")
        print(f"# metrics file not found: {METRICS_PATH}", file=sys.stderr)
        return 1

    summaries: Dict[Tuple[str, str], dict] = {}

    with METRICS_PATH.open("r", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if str(row.get("jobInternalId", "")) != job_internal_id:
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
    raise SystemExit(main(sys.argv))
