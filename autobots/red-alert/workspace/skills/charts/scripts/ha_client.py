#!/usr/bin/env python3
"""Shared HTTP client for Home Assistant API."""

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone


def parse_time(s):
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


def fmt_ts(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_history(base_url, token, entity_id, start, end):
    url = (
        f"{base_url}/api/history/period/{fmt_ts(start)}"
        f"?end_time={fmt_ts(end)}"
        f"&filter_entity_id={entity_id}&minimal_response&no_attributes"
    )
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason} for {entity_id}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)
    if not data or not data[0]:
        return []
    return data[0]


def parse_args_time(argv, default_hours=12):
    if len(argv) < 2:
        print(f"Usage: {argv[0]} <entity_id> [hours|start end]", file=sys.stderr)
        sys.exit(1)

    entity_id = argv[1]
    now = datetime.now(timezone.utc)

    if len(argv) == 4:
        start = parse_time(argv[2])
        end = parse_time(argv[3])
    elif len(argv) == 3:
        hours = int(argv[2])
        start = now - timedelta(hours=hours)
        end = now
    else:
        start = now - timedelta(hours=default_hours)
        end = now

    return entity_id, start, end


def get_ha_credentials():
    base_url = os.environ.get("HA_URL", "").rstrip("/")
    token = os.environ.get("HA_TOKEN", "")
    if not base_url or not token:
        print(json.dumps({"error": "HA_URL and HA_TOKEN env vars required"}))
        sys.exit(1)
    return base_url, token
