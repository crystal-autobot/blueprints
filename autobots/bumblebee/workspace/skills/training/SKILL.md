---
name: training
description: Generate training charts and summaries from Garmin/Strava data.
tool: exec
---

# Training charts

Generate training progress charts from fitness data.

## When to use

Activate when the user asks for:
- "weekly summary"
- "training progress"
- "show my stats"
- "chart my runs"
- "how was my week"

## How it works

1. Fetch data from Garmin or Strava using MCP tools
2. Shape the response into chart input format
3. Pipe JSON to chart.py via exec

## Chart types

| Type | Input format | Use case |
|------|-------------|----------|
| `line` | `[{"t": "label", "v": float}]` | Progress over time (weekly mileage, avg pace) |
| `bar` | `[{"t": "label", "v": float}]` | Volume per day/week, activity counts |
| `pie` | `[{"t": "label", "v": float}]` | Time by sport, time in HR zones |

## Rendering

```bash
echo '<json>' | python3 skills/training/chart.py --type <type> [options] -o .output/chart.png
```

### Options

Common: `--type`, `-t` (title), `-o` (output), `--width`, `--height`

Line/bar: `-y` (ylabel), `--thresholds "val:label:color,..."`, `--color`

## Recipes

Weekly running volume:
```bash
echo '[{"t":"Mon","v":8.2},{"t":"Tue","v":0},{"t":"Wed","v":12.5},{"t":"Thu","v":6.0},{"t":"Fri","v":0},{"t":"Sat","v":21.1},{"t":"Sun","v":5.0}]' | python3 skills/training/chart.py --type bar -t "Weekly running volume" -y "km" --color "#FF6B35" -o .output/weekly.png
```

Monthly mileage trend:
```bash
echo '[{"t":"W1","v":35},{"t":"W2","v":42},{"t":"W3","v":48},{"t":"W4","v":30}]' | python3 skills/training/chart.py --type line -t "Monthly mileage" -y "km" --color "#2196F3" -o .output/monthly.png
```

Sport distribution:
```bash
echo '[{"t":"Running","v":180},{"t":"Cycling","v":120},{"t":"Swimming","v":45}]' | python3 skills/training/chart.py --type pie -t "Training time by sport" -y "min" -o .output/sports.png
```
