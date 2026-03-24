---
name: flashcard
description: Generate visual flashcard images for vocabulary review
tool: exec
---

# Flashcard generator

## When to use

Use this skill when the user asks to create flashcards, wants a visual vocabulary review,
or when you want to reinforce newly learned words with images.

## How to generate

Run the Python script with JSON input via stdin:

```bash
echo '<json>' | python3 skills/flashcard/generate.py -o .output/flashcard.png
```

## Input format

JSON array of word objects:

```json
[
  {"word": "hablar", "translation": "to speak", "example": "Necesito hablar contigo"},
  {"word": "comer", "translation": "to eat", "example": "Vamos a comer juntos"}
]
```

## Parameters

- `-o <path>` — output file path (required)
- `--title <text>` — card title (default: "Vocabulary")
- `--cols <n>` — number of columns (default: 2, max: 3)
- `--theme <name>` — color theme: `ocean`, `forest`, `sunset`, `lavender`, `slate` (default: `ocean`)

## Rules

- Maximum 8 words per image for readability
- Always include an example sentence for each word
- Choose a theme that feels fresh — vary across generations
- Save output to `.output/` directory
