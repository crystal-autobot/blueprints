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

Save a raw transcript (prints the created path):
```bash
echo '<transcript text>' | python3 skills/notes/notes.py transcript
```

Create or overwrite a topic note (body from stdin, frontmatter generated):
```bash
echo '<markdown body>' | python3 skills/notes/notes.py write --title "Kitchen renovation" --tags home,budget
```

Append a section to an existing topic note (keeps frontmatter, bumps `updated`):
```bash
echo '<markdown body>' | python3 skills/notes/notes.py append --title "Kitchen renovation"
```

Add links to today's daily note:
```bash
python3 skills/notes/notes.py daily --link "transcripts/2026-09-03-0912" --link "notes/kitchen-renovation"
```

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
