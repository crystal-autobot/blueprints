<p align="center">
  <img src="../../docs/images/blaster.jpg" width="120" alt="Blaster" />
</p>

<h1 align="center">Blaster</h1>

<p align="center">
  Language learning companion and conversation partner.<br/>
  Practice speaking, build vocabulary, and get corrections — all through chat.
</p>

---

## What's included

| Feature | Status | Details |
|---------|--------|---------|
| Telegram | Enabled | Streaming, language learning commands |
| Web search | Enabled | Articles and cultural content in target language |
| Flashcard skill | Included | Visual vocabulary cards with themed styles |
| Sandbox execution | Auto | Docker (macOS) or bubblewrap (Linux) |
| Memory | Enabled | Tracks vocabulary, level, and progress |

## Documentation

- [Quick start](https://crystal-autobot.github.io/autobot/quickstart/) — install Autobot and run your first bot
- [Configuration](https://crystal-autobot.github.io/autobot/configuration/) — all config options explained

## Quick start

```bash
# Copy blueprint
cp -r autobots/blaster ~/my-language-bot
cd ~/my-language-bot

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# (Optional) Build sandbox
docker build -t blaster-sandbox -f Dockerfile.sandbox .

# Run
autobot gateway
```

## Configuration

### Language setup

Edit `workspace/USER.md` to set your target and native languages:

```markdown
- Target language: Spanish
- Native language: English
- Current level: B1
```

### Channels

Update `allow_from` in `config.yml` with your Telegram username:

```yaml
channels:
  telegram:
    allow_from: ["your-username"]
```

### Custom commands

| Command | Description |
|---------|-------------|
| `/practice` | Start a conversation in the target language |
| `/vocab` | Review recently learned words |
| `/quiz` | Quick vocabulary and grammar quiz |

## Skills

### Flashcard generator

Creates visual flashcard images for vocabulary review.

**Themes:** `ocean`, `forest`, `sunset`, `lavender`, `slate`

Generates images with word, translation, and example sentence — up to 8 words per card.

## Personality

Blaster is an enthusiastic language tutor — patient, encouraging, and always ready to chat. Corrects mistakes gently, introduces new words in context, and adapts to your level. Customize in `workspace/SOUL.md`.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `BRAVE_API_KEY` | No | Brave Search API key (for articles in target language) |
