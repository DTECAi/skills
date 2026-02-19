---
name: screenshot-extractor
description: Use this skill whenever the user uploads or shares a screenshot (image) of a social media post, tweet, article, LinkedIn post, Reddit thread, newsletter, or any web content — especially related to generative AI, LLMs, prompts, AI tools, or research. Extracts structured information from the image and appends it to a local knowledge base organized by category. Also use this skill when the user asks to search, browse, or summarize their knowledge base, or when they want to review what has been saved.
---

# Screenshot Extraction & Knowledge Base System

## Overview

This skill processes screenshots of social media posts, articles, and web content. It uses Claude's vision capabilities to extract structured information and stores entries in a local Markdown + JSON knowledge base organized by category.

**Trigger phrases**: "save this", "extract this", "add this to my knowledge base", "what have I saved about X", "show me my saved [category]", uploading any image without context (assume extraction intent).

---

## Workflow

### Step 1: Analyze the Screenshot

When the user provides a screenshot, carefully examine it and extract:

| Field | Description |
|---|---|
| `source_platform` | Where it's from: Twitter/X, LinkedIn, Reddit, Substack, Medium, YouTube, HackerNews, Discord, other |
| `author` | Username, handle, or real name visible in the screenshot |
| `content` | Full verbatim text visible in the post/article (transcribe completely) |
| `url` | Any URL visible in the image (post URL, shared link, etc.) |
| `date_posted` | Date of the original post if visible |
| `date_saved` | Today's date (always include) |
| `category` | Assign from the Categories section below |
| `tags` | 3–7 relevant keyword tags (lowercase, hyphenated) |
| `summary` | One-sentence summary of the key insight or value |
| `key_links` | Any URLs mentioned or shared in the content |

### Step 2: Assign a Category

Assign exactly one primary category from this list:

| Category ID | When to use |
|---|---|
| `ai-news` | Product launches, company announcements, industry news, AI policy, funding rounds |
| `prompts` | Prompt templates, prompt engineering techniques, system prompts, examples that make LLMs behave differently |
| `tools` | AI tools, apps, APIs, plugins, frameworks, platforms, workflows |
| `research` | Academic papers, research findings, benchmark results, technical deep-dives |
| `threads` | Long-form Twitter/X threads, LinkedIn carousels, multi-post series with substantial insight |
| `articles` | Blog posts, newsletters, essays, opinion pieces, Substack posts |
| `quotes` | Memorable standalone quotes, hot takes, predictions from notable people |
| `links` | A post whose main value is a URL it shares (the link is the content) |
| `misc` | Anything that doesn't fit the above categories cleanly |

### Step 3: Store the Entry

Store data in `knowledge-base/` relative to wherever the user is working. Use this structure:

```
knowledge-base/
├── index.json                  # Master index of all entries
├── ai-news.md                  # Human-readable entries per category
├── prompts.md
├── tools.md
├── research.md
├── threads.md
├── articles.md
├── quotes.md
├── links.md
└── misc.md
```

**To add an entry**, run the management script:
```bash
python skills/screenshot-extractor/scripts/manage_kb.py add --data '<json>'
```

Or directly append to both `index.json` and the relevant category `.md` file using the formats below.

### Step 4: Confirm to the User

After saving, display a confirmation card:

```
Saved to knowledge base
Category : [category]
Author   : [author]
Source   : [platform]
Summary  : [one-sentence summary]
Tags     : [tag1, tag2, tag3]
```

Then ask: "Anything to add or correct before I save?"

---

## Storage Formats

### index.json format

Each entry in `index.json` is appended to the top-level `entries` array:

```json
{
  "id": "20260219-twitter-karpathy-001",
  "date_saved": "2026-02-19",
  "date_posted": "2026-02-18",
  "source_platform": "Twitter/X",
  "author": "@karpathy",
  "category": "ai-news",
  "tags": ["llm", "scaling", "training"],
  "summary": "Karpathy explains why next-token prediction is sufficient for AGI.",
  "url": "https://twitter.com/karpathy/status/...",
  "key_links": [],
  "content_preview": "First 200 characters of the content..."
}
```

**ID format**: `YYYYMMDD-[platform-slug]-[author-slug]-[3-digit-counter]`

### Category Markdown format

Each `.md` file uses this entry block, separated by `---`:

```markdown
## [Author] · [Platform] · [Date Saved]

**Summary**: [one-sentence summary]
**Tags**: `tag1` `tag2` `tag3`
**URL**: [url or "not visible"]

> [Full verbatim content transcribed from the screenshot]

**Key links**: [any URLs shared in the content, or "none"]

---
```

---

## Querying the Knowledge Base

When the user asks to search or browse their saved content:

1. Read `knowledge-base/index.json`
2. Filter by category, tags, author, or keyword as requested
3. Return a formatted list of matches with their summaries
4. Offer to show full content for any entry

**Example queries to handle**:
- "Show me everything I've saved about RAG"
- "What prompts have I collected?"
- "Find posts from Andrej Karpathy"
- "Summarize my ai-news category"
- "What tools have I saved this month?"

---

## Batch Processing

When the user sends multiple screenshots at once:
1. Process each one sequentially
2. Show a numbered list of all extracted entries for confirmation before saving
3. Save all confirmed entries in one batch

---

## Edge Cases

- **No text visible**: Describe what is visually shown; categorize as `misc`; flag it clearly
- **Partial screenshot**: Extract what is visible; note "[content truncated]" if clearly cut off
- **Non-English content**: Transcribe as-is and add an English translation in a `translation` field
- **Duplicate detection**: Before saving, check `index.json` for entries with the same `author` + `date_posted` + `source_platform`. If found, alert the user
- **Multiple posts in one screenshot**: Create one entry per distinct post visible
- **URL-only post**: Set content to the URL; extract any caption/context; set category to `links`

---

## Initialization

If `knowledge-base/` does not exist yet, create it automatically:
```bash
python skills/screenshot-extractor/scripts/manage_kb.py init
```

This creates the directory structure and empty `index.json`.
