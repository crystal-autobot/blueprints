<p align="center">
  <img src="../../docs/images/optimus.jpg" width="120" alt="Optimus" />
</p>

<h1 align="center">Optimus</h1>

<p align="center">
  General-purpose autobot with all features enabled.<br/>
  The kitchen-sink blueprint — start here if you want everything.
</p>

---

## What's included

| Feature | Status | Details |
|---------|--------|---------|
| Telegram | Enabled | Streaming, custom commands, user allowlist |
| Slack | Ready | Socket mode, group policies, DM support |
| Web search | Enabled | Brave Search API |
| Image generation | Enabled | OpenAI (DALL-E / GPT Image) |
| Sandbox execution | Auto | Docker (macOS) or bubblewrap (Linux) |
| MCP servers | Ready | Add your own via config |
| SQLite plugin | Auto | Requires `sqlite3` CLI |
| GitHub plugin | Auto | Requires `gh` CLI |
| Weather plugin | Auto | Built-in via wttr.in |
| Custom skills | 2 | GIF generator, programming jokes |
| Memory | Enabled | Consolidation after 50 messages |

## Quick start

```bash
# Copy blueprint
cp -r autobots/optimus ~/my-autobot
cd ~/my-autobot

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# (Optional) Build sandbox
docker build -t autobot-sandbox -f Dockerfile.sandbox .

# Run
autobot gateway
```

## Configuration

### Channels

**Telegram** is enabled by default. Update `allow_from` in `config.yml` with your Telegram username:

```yaml
channels:
  telegram:
    enabled: true
    allow_from: ["your-username"]
```

**Slack** is pre-configured but disabled. To enable:

1. Create a [Slack app](https://api.slack.com/apps) with Socket Mode
2. Add `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN` to `.env`
3. Set `enabled: true` in `config.yml`

### Custom commands

Telegram macros let users trigger predefined prompts:

```yaml
custom_commands:
  macros:
    summarize:
      prompt: "Summarize our conversation in 3 bullet points"
      description: "Summarize the conversation"
```

## Skills

### GIF generator

Creates animated text GIFs. Triggered by "create a gif", "make a gif", etc.

Styles: `wave`, `typing`, `pulse`, `slide`, `rainbow`
Palettes: `blue`, `fire`, `green`, `purple`, `gold`

### Programming jokes

Tells programming jokes on demand. Categories: debugging, naming, git, languages.

## Personality

Optimus is configured as the Autobot leader — noble, decisive, and helpful. Customize `workspace/SOUL.md` and `workspace/AGENTS.md` to change the persona.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `BRAVE_API_KEY` | No | Brave Search API key (for web search) |
| `SLACK_BOT_TOKEN` | No | Slack bot token (if Slack enabled) |
| `SLACK_APP_TOKEN` | No | Slack app token (if Slack enabled) |
