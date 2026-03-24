#!/usr/bin/env python3
"""Generate visual flashcard images for vocabulary review."""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

THEMES = {
    "ocean": {
        "bg": "#1a2332",
        "card": "#243447",
        "word": "#5dade2",
        "translation": "#f0f0f0",
        "example": "#aab7c4",
        "title": "#5dade2",
        "border": "#2e86c1",
    },
    "forest": {
        "bg": "#1a2e1a",
        "card": "#2d4a2d",
        "word": "#82e085",
        "translation": "#f0f0f0",
        "example": "#a8c5a8",
        "title": "#82e085",
        "border": "#52be56",
    },
    "sunset": {
        "bg": "#2e1a1a",
        "card": "#4a2d2d",
        "word": "#e8956a",
        "translation": "#f0f0f0",
        "example": "#c5a8a8",
        "title": "#e8956a",
        "border": "#c0694a",
    },
    "lavender": {
        "bg": "#221a2e",
        "card": "#372d4a",
        "word": "#b39ddb",
        "translation": "#f0f0f0",
        "example": "#b0a8c5",
        "title": "#b39ddb",
        "border": "#7e57c2",
    },
    "slate": {
        "bg": "#1e1e2e",
        "card": "#313244",
        "word": "#89b4fa",
        "translation": "#f0f0f0",
        "example": "#a6adc8",
        "title": "#89b4fa",
        "border": "#585b70",
    },
}

CARD_WIDTH = 340
CARD_HEIGHT = 140
CARD_PADDING = 16
CARD_GAP = 16
MARGIN = 32
TITLE_HEIGHT = 60


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines or [""]


def load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except OSError:
        pass
    try:
        return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans.ttf", size)
    except OSError:
        pass
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def load_font_bold(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
    except OSError:
        pass
    try:
        return ImageFont.truetype("/usr/share/fonts/TTF/DejaVuSans-Bold.ttf", size)
    except OSError:
        pass
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return load_font(size)


def draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int, int, int],
    radius: int,
    fill: str,
    outline: str | None = None,
):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def generate(words: list[dict], title: str, cols: int, theme_name: str, output: str):
    theme = THEMES.get(theme_name, THEMES["ocean"])
    cols = min(cols, 3)
    rows = (len(words) + cols - 1) // cols

    img_width = MARGIN * 2 + cols * CARD_WIDTH + (cols - 1) * CARD_GAP
    img_height = MARGIN + TITLE_HEIGHT + rows * CARD_HEIGHT + (rows - 1) * CARD_GAP + MARGIN

    img = Image.new("RGB", (img_width, img_height), hex_to_rgb(theme["bg"]))
    draw = ImageDraw.Draw(img)

    font_title = load_font_bold(22)
    font_word = load_font_bold(17)
    font_translation = load_font(14)
    font_example = load_font(12)

    # Title
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text(
        ((img_width - tw) // 2, MARGIN + 8),
        title,
        fill=hex_to_rgb(theme["title"]),
        font=font_title,
    )

    for i, entry in enumerate(words):
        row = i // cols
        col = i % cols

        x = MARGIN + col * (CARD_WIDTH + CARD_GAP)
        y = MARGIN + TITLE_HEIGHT + row * (CARD_HEIGHT + CARD_GAP)

        draw_rounded_rect(
            draw,
            (x, y, x + CARD_WIDTH, y + CARD_HEIGHT),
            radius=10,
            fill=hex_to_rgb(theme["card"]),
            outline=hex_to_rgb(theme["border"]),
        )

        word = entry.get("word", "")
        translation = entry.get("translation", "")
        example = entry.get("example", "")

        cy = y + CARD_PADDING

        # Word
        draw.text((x + CARD_PADDING, cy), word, fill=hex_to_rgb(theme["word"]), font=font_word)
        cy += 24

        # Translation
        draw.text(
            (x + CARD_PADDING, cy),
            translation,
            fill=hex_to_rgb(theme["translation"]),
            font=font_translation,
        )
        cy += 22

        # Example (wrapped)
        max_text_w = CARD_WIDTH - CARD_PADDING * 2
        lines = wrap_text(example, font_example, max_text_w, draw)
        for line in lines[:2]:
            draw.text(
                (x + CARD_PADDING, cy),
                line,
                fill=hex_to_rgb(theme["example"]),
                font=font_example,
            )
            cy += 16

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    img.save(output)
    print(json.dumps({"ok": True, "path": output}))


def main():
    parser = argparse.ArgumentParser(description="Generate vocabulary flashcards")
    parser.add_argument("-o", "--output", required=True, help="Output image path")
    parser.add_argument("--title", default="Vocabulary", help="Card title")
    parser.add_argument("--cols", type=int, default=2, help="Number of columns (max 3)")
    parser.add_argument("--theme", default="ocean", choices=list(THEMES.keys()), help="Color theme")
    args = parser.parse_args()

    data = json.load(sys.stdin)
    if not isinstance(data, list):
        print(json.dumps({"ok": False, "error": "Input must be a JSON array"}), file=sys.stderr)
        sys.exit(1)

    words = data[:8]
    generate(words, args.title, args.cols, args.theme, args.output)


if __name__ == "__main__":
    main()
