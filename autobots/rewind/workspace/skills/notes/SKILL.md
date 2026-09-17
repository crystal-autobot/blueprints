---
name: notes
description: Save transcripts, create and search markdown notes in the vault.
tool: exec
---

# Notes

Manage the markdown vault in `notes/`.

## When to use

- A voice memo or audio file was transcribed and needs saving
- The user asks "what did I say about ...", "find my note on ...", "recent notes"
- The user asks for open action items or a digest

## Commands

All commands run from the workspace root.

Never put transcript or note text in the command string. Use the `write_file` tool to put the text in `notes/.staging.md` first, then redirect that file into the script.

Save a raw transcript (prints the created path):
```bash
python3 skills/notes/notes.py transcript < notes/.staging.md
```

Create or overwrite a topic note (body from `notes/.staging.md`, frontmatter generated):
```bash
python3 skills/notes/notes.py write --title "Kitchen renovation" --tags home,budget < notes/.staging.md
```

Append a section to an existing topic note (keeps frontmatter, bumps `updated`):
```bash
python3 skills/notes/notes.py append --title "Kitchen renovation" < notes/.staging.md
```

Add links to today's daily note:
```bash
python3 skills/notes/notes.py daily --link "transcripts/2026-09-03-0912" --link "notes/kitchen-renovation"
```

`--link` takes the path printed by `transcript`/`write`/`append` with the leading `notes/` and the `.md` suffix removed, e.g. `notes/notes/kitchen-renovation.md` becomes `notes/kitchen-renovation`.

Search notes (case-insensitive, all words must match, prints path, title and matching lines):
```bash
python3 skills/notes/notes.py search "kitchen budget"
```

Recent notes:
```bash
python3 skills/notes/notes.py recent --limit 10
```

Open action items grouped by note:
```bash
python3 skills/notes/notes.py todos
```

## Tips

- Search before writing to avoid duplicate topics
- Use `read_file` to read a full note after `search` finds it
- Titles are turned into slugs: "Kitchen renovation" becomes `notes/notes/kitchen-renovation.md`
