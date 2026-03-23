#!/usr/bin/env python3
"""Generate charts from JSON data piped via stdin.

Supported chart types:
  - line:     time-series line chart from [{"t": "HH:MM", "v": float}]
  - bar:      bar chart from [{"t": "label", "v": float}]
  - pie:      pie chart from [{"t": "label", "v": float}]
  - timeline: horizontal state timeline from [{"when"|"t": "ISO8601", "state": "..."}]

Usage:
  echo '<json>' | python3 chart.py --type line [options] -o .output/chart.png

Common options:
  --type TYPE             Chart type: line, bar, pie, timeline (default: line)
  -t, --title TITLE       Chart title (default: "Chart")
  -o, --output PATH       Output file (default: chart.png)
  --width WIDTH           Figure width (default: 10)
  --height HEIGHT         Figure height (default: 5)

Line/bar options:
  -y, --ylabel LABEL      Y-axis label (default: "Value")
  --thresholds SPEC       Horizontal lines: "val:label:color,val:label:color"
  --color COLOR           Line/bar color (default: #2196F3)

Timeline options:
  --colors SPEC           State colors: "state:color,state:color"
"""

import argparse
import json
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle


TIMELINE_COLORS = {
    "docked": "#2ecc71",
    "cleaning": "#e74c3c",
    "returning": "#f39c12",
    "paused": "#9b59b6",
    "on": "#2ecc71",
    "off": "#95a5a6",
    "unavailable": "#555555",
    "unknown": "#555555",
    "idle": "#95a5a6",
    "sleep": "#3498db",
}


def parse_kv(spec):
    result = {}
    if not spec:
        return result
    for part in spec.split(","):
        pieces = part.split(":")
        if len(pieces) == 2:
            result[pieces[0].strip()] = pieces[1].strip()
    return result


def parse_thresholds(spec):
    if not spec:
        return []
    thresholds = []
    for part in spec.split(","):
        pieces = part.split(":")
        if len(pieces) == 3:
            thresholds.append((float(pieces[0]), pieces[1], pieces[2]))
        elif len(pieces) == 2:
            thresholds.append((float(pieces[0]), pieces[1], "gray"))
    return thresholds


def render_line(data, args):
    if len(data) < 2:
        print("Line chart requires at least 2 data points", file=sys.stderr)
        sys.exit(1)

    times = [d["t"] for d in data]
    values = [d["v"] for d in data]

    fig, ax = plt.subplots(figsize=(args.width, args.height))
    ax.plot(times, values, linewidth=2, color=args.color)

    for val, label, color in parse_thresholds(args.thresholds):
        ax.axhline(y=val, color=color, linestyle="--", alpha=0.5, label=f"{label} ({val})")

    step = max(1, len(times) // 12)
    ax.set_xticks(range(0, len(times), step))
    ax.set_xticklabels([times[i] for i in range(0, len(times), step)], rotation=45)

    ax.set_xlabel("Time")
    ax.set_ylabel(args.ylabel)
    ax.set_title(args.title)
    if parse_thresholds(args.thresholds):
        ax.legend()
    ax.grid(True, alpha=0.3)
    return fig


def render_bar(data, args):
    labels = [d["t"] for d in data]
    values = [d["v"] for d in data]

    fig, ax = plt.subplots(figsize=(args.width, args.height))
    ax.bar(labels, values, color=args.color)

    for val, label, color in parse_thresholds(args.thresholds):
        ax.axhline(y=val, color=color, linestyle="--", alpha=0.5, label=f"{label} ({val})")

    ax.set_ylabel(args.ylabel)
    ax.set_title(args.title)
    ax.tick_params(axis="x", rotation=45)
    if parse_thresholds(args.thresholds):
        ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    return fig


def render_pie(data, args):
    labels = [d["t"] for d in data]
    values = [d["v"] for d in data]
    total = sum(values)

    unit = args.ylabel if args.ylabel != "Value" else None

    def autopct(pct):
        val = pct / 100 * total
        if unit:
            return f"{val:.1f} {unit}"
        return f"{pct:.1f}%"

    fig, ax = plt.subplots(figsize=(args.width, args.height))
    ax.pie(values, labels=labels, autopct=autopct, startangle=90)
    ax.set_title(args.title)
    return fig


def render_timeline(data, args):
    entries = []
    for entry in data:
        ts = entry.get("when") or entry.get("t")
        state = entry.get("state", "")
        if ts and state:
            entries.append((ts, state))

    if not entries:
        print("No valid entries found", file=sys.stderr)
        sys.exit(1)

    colors = {**TIMELINE_COLORS, **parse_kv(args.colors)}

    segments = []
    for i, (ts, state) in enumerate(entries):
        start = datetime.fromisoformat(ts)
        if i + 1 < len(entries):
            end = datetime.fromisoformat(entries[i + 1][0])
        else:
            end = datetime.now().astimezone()
        segments.append((start, end, state))

    multi_day = (segments[-1][1] - segments[0][0]).total_seconds() > 86400
    time_fmt = "%m-%d %H:%M" if multi_day else "%H:%M"

    fig, ax = plt.subplots(figsize=(args.width, args.height))

    seen_states = set()
    for start, end, state in segments:
        color = colors.get(state, "#888888")
        width = mdates.date2num(end) - mdates.date2num(start)
        rect = Rectangle(
            (mdates.date2num(start), 0.1),
            width, 0.8,
            facecolor=color,
            edgecolor="white",
            linewidth=0.5,
        )
        ax.add_patch(rect)
        seen_states.add(state)

    ax.set_xlim(mdates.date2num(segments[0][0]), mdates.date2num(segments[-1][1]))
    ax.set_ylim(0, 1)
    ax.set_yticks([])

    ax.xaxis.set_major_formatter(mdates.DateFormatter(time_fmt))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    fig.autofmt_xdate()

    ax.set_title(args.title)
    ax.grid(True, axis="x", alpha=0.3)

    legend_handles = []
    for state in sorted(seen_states):
        color = colors.get(state, "#888888")
        legend_handles.append(Rectangle((0, 0), 1, 1, facecolor=color, label=state))
    ax.legend(handles=legend_handles, loc="upper right", fontsize=8)
    return fig


RENDERERS = {
    "line": render_line,
    "bar": render_bar,
    "pie": render_pie,
    "timeline": render_timeline,
}


def main():
    parser = argparse.ArgumentParser(description="Generate charts from JSON data")
    parser.add_argument("--type", default="line", choices=RENDERERS.keys())
    parser.add_argument("-t", "--title", default="Chart")
    parser.add_argument("-y", "--ylabel", default="Value")
    parser.add_argument("-o", "--output", default="chart.png")
    parser.add_argument("--thresholds", default="")
    parser.add_argument("--color", default="#2196F3")
    parser.add_argument("--colors", default="")
    parser.add_argument("--width", type=float, default=10)
    parser.add_argument("--height", type=float, default=5)
    args = parser.parse_args()

    data = json.load(sys.stdin)
    if not data:
        print("No data to chart", file=sys.stderr)
        sys.exit(1)

    fig = RENDERERS[args.type](data, args)
    fig.tight_layout()
    fig.savefig(args.output, dpi=150)
    print(args.output)


if __name__ == "__main__":
    main()
