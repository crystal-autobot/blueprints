#!/usr/bin/env python3
"""Fetch entity history from Home Assistant and output downsampled JSON.

Usage:
  python3 fetch-history.py <entity_id> [hours]
  python3 fetch-history.py <entity_id> <start> <end>

Examples:
  python3 fetch-history.py sensor.living_room_temperature 12
  python3 fetch-history.py sensor.humidity 2025-03-20 2025-03-21

Output: JSON array of {"t": "HH:MM", "v": float}
Downsamples to ~100 points max.

Requires env vars: HA_URL, HA_TOKEN
"""

import json
import sys
from datetime import datetime

from ha_client import fetch_history, get_ha_credentials, parse_args_time


def downsample(entries, max_points=100):
    points = []
    for e in entries:
        state = e.get("state", "")
        ts = e.get("last_changed", "")
        if state in ("unknown", "unavailable", "") or not ts:
            continue
        try:
            points.append((ts, float(state)))
        except ValueError:
            continue

    if len(points) <= max_points:
        return points

    step = len(points) / max_points
    return [points[int(i * step)] for i in range(max_points)]


def main():
    entity_id, start, end = parse_args_time(sys.argv, default_hours=12)
    base_url, token = get_ha_credentials()

    entries = fetch_history(base_url, token, entity_id, start, end)
    points = downsample(entries)

    multi_day = (end - start).total_seconds() > 86400
    time_fmt = "%m-%d %H:%M" if multi_day else "%H:%M"

    local_tz = datetime.now().astimezone().tzinfo
    result = []
    for ts, val in points:
        t = datetime.fromisoformat(ts).astimezone(local_tz).strftime(time_fmt)
        result.append({"t": t, "v": val})

    print(json.dumps(result))


if __name__ == "__main__":
    main()
