#!/usr/bin/env python3
"""Fetch entity history from Home Assistant and output aggregated stats.

Two modes (auto-detected):
  - numeric: aggregates sensor values (avg/min/max/sum per period)
  - state:   calculates minutes spent in each state

Usage:
  python3 fetch-stats.py <entity_id> [options]

Options:
  --days N        Lookback days (default: 7)
  --period P      Aggregation: hourly, daily (default: daily)
  --stat S        Numeric stat: avg, min, max, sum (default: avg)
  --unit U        State time unit: min, hours, days (default: min)

Examples:
  python3 fetch-stats.py sensor.temperature --days 7 --stat avg
  python3 fetch-stats.py vacuum.robot --days 7
  python3 fetch-stats.py switch.light --days 3 --period hourly

Output:
  numeric: [{"t": "Mar 17", "v": 12.5}, ...]
  state:   [{"t": "cleaning", "v": 45.2}, ...]  (default: minutes)

Requires env vars: HA_URL, HA_TOKEN
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from ha_client import fetch_history, get_ha_credentials


def period_key(dt, period):
    if period == "hourly":
        return dt.strftime("%a %H:00")
    return dt.strftime("%b %d")


def aggregate_numeric(entries, period, stat):
    local_tz = datetime.now().astimezone().tzinfo
    buckets = defaultdict(list)
    bucket_order = []

    for e in entries:
        state = e.get("state", "")
        ts = e.get("last_changed", "")
        if state in ("unknown", "unavailable", "") or not ts:
            continue
        try:
            val = float(state)
        except ValueError:
            continue
        dt = datetime.fromisoformat(ts).astimezone(local_tz)
        key = period_key(dt, period)
        if key not in buckets:
            bucket_order.append(key)
        buckets[key].append(val)

    stat_fn = {
        "avg": lambda vs: sum(vs) / len(vs),
        "min": min,
        "max": max,
        "sum": sum,
    }[stat]

    return [{"t": key, "v": round(stat_fn(buckets[key]), 1)} for key in bucket_order]


def aggregate_states(entries, end):
    local_tz = datetime.now().astimezone().tzinfo
    totals = defaultdict(float)

    for i, e in enumerate(entries):
        state = e.get("state", "")
        ts = e.get("last_changed", "")
        if not ts or not state or state in ("unknown", "unavailable"):
            continue

        start_dt = datetime.fromisoformat(ts).astimezone(local_tz)
        if i + 1 < len(entries):
            next_ts = entries[i + 1].get("last_changed", "")
            end_dt = datetime.fromisoformat(next_ts).astimezone(local_tz)
        else:
            end_dt = end.astimezone(local_tz)

        minutes = (end_dt - start_dt).total_seconds() / 60
        if minutes > 0:
            totals[state] += minutes

    return [{"t": state, "v": round(mins, 1)} for state, mins in sorted(totals.items(), key=lambda x: -x[1])]


def is_numeric(entries):
    for e in entries:
        state = e.get("state", "")
        if state in ("unknown", "unavailable", ""):
            continue
        try:
            float(state)
            return True
        except ValueError:
            return False
    return False


def main():
    parser = argparse.ArgumentParser(description="Fetch and aggregate HA entity stats")
    parser.add_argument("entity_id")
    parser.add_argument("--days", type=int, default=7)
    parser.add_argument("--period", default="daily", choices=["hourly", "daily"])
    parser.add_argument("--stat", default="avg", choices=["avg", "min", "max", "sum"])
    parser.add_argument("--unit", default="min", choices=["min", "hours", "days"])
    args = parser.parse_args()

    base_url, token = get_ha_credentials()

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=args.days)

    entries = fetch_history(base_url, token, args.entity_id, start, now)

    if not entries:
        print(json.dumps([]))
        return

    if is_numeric(entries):
        result = aggregate_numeric(entries, args.period, args.stat)
    else:
        result = aggregate_states(entries, now)
        divisor = {"min": 1, "hours": 60, "days": 1440}[args.unit]
        if divisor != 1:
            result = [{"t": r["t"], "v": round(r["v"] / divisor, 1)} for r in result]

    print(json.dumps(result))


if __name__ == "__main__":
    main()
