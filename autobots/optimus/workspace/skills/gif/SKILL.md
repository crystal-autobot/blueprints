---
name: gif
description: Generate animated GIFs from text prompts using Python.
tool: exec
---

# GIF generator

Create animated text GIFs from user prompts.

## When to use

Activate when the user asks for:
- "create a gif"
- "make a gif"
- "generate a gif"
- "gif of ..."
- "animated text"

## How to generate

Call the `exec` tool with exactly this command (replace text/style/output as needed):

```
python3 skills/gif/generate.py --text "YOUR TEXT" --style wave --output .output/gif_output.gif
```

## Rules

- Always use the exact command above via the `exec` tool. Do not modify it.
- Do not use `python -c` or `python3 -c`. Use the provided script instead.
- Do not write your own Python script. Use `skills/gif/generate.py` which is already provided.
- Pillow is pre-installed in the sandbox image built from `Dockerfile.sandbox`.

### Parameters

| Parameter    | Required | Default | Description                              |
|-------------|----------|---------|------------------------------------------|
| `--text`    | yes      | —       | Text to animate                          |
| `--style`   | no       | wave    | Animation style (see below)              |
| `--output`  | no       | .output/output.gif | Output file path              |
| `--width`   | no       | 480     | Canvas width in pixels                   |
| `--height`  | no       | 160     | Canvas height in pixels                  |
| `--fps`     | no       | 15      | Frames per second                        |
| `--duration`| no       | 2.0     | Animation duration in seconds            |
| `--palette` | no       | blue    | Color palette (see below)                |

### Styles

- **wave** — characters oscillate vertically with phase offset (good for greetings, fun text)
- **typing** — characters appear one by one with a blinking cursor (good for code, terminal feel)
- **pulse** — text scales up and down with color cycling (good for emphasis, alerts)
- **slide** — text slides in from the left and settles (good for reveals, announcements)
- **rainbow** — each character cycles through rainbow colors (good for celebrations)

### Palettes

- **blue** — cool blue to pink gradient (default)
- **fire** — red to yellow
- **green** — mint to lime
- **purple** — violet to cyan
- **gold** — golden to orange

## Guidelines

- Pick style and palette based on the mood of the prompt
- For short punchy text (1-3 words): use `pulse` or `slide`
- For longer text: use `wave` or `typing`
- For celebrations: use `rainbow`
- Keep text concise — long sentences don't animate well
- Increase `--width` for longer text, increase `--height` for larger fonts
- After generating, send the GIF file to the user
