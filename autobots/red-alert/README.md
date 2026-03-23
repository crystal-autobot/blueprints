<p align="center">
  <img src="../../docs/images/red-alert.jpg" width="120" alt="Red Alert" />
</p>

<h1 align="center">Red Alert</h1>

<p align="center">
  Smart home monitor connected to Home Assistant.<br/>
  Track sensors, control devices, visualize data, and set up automations — all via chat.
</p>

---

## What's included

| Feature | Status | Details |
|---------|--------|---------|
| Telegram | Enabled | Streaming, home-specific commands |
| Home Assistant MCP | Enabled | Full HA integration via ha-mcp |
| Charts skill | Included | Line, bar, pie, timeline charts from HA data |
| Sandbox execution | Docker | Python with matplotlib and pandas |
| Memory | Enabled | Remembers devices, entities, preferences |

## Quick start

```bash
# Copy blueprint
cp -r autobots/red-alert ~/my-home-bot
cd ~/my-home-bot

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Build sandbox (required for charts)
docker build -t red-alert-sandbox -f Dockerfile.sandbox .

# Run
autobot gateway
```

## Prerequisites

```bash
# uv (required for ha-mcp)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Configuration

### Home Assistant

You need a [long-lived access token](https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token) from your Home Assistant instance:

1. Go to your HA profile page → Security → Long-lived access tokens
2. Create a new token
3. Add to `.env`:
   ```
   HA_URL=http://your-ha-instance:8123
   HA_TOKEN=your-long-lived-token
   ```

### MCP tools

The Home Assistant MCP server provides these tools:

| Tool | Description |
|------|-------------|
| `ha_get_state` | Get current state of an entity |
| `ha_get_overview` | Overview of all devices and entities |
| `ha_search_entities` | Search entities by name or type |
| `ha_call_service` | Call HA services (turn on/off, set speed, etc.) |
| `ha_config_get_automation` | Read automation configurations |
| `ha_config_set_automation` | Create or update automations |

### Custom commands

| Command | Description |
|---------|-------------|
| `/status` | Device status, sensor readings, weather |
| `/history` | Sensor chart for the last 12 hours |
| `/overview` | Full Home Assistant overview |

Customize the command prompts in `config.yml` to match your devices:

```yaml
custom_commands:
  macros:
    status:
      prompt: "Report: 1) Weather 2) Indoor air quality 3) Device status"
```

## Skills

### Charts

Generate charts from Home Assistant sensor data. Four chart types available:

| Type | Input | Use case |
|------|-------|----------|
| `line` | `[{"t": "HH:MM", "v": float}]` | Sensor values over time |
| `bar` | `[{"t": "label", "v": float}]` | Daily averages, totals |
| `pie` | `[{"t": "label", "v": float}]` | Time distribution by state |
| `timeline` | `[{"when": "ISO8601", "state": "..."}]` | Device activity over time |

**Data fetching scripts** (run inside sandbox with HA_URL and HA_TOKEN):

| Script | Purpose | Output |
|--------|---------|--------|
| `fetch-history.py` | Numeric sensor values (downsampled) | `[{"t", "v"}]` |
| `fetch-stats.py` | Aggregated stats (avg/min/max or state duration) | `[{"t", "v"}]` |
| `fetch-states.py` | State transitions (deduped) | `[{"when", "state"}]` |

**Example — temperature chart:**
```bash
python3 skills/charts/scripts/fetch-history.py sensor.living_room_temperature 12 \
  | python3 skills/charts/scripts/chart.py --type line -t "Living room temperature" -y "°C" -o .output/temp.png
```

**Example — device state timeline:**
```bash
python3 skills/charts/scripts/fetch-states.py switch.living_room_light 24 \
  | python3 skills/charts/scripts/chart.py --type timeline -t "Light" --height 3 -o .output/light.png
```

## Personality

Red Alert is a vigilant home guardian — concise, proactive, and focused on keeping your home safe and comfortable. Customize in `workspace/SOUL.md`.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `HA_URL` | Yes | Home Assistant URL (e.g. `http://homeassistant.local:8123`) |
| `HA_TOKEN` | Yes | Home Assistant long-lived access token |
