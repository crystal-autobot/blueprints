#!/usr/bin/env python3
"""Generate charts from JSON data piped via stdin.

Supported chart types:
  - line: time-series line chart from [{"t": "label", "v": float}]
  - bar:  bar chart from [{"t": "label", "v": float}]
  - pie:  pie chart from [{"t": "label", "v": float}]

Usage:
  echo '<json>' | python3 chart.py --type line [options] -o .output/chart.png

Common options:
  --type TYPE             Chart type: line, bar, pie (default: line)
  -t, --title TITLE       Chart title (default: "Chart")
  -o, --output PATH       Output file (default: chart.png)
  --width WIDTH           Figure width (default: 10)
  --height HEIGHT         Figure height (default: 5)

Line/bar options:
  -y, --ylabel LABEL      Y-axis label (default: "Value")
  --thresholds SPEC       Horizontal lines: "val:label:color,val:label:color"
  --color COLOR           Line/bar color (default: #2196F3)
"""

import argparse
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


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
    ax.plot(times, values, linewidth=2, color=args.color, marker="o", markersize=4)

    for val, label, color in parse_thresholds(args.thresholds):
        ax.axhline(y=val, color=color, linestyle="--", alpha=0.5, label=f"{label} ({val})")

    step = max(1, len(times) // 12)
    ax.set_xticks(range(0, len(times), step))
    ax.set_xticklabels([times[i] for i in range(0, len(times), step)], rotation=45)

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


RENDERERS = {
    "line": render_line,
    "bar": render_bar,
    "pie": render_pie,
}


def main():
    parser = argparse.ArgumentParser(description="Generate charts from JSON data")
    parser.add_argument("--type", default="line", choices=RENDERERS.keys())
    parser.add_argument("-t", "--title", default="Chart")
    parser.add_argument("-y", "--ylabel", default="Value")
    parser.add_argument("-o", "--output", default="chart.png")
    parser.add_argument("--thresholds", default="")
    parser.add_argument("--color", default="#2196F3")
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
