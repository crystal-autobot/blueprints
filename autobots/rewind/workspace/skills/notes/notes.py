#!/usr/bin/env python3
"""Manage the markdown notes vault.

Commands:
  transcript            Save stdin as a raw transcript, print its path
  write                 Create or overwrite a topic note from stdin
  append                Append stdin as a dated section to a topic note
  daily                 Add links to today's daily note
  search QUERY          Find notes matching all query words
  recent                List recently updated notes
  todos                 List unchecked action items grouped by note
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

VAULT = Path("notes")
TRANSCRIPTS = VAULT / "transcripts"
NOTES = VAULT / "notes"
DAILY = VAULT / "daily"
FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
TODO = re.compile(r"^\s*- \[ \] (.+)$")


def slugify(title):
    slug = re.sub(r"[^\w]+", "-", title.lower()).strip("-")
    return slug or f"untitled-{now()}"


def today():
    return datetime.now().strftime("%Y-%m-%d")


def now():
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def read_stdin():
    return sys.stdin.read().strip()


def parse_frontmatter(text):
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    fields = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields, text[match.end():]


def render_frontmatter(fields):
    lines = [f"{key}: {value}" for key, value in fields.items()]
    return "---\n" + "\n".join(lines) + "\n---\n"


def note_title(path):
    fields, _ = parse_frontmatter(path.read_text())
    return fields.get("title", path.stem)


def relative(path):
    return path.relative_to(VAULT).with_suffix("").as_posix()


def cmd_transcript(args):
    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    stamp = now()
    path = TRANSCRIPTS / f"{stamp}.md"
    suffix = 2
    while path.exists():
        path = TRANSCRIPTS / f"{stamp}-{suffix}.md"
        suffix += 1
    fields = {"title": f"Transcript {stamp}", "tags": "[transcript]", "created": today()}
    path.write_text(render_frontmatter(fields) + "\n" + read_stdin() + "\n")
    print(path)


def cmd_write(args):
    NOTES.mkdir(parents=True, exist_ok=True)
    path = NOTES / f"{slugify(args.title)}.md"
    created = today()
    if path.exists():
        created = parse_frontmatter(path.read_text())[0].get("created", created)
    tags = "[" + ", ".join(tag.strip() for tag in args.tags.split(",") if tag.strip()) + "]"
    fields = {"title": args.title, "tags": tags, "created": created, "updated": today()}
    path.write_text(render_frontmatter(fields) + "\n" + read_stdin() + "\n")
    print(path)


def cmd_append(args):
    path = NOTES / f"{slugify(args.title)}.md"
    if not path.exists():
        sys.exit(f"Note not found: {path}. Use write to create it.")
    fields, body = parse_frontmatter(path.read_text())
    fields["updated"] = today()
    section = f"\n## {today()}\n\n{read_stdin()}\n"
    path.write_text(render_frontmatter(fields) + body.rstrip("\n") + "\n" + section)
    print(path)


def cmd_daily(args):
    DAILY.mkdir(parents=True, exist_ok=True)
    path = DAILY / f"{today()}.md"
    if not path.exists():
        fields = {"title": today(), "tags": "[daily]", "created": today()}
        path.write_text(render_frontmatter(fields) + "\n")
    existing = path.read_text()
    new_links = [f"- [[{link}]]" for link in dict.fromkeys(args.link) if f"[[{link}]]" not in existing]
    if new_links:
        path.write_text(existing.rstrip("\n") + "\n" + "\n".join(new_links) + "\n")
    print(path)


def all_notes():
    return [path for folder in (NOTES, DAILY, TRANSCRIPTS) if folder.exists() for path in folder.glob("*.md")]


def cmd_search(args):
    words = [word.lower() for word in args.query.split()]
    hits = 0
    for path in sorted(all_notes()):
        text = path.read_text()
        lowered = text.lower()
        if not all(word in lowered for word in words):
            continue
        hits += 1
        print(f"{path} — {note_title(path)}")
        for line in text.splitlines():
            if any(word in line.lower() for word in words) and not line.startswith(("---", "title:", "tags:")):
                print(f"    {line.strip()[:160]}")
    if hits == 0:
        print("No notes found.")


def cmd_recent(args):
    notes = sorted(all_notes(), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in notes[: args.limit]:
        fields, _ = parse_frontmatter(path.read_text())
        print(f"{fields.get('updated', fields.get('created', ''))}  {relative(path)}  {fields.get('title', path.stem)}")


def cmd_todos(args):
    found = False
    for path in sorted(all_notes()):
        items = [TODO.match(line).group(1) for line in path.read_text().splitlines() if TODO.match(line)]
        if not items:
            continue
        found = True
        print(f"{note_title(path)} ({relative(path)})")
        for item in items:
            print(f"  - [ ] {item}")
    if not found:
        print("No open action items.")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("transcript").set_defaults(func=cmd_transcript)

    write = commands.add_parser("write")
    write.add_argument("--title", required=True)
    write.add_argument("--tags", default="")
    write.set_defaults(func=cmd_write)

    append = commands.add_parser("append")
    append.add_argument("--title", required=True)
    append.set_defaults(func=cmd_append)

    daily = commands.add_parser("daily")
    daily.add_argument("--link", action="append", default=[])
    daily.set_defaults(func=cmd_daily)

    search = commands.add_parser("search")
    search.add_argument("query")
    search.set_defaults(func=cmd_search)

    recent = commands.add_parser("recent")
    recent.add_argument("--limit", type=int, default=10)
    recent.set_defaults(func=cmd_recent)

    commands.add_parser("todos").set_defaults(func=cmd_todos)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
