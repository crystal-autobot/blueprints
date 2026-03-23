#!/usr/bin/env python3
"""Fetch entity state transitions from Home Assistant.

Unlike fetch-history.py (numeric sensors), this fetches state changes
for entities like vacuums, fans, switches, etc.

Usage:
  python3 fetch-states.py <entity_id> [hours]
  python3 fetch-states.py <entity_id> <start> <end>

Examples:
  python3 fetch-states.py vacuum.robot_vacuum 24
  python3 fetch-states.py switch.living_room_light 2025-03-20 2025-03-21

Output: [{"when": "ISO8601", "state": "cleaning"}, ...]

Requires env vars: HA_URL, HA_TOKEN
"""

import json
import sys

from ha_client import fetch_history, get_ha_credentials, parse_args_time


def main():
    entity_id, start, end = parse_args_time(sys.argv, default_hours=24)
    base_url, token = get_ha_credentials()

    entries = fetch_history(base_url, token, entity_id, start, end)

    result = []
    prev_state = None
    for e in entries:
        state = e.get("state", "")
        ts = e.get("last_changed", "")
        if not ts or not state:
            continue
        if state == prev_state:
            continue
        prev_state = state
        result.append({"when": ts, "state": state})

    print(json.dumps(result))


if __name__ == "__main__":
    main()
