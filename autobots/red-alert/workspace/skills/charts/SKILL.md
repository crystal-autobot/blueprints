---
name: charts
description: Generate charts (line, bar, pie, timeline) from Home Assistant data.
tool: exec
---

## Getting data

| Script | What it fetches | Output format | Best for |
|--------|----------------|---------------|----------|
| `fetch-history.py` | Numeric sensor values, downsampled ~100 pts | `[{"t": "HH:MM", "v": float}]` | line |
| `fetch-stats.py` | Aggregated stats (auto-detects numeric/state) | `[{"t": "label", "v": float}]` | bar, pie |
| `fetch-states.py` | State transitions (deduped) | `[{"when": "ISO8601", "state": "..."}]` | timeline |

### fetch-history.py

```
python3 skills/charts/scripts/fetch-history.py <entity_id> [hours]
python3 skills/charts/scripts/fetch-history.py <entity_id> <start> <end>
```

- `hours` — lookback (default: 12)
- `start end` — date range (`2025-03-20`, `2025-03-20T10:00`)

### fetch-stats.py

```
python3 skills/charts/scripts/fetch-stats.py <entity_id> [options]
```

- `--days N` — lookback days (default: 7)
- `--period P` — hourly or daily (default: daily)
- `--stat S` — for numeric entities: avg, min, max, sum (default: avg)

For state entities outputs minutes spent in each state.

### fetch-states.py

```
python3 skills/charts/scripts/fetch-states.py <entity_id> [hours]
python3 skills/charts/scripts/fetch-states.py <entity_id> <start> <end>
```

- `hours` — lookback (default: 24)
- `start end` — date range

### MCP to exec pattern

When fetch scripts don't cover your use case, get data via any MCP tool and pipe to chart.py:

1. Call an MCP tool (e.g. `ha_get_state`, `ha_search_entities`)
2. Shape the response into the chart input format
3. Pass via exec: `echo '<json>' | python3 skills/charts/scripts/chart.py --type <type> ...`

## Rendering charts

Single script, pipe JSON via stdin:

```
... | python3 skills/charts/scripts/chart.py --type <type> [options] -o .output/chart.png
```

### Chart types

| Type | Input | Use case |
|------|-------|----------|
| `line` | `[{"t", "v"}]` | Sensor values over time |
| `bar` | `[{"t", "v"}]` | Daily averages, totals |
| `pie` | `[{"t", "v"}]` | Time distribution by state |
| `timeline` | `[{"when", "state"}]` | Device activity over time |

### Options

Common: `--type`, `-t` (title), `-o` (output), `--width`, `--height`

Line/bar: `-y` (ylabel), `--thresholds "val:label:color,..."`, `--color`

Timeline: `--colors "state:color,..."` (built-in: docked, cleaning, returning, paused, on, off, idle, sleep)

## Recipes

Temperature line chart:
```
python3 skills/charts/scripts/fetch-history.py sensor.living_room_temperature 12 | python3 skills/charts/scripts/chart.py --type line -t "Temperature" -y "°C" -o .output/chart.png
```

Humidity daily averages:
```
python3 skills/charts/scripts/fetch-stats.py sensor.living_room_humidity --days 7 | python3 skills/charts/scripts/chart.py --type bar -t "Humidity — daily average" -y "%" -o .output/chart.png
```

Device time by state:
```
python3 skills/charts/scripts/fetch-stats.py switch.living_room_light --days 7 | python3 skills/charts/scripts/chart.py --type pie -t "Light — time by state" -o .output/chart.png
```

Device timeline:
```
python3 skills/charts/scripts/fetch-states.py vacuum.robot_vacuum 24 | python3 skills/charts/scripts/chart.py --type timeline -t "Vacuum" --height 3 -o .output/timeline.png
```
