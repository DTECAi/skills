# Screenshot Extractor — Reference

## Entry Schema

Full JSON schema for a knowledge base entry:

```json
{
  "id": "20260219-twitter-karpathy-001",
  "date_saved": "2026-02-19",
  "date_posted": "2026-02-18",
  "source_platform": "Twitter/X",
  "author": "@karpathy",
  "category": "ai-news",
  "tags": ["llm", "scaling", "training", "gpt"],
  "summary": "Karpathy explains why next-token prediction is sufficient for emergent reasoning.",
  "url": "https://twitter.com/karpathy/status/...",
  "content": "Full verbatim text extracted from the screenshot...",
  "key_links": ["https://arxiv.org/..."],
  "translation": ""
}
```

### Required Fields

| Field | Type | Notes |
|---|---|---|
| `date_saved` | string | YYYY-MM-DD, always today |
| `source_platform` | string | Platform name |
| `author` | string | Handle or name as shown |
| `category` | string | One of the 9 category IDs |
| `summary` | string | Single sentence, ≤150 chars |

### Optional Fields

| Field | Type | Notes |
|---|---|---|
| `date_posted` | string | YYYY-MM-DD or as visible |
| `url` | string | URL of the post itself |
| `content` | string | Full verbatim text |
| `tags` | string[] | 3–7 lowercase hyphenated tags |
| `key_links` | string[] | URLs shared in the post |
| `translation` | string | English translation if non-English |

---

## Categories Quick Reference

| ID | Use for |
|---|---|
| `ai-news` | Announcements, launches, policy, funding |
| `prompts` | Prompt templates, system prompts, techniques |
| `tools` | Apps, APIs, frameworks, platforms |
| `research` | Papers, benchmarks, technical findings |
| `threads` | Multi-post threads and carousels |
| `articles` | Blog posts, newsletters, essays |
| `quotes` | Standalone insights and predictions |
| `links` | Posts where the URL is the main value |
| `misc` | Uncategorized content |

---

## Tag Conventions

Use lowercase, hyphenated tags. Common tags:

**Model-related**: `gpt-4o`, `claude`, `gemini`, `llama`, `mistral`, `o3`, `deepseek`
**Technique**: `rag`, `chain-of-thought`, `function-calling`, `fine-tuning`, `agents`, `evals`
**Topic**: `alignment`, `safety`, `scaling`, `multimodal`, `robotics`, `code-generation`
**Format**: `paper`, `tutorial`, `benchmark`, `dataset`, `demo`, `tool`, `open-source`
**Source**: `twitter-thread`, `substack`, `hacker-news`, `reddit`

---

## Platform Name Conventions

Use these standard names for `source_platform`:

- `Twitter/X`
- `LinkedIn`
- `Reddit`
- `Substack`
- `Medium`
- `HackerNews`
- `YouTube`
- `Discord`
- `GitHub`
- `Newsletter`
- `Blog`
- `Unknown`

---

## Management Script Examples

```bash
# Initialize
python manage_kb.py init

# Add entry from JSON
python manage_kb.py add --data '{
  "source_platform": "Twitter/X",
  "author": "@sama",
  "category": "ai-news",
  "tags": ["openai", "gpt-5", "announcement"],
  "summary": "Sam Altman announces GPT-5 release timeline.",
  "content": "Full tweet text here...",
  "date_posted": "2026-02-19"
}'

# Search
python manage_kb.py search --query "RAG retrieval"
python manage_kb.py search --query "prompt" --category prompts

# List
python manage_kb.py list --category tools --limit 10
python manage_kb.py list

# Stats
python manage_kb.py stats

# Export
python manage_kb.py export --output my-kb-backup.md
```

---

## Knowledge Base File Structure

```
knowledge-base/
├── index.json       # All entries, newest first, compact format
├── ai-news.md       # Full entries with content
├── prompts.md
├── tools.md
├── research.md
├── threads.md
├── articles.md
├── quotes.md
├── links.md
└── misc.md
```

The `index.json` is optimized for search and filtering. The `.md` files contain the full verbatim content for reading.

---

## Example Knowledge Base Entry (Markdown)

```markdown
## @karpathy · Twitter/X · Saved 2026-02-19

**ID**: `20260219-twitterx-karpathy-001`
**Posted**: 2026-02-18
**Summary**: Karpathy explains why next-token prediction is sufficient for emergent reasoning.
**Tags**: `llm` `scaling` `training`
**URL**: https://twitter.com/karpathy/status/...

> I've been thinking about why next token prediction keeps surprising us.
> The key insight is that to predict the next token well you need to
> model the entire process that generated it...

**Key links**:
- https://arxiv.org/abs/...

---
```
