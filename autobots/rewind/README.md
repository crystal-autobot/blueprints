<p align="center">
  <img src="../../docs/images/rewind.jpg" width="120" alt="Rewind" />
</p>

<h1 align="center">Rewind</h1>

<p align="center">
  Voice memos in, organized notes out.<br/>
  Send a voice message, Rewind transcribes it, files it into your Obsidian vault or Notion, and answers questions about it later.
</p>

---

## What's included

| Feature | Status | Details |
|---------|--------|---------|
| Telegram | Enabled | Voice messages, audio files, and text |
| Voice transcription | Enabled | Whisper via OpenAI, or Groq when configured |
| Obsidian vault | Enabled | Markdown notes with frontmatter and wikilinks in `workspace/notes` |
| Notion MCP | Optional | Mirror notes to a Notion page or database |
| Notes skill | Included | Save transcripts, create and search notes, list action items |
| Sandbox execution | Docker | Python standard library for the notes skill |
| Cron | Enabled | Ask for a weekly digest on a schedule |
| Web search | Optional | Look things up while organizing a note (needs BRAVE_API_KEY) |
| Memory | Enabled | Remembers your tags, language, and preferences |

## How it works

```
Voice memo -> Telegram -> Whisper transcription -> Rewind
                                                     |
                     +-------------------------------+-------------------------------+
                     v                               v                               v
          notes/transcripts/         notes/notes/<topic>.md            notes/daily/<date>.md
          raw words, never edited    organized note, tags, todos       links to everything captured today
```

Later, ask "what did I say about the kitchen budget?" and Rewind searches the vault and answers with the note it found.

## Documentation

- [Quick start](https://crystal-autobot.github.io/autobot/quickstart/) — install Autobot and run your first bot
- [Media & voice](https://crystal-autobot.github.io/autobot/media/) — how transcription works
- [MCP servers](https://crystal-autobot.github.io/autobot/mcp/) — connect Notion

## Quick start

```bash
# Copy blueprint
cp -r autobots/rewind ~/my-notes-bot
cd ~/my-notes-bot

# Set up environment
cp .env.example .env
chmod 600 .env
# Edit .env with your API keys

# Build sandbox
docker build -t rewind-sandbox -f Dockerfile.sandbox .

# Run
autobot gateway
```

Then send a voice message to your bot. Voice memos recorded on your phone can be shared to the Telegram chat as audio files too.

## Obsidian

Open `workspace/notes` as a vault in Obsidian. Notes use standard frontmatter and `[[wikilinks]]`, so graph view, tags, and search work out of the box. To sync across devices, put the bot folder in iCloud, Syncthing, or any folder Obsidian Sync already watches.

The vault stays inside the workspace so the bot's file tools can reach it while sandboxing stays on.

## Notion

Requires [Node.js](https://nodejs.org/) so `npx` can start the Notion MCP server.

1. Create an internal integration at [notion.so/profile/integrations](https://www.notion.so/profile/integrations)
2. Share the page or database where notes should go with the integration
3. Put the token in `.env` as `NOTION_TOKEN`
4. Uncomment the `mcp` block in `config.yml`
5. Tell Rewind the parent page in `workspace/USER.md`

Local markdown stays the source of truth. Notion is a mirror.

## Configuration

### Channels

Update `allow_from` in `config.yml` with your Telegram username:

```yaml
channels:
  telegram:
    allow_from: ["your-username"]
```

### Transcription

Whisper transcription uses the OpenAI key by default. Add a Groq key for faster, free transcription and uncomment the `groq` provider in `config.yml`. Groq is preferred when both are set.

### Custom commands

| Command | Description |
|---------|-------------|
| `/recent` | Ten most recent notes with one-line summaries |
| `/today` | Today's daily note |
| `/todos` | Open action items across all notes |
| `/digest` | Weekly digest of ideas, decisions, and action items |

Ask for "a digest every Sunday at 6pm" and Rewind schedules it with the built-in cron tool.

## Skills

### Notes

`workspace/skills/notes/notes.py` manages the vault. It uses only the Python standard library.

| Command | What it does |
|---------|-------------|
| `transcript` | Save a raw transcript with a timestamped name |
| `write` | Create or overwrite a topic note with frontmatter |
| `append` | Add a dated section to an existing note |
| `daily` | Link notes and transcripts from today's daily note |
| `search` | Find notes where all query words appear |
| `recent` | List recently updated notes |
| `todos` | List unchecked `- [ ]` items grouped by note |

## Personality

Rewind is a quiet, careful archivist. It confirms captures in a few lines, cites notes when answering, and never edits your words in a transcript. Customize in `workspace/SOUL.md`.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key (chat and Whisper transcription) |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram bot token from @BotFather |
| `ANTHROPIC_API_KEY` | No | Anthropic API key (if the `anthropic` model is enabled) |
| `GROQ_API_KEY` | No | Groq API key for faster transcription (also uncomment the `groq` provider in `config.yml`) |
| `BRAVE_API_KEY` | No | Brave Search API key (for web search) |
| `NOTION_TOKEN` | No | Notion integration token (for Notion sync) |
| `TZ` | No | Timezone for note dates inside the sandbox (e.g. `Europe/Berlin`); defaults to UTC |
