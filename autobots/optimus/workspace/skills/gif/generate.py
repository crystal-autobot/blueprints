"""
Animated GIF generator from text prompts.

Usage:
    python generate.py --text "Hello World" --style wave --output output.gif
    python generate.py --text "Loading..." --style typing --output loading.gif
    python generate.py --text "BOOM" --style pulse --output boom.gif

Requires: Pillow (pip install Pillow)
"""

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Canvas defaults
DEFAULT_WIDTH = 480
DEFAULT_HEIGHT = 160
DEFAULT_FPS = 15
DEFAULT_DURATION_S = 2.0
BACKGROUND_COLOR = (25, 25, 35)
FONT_SIZE_RATIO = 0.35  # font size relative to canvas height
PADDING = 20


def get_font(size):
    """Load a monospace font, falling back to default."""
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    ]
    for path in font_paths:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:
        return ImageFont.load_default(size)


def fit_font_size(text, width, height):
    """Find the largest font size that fits the text within the canvas."""
    max_size = int(height * FONT_SIZE_RATIO)
    for size in range(max_size, 8, -1):
        font = get_font(size)
        bbox = font.getbbox(text)
        text_w = bbox[2] - bbox[0]
        if text_w <= width - 2 * PADDING:
            return font, size
    return get_font(10), 10


def text_center(draw, text, font, canvas_w, canvas_h):
    """Calculate x, y to center text on canvas."""
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (canvas_w - text_w) // 2
    y = (canvas_h - text_h) // 2
    return x, y


def lerp_color(c1, c2, t):
    """Linearly interpolate between two RGB colors."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


# -- Animation styles --


def style_wave(text, width, height, num_frames, palette):
    """Each character oscillates vertically with a phase offset."""
    frames = []
    font, _ = fit_font_size(text, width, height)
    amplitude = height * 0.08

    for i in range(num_frames):
        img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        t = i / num_frames

        char_widths = []
        for ch in text:
            bbox = font.getbbox(ch)
            char_widths.append(bbox[2] - bbox[0])
        total_w = sum(char_widths) + max(0, len(text) - 1) * 2
        start_x = (width - total_w) // 2
        base_y = height // 2 - font.getbbox(text)[3] // 2

        x = start_x
        for j, ch in enumerate(text):
            phase = t * 2 * math.pi + j * 0.5
            y_off = math.sin(phase) * amplitude
            color_t = (math.sin(phase) + 1) / 2
            color = lerp_color(palette[0], palette[1], color_t)
            draw.text((x, base_y + y_off), ch, fill=color, font=font)
            x += char_widths[j] + 2

        frames.append(img)
    return frames


def style_typing(text, width, height, num_frames, palette):
    """Characters appear one by one with a blinking cursor."""
    frames = []
    font, _ = fit_font_size(text, width, height)
    chars_total = len(text)
    cursor_char = "|"

    for i in range(num_frames):
        img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        t = i / num_frames

        visible = min(int(t * (chars_total + 1) * 1.2), chars_total)
        shown = text[:visible]

        cursor_on = (i % 8) < 5
        display = shown + (cursor_char if cursor_on else " ")

        x, y = text_center(draw, text + cursor_char, font, width, height)
        draw.text((x, y), display, fill=palette[0], font=font)

        frames.append(img)
    return frames


def style_pulse(text, width, height, num_frames, palette):
    """Text scales up and down with color cycling."""
    frames = []
    max_font, max_size = fit_font_size(text, width, height)

    for i in range(num_frames):
        img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        t = i / num_frames

        scale = 0.6 + 0.4 * abs(math.sin(t * math.pi))
        size = max(10, int(max_size * scale))
        font = get_font(size)

        x, y = text_center(draw, text, font, width, height)
        color_t = (math.sin(t * 2 * math.pi) + 1) / 2
        color = lerp_color(palette[0], palette[1], color_t)
        draw.text((x, y), text, fill=color, font=font)

        frames.append(img)
    return frames


def style_slide(text, width, height, num_frames, palette):
    """Text slides in from the left and settles in the center."""
    frames = []
    font, _ = fit_font_size(text, width, height)
    _, cy = text_center(ImageDraw.Draw(Image.new("RGB", (1, 1))), text, font, width, height)
    bbox = font.getbbox(text)
    text_w = bbox[2] - bbox[0]
    target_x = (width - text_w) // 2

    for i in range(num_frames):
        img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        t = i / num_frames

        # Ease-out cubic
        progress = 1 - (1 - t) ** 3
        x = int(-text_w + (target_x + text_w) * progress)

        color_t = min(1.0, t * 1.5)
        color = lerp_color(palette[0], palette[1], color_t)
        draw.text((x, cy), text, fill=color, font=font)

        frames.append(img)
    return frames


def style_rainbow(text, width, height, num_frames, palette):
    """Each character cycles through rainbow colors."""
    frames = []
    font, _ = fit_font_size(text, width, height)
    rainbow = [
        (255, 100, 100), (255, 200, 80), (255, 255, 100),
        (100, 255, 100), (100, 200, 255), (150, 100, 255),
    ]

    for i in range(num_frames):
        img = Image.new("RGB", (width, height), BACKGROUND_COLOR)
        draw = ImageDraw.Draw(img)
        t = i / num_frames

        char_widths = [font.getbbox(ch)[2] - font.getbbox(ch)[0] for ch in text]
        total_w = sum(char_widths) + max(0, len(text) - 1) * 2
        x = (width - total_w) // 2
        base_y = height // 2 - font.getbbox(text)[3] // 2

        for j, ch in enumerate(text):
            idx = (int(t * len(rainbow)) + j) % len(rainbow)
            color = rainbow[idx]
            draw.text((x, base_y), ch, fill=color, font=font)
            x += char_widths[j] + 2

        frames.append(img)
    return frames


STYLES = {
    "wave": style_wave,
    "typing": style_typing,
    "pulse": style_pulse,
    "slide": style_slide,
    "rainbow": style_rainbow,
}

DEFAULT_PALETTE = [(100, 200, 255), (255, 120, 200)]

PALETTES = {
    "blue":   [(100, 200, 255), (255, 120, 200)],
    "fire":   [(255, 80, 40),   (255, 220, 60)],
    "green":  [(60, 255, 160),  (200, 255, 60)],
    "purple": [(180, 80, 255),  (80, 200, 255)],
    "gold":   [(255, 200, 50),  (255, 120, 30)],
}


def generate_gif(text, style_name, output, width, height, fps, duration, palette_name):
    style_fn = STYLES.get(style_name)
    if not style_fn:
        print(f"Unknown style: {style_name}. Available: {', '.join(STYLES)}", file=sys.stderr)
        sys.exit(1)

    palette = PALETTES.get(palette_name, DEFAULT_PALETTE)
    num_frames = int(fps * duration)
    frames = style_fn(text, width, height, num_frames, palette)

    frame_duration_ms = int(1000 / fps)
    frames[0].save(
        output,
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=0,
        optimize=True,
    )
    print(f"GIF saved: {output} ({len(frames)} frames, {width}x{height})")


def main():
    parser = argparse.ArgumentParser(description="Generate animated GIF from text")
    parser.add_argument("--text", required=True, help="Text to animate")
    parser.add_argument("--style", default="wave", choices=list(STYLES.keys()),
                        help="Animation style (default: wave)")
    parser.add_argument("--output", default="output.gif", help="Output file path")
    parser.add_argument("--width", type=int, default=DEFAULT_WIDTH, help="Canvas width")
    parser.add_argument("--height", type=int, default=DEFAULT_HEIGHT, help="Canvas height")
    parser.add_argument("--fps", type=int, default=DEFAULT_FPS, help="Frames per second")
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION_S,
                        help="Animation duration in seconds")
    parser.add_argument("--palette", default="blue", choices=list(PALETTES.keys()),
                        help="Color palette (default: blue)")
    args = parser.parse_args()

    generate_gif(args.text, args.style, args.output, args.width, args.height,
                 args.fps, args.duration, args.palette)


if __name__ == "__main__":
    main()
