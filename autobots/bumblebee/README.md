<p align="center">
  <img src="../../docs/images/bumblebee.jpg" width="120" alt="Bumblebee" />
</p>

<h1 align="center">Bumblebee</h1>

<p align="center">
  Training assistant with Strava and Garmin integrations.<br/>
  Your personal coach that tracks workouts, analyzes progress, and keeps you motivated.
</p>

---

## What's included

| Feature | Status | Details |
|---------|--------|---------|
| Telegram | Enabled | Training-specific commands |
| Garmin MCP | Enabled | Activity tracking, stats, health metrics |
| Strava MCP | Enabled | Recent activities, activities by date range |
| Web search | Optional | Training articles, race info lookup (needs BRAVE_API_KEY) |
| Sandbox execution | Docker | Python with matplotlib for charts |
| Training skill | Included | Weekly summaries, progress charts, workout logging |
| Memory | Enabled | Remembers your training history and goals |

## Documentation

- [Quick start](https://crystal-autobot.github.io/autobot/quickstart/) — install Autobot and run your first bot
- [Configuration](https://crystal-autobot.github.io/autobot/configuration/) — all config options explained

## Quick start

```bash
# Copy blueprint
cp -r autobots/bumblebee ~/my-training-bot
cd ~/my-training-bot

# Set up environment
cp .env.example .env
chmod 600 .env
# Edit .env with your API keys

# Build sandbox (required for charts)
docker build -t bumblebee-sandbox -f Dockerfile.sandbox .

# Run
autobot gateway
```

## Prerequisites

```bash
# uv (required for the Garmin and Strava MCP servers)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## Configuration

### Channels

Update `allow_from` in `config.yml` with your Telegram username:

```yaml
channels:
  telegram:
    allow_from: ["your-username"]
```

### MCP servers

Two fitness MCP servers are pre-configured:

**Garmin** — pulls activities, stats, and health data from Garmin Connect:
```yaml
garmin:
  command: "uvx"
  args: ["--python", "3.12", "--from", "git+https://github.com/Taxuspt/garmin_mcp", "garmin-mcp"]
```

If your Garmin account has MFA enabled, authenticate once before starting the bot: `uvx --python 3.12 --from git+https://github.com/Taxuspt/garmin_mcp garmin-mcp-auth`. Tokens are cached in `~/.garminconnect` and last about 6 months; the MCP server cannot prompt for an MFA code itself.

**Strava** — read your recent Strava activities and activities in a date range:
```yaml
strava:
  command: "uvx"
  args: ["strava-mcp-server"]
```

### Custom commands

| Command | Description |
|---------|-------------|
| `/week` | Weekly training summary with totals and highlights |
| `/progress` | Training progress over the last 30 days |
| `/plan` | Show upcoming training plan for the week |

## Skills

### Training

Generates training progress charts and weekly summaries. Uses data from Garmin and Strava MCP servers, processes it with Python, and renders charts via matplotlib.

**Chart types:**
- **Weekly volume** — bar chart of distance/duration per day
- **Heart rate zones** — pie chart of time in each HR zone
- **Progress over time** — line chart of weekly mileage trends
- **Activity breakdown** — bar chart by sport type (running, cycling, swimming)

## Personality

Bumblebee is an energetic, supportive training buddy — always enthusiastic about your progress, encouraging on rest days, and data-driven in recommendations. Customize in `workspace/SOUL.md`.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (if the `anthropic` model is enabled) |
| `BRAVE_API_KEY` | No | Brave Search API key (for web search) |
| `GARMIN_EMAIL` | Yes* | Garmin Connect email |
| `GARMIN_PASSWORD` | Yes* | Garmin Connect password |
| `STRAVA_CLIENT_ID` | Yes* | Strava API application client ID |
| `STRAVA_CLIENT_SECRET` | Yes* | Strava API application client secret |
| `STRAVA_REFRESH_TOKEN` | Yes* | Strava API refresh token |

*Required if corresponding MCP server is enabled. Remove unused servers from `config.yml`. Garmin credentials can be left blank once you have run `garmin-mcp-auth`.
