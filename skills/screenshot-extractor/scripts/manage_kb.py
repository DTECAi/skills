#!/usr/bin/env python3
"""
Knowledge Base Manager for Screenshot Extractor Skill
Manages a local knowledge base of extracted screenshot content.

Usage:
    python manage_kb.py init                      # Initialize knowledge base
    python manage_kb.py add --data '<json>'       # Add a new entry
    python manage_kb.py search --query 'RAG'      # Search entries
    python manage_kb.py list --category prompts   # List by category
    python manage_kb.py stats                     # Show statistics
    python manage_kb.py export --format md        # Export to markdown
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path


CATEGORIES = [
    "ai-news",
    "prompts",
    "tools",
    "research",
    "threads",
    "articles",
    "quotes",
    "links",
    "misc",
]

CATEGORY_DESCRIPTIONS = {
    "ai-news":   "Product launches, company announcements, industry news, policy, funding",
    "prompts":   "Prompt templates, techniques, system prompts, engineering examples",
    "tools":     "AI tools, apps, APIs, plugins, frameworks, platforms",
    "research":  "Papers, research findings, benchmarks, technical deep-dives",
    "threads":   "Long-form Twitter threads, LinkedIn carousels, multi-post series",
    "articles":  "Blog posts, newsletters, essays, opinion pieces, Substack",
    "quotes":    "Memorable quotes, hot takes, predictions from notable people",
    "links":     "Posts whose primary value is a URL they share",
    "misc":      "Content that doesn't fit other categories",
}

INDEX_FILE = "index.json"
KB_DIR_NAME = "knowledge-base"


def get_kb_dir() -> Path:
    """Find or return the knowledge-base directory path."""
    # Search upward from cwd for existing kb, or use cwd
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / KB_DIR_NAME
        if candidate.exists():
            return candidate
    return cwd / KB_DIR_NAME


def init_kb(kb_dir: Path) -> None:
    """Initialize the knowledge base directory structure."""
    kb_dir.mkdir(parents=True, exist_ok=True)

    index_path = kb_dir / INDEX_FILE
    if not index_path.exists():
        index_data = {
            "version": "1.0",
            "created": datetime.now().strftime("%Y-%m-%d"),
            "entries": [],
        }
        index_path.write_text(json.dumps(index_data, indent=2))
        print(f"Created: {index_path}")

    for category in CATEGORIES:
        md_path = kb_dir / f"{category}.md"
        if not md_path.exists():
            header = (
                f"# {category.replace('-', ' ').title()}\n\n"
                f"_{CATEGORY_DESCRIPTIONS[category]}_\n\n"
            )
            md_path.write_text(header)
            print(f"Created: {md_path}")

    print(f"\nKnowledge base initialized at: {kb_dir}")


def load_index(kb_dir: Path) -> dict:
    index_path = kb_dir / INDEX_FILE
    if not index_path.exists():
        print(f"No knowledge base found at {kb_dir}. Run: python manage_kb.py init")
        sys.exit(1)
    return json.loads(index_path.read_text())


def save_index(kb_dir: Path, index_data: dict) -> None:
    index_path = kb_dir / INDEX_FILE
    index_path.write_text(json.dumps(index_data, indent=2))


def generate_id(entry: dict, existing_ids: list[str]) -> str:
    """Generate a unique ID for an entry."""
    date = entry.get("date_saved", datetime.now().strftime("%Y-%m-%d")).replace("-", "")
    platform = re.sub(r"[^a-z0-9]", "", entry.get("source_platform", "unknown").lower())[:10]
    author = re.sub(r"[^a-z0-9]", "", entry.get("author", "unknown").lower().lstrip("@"))[:12]

    counter = 1
    while True:
        candidate = f"{date}-{platform}-{author}-{counter:03d}"
        if candidate not in existing_ids:
            return candidate
        counter += 1


def add_entry(kb_dir: Path, entry: dict, force: bool = False) -> None:
    """Add a new entry to the knowledge base."""
    index_data = load_index(kb_dir)
    existing_ids = [e["id"] for e in index_data["entries"]]

    # Validate category
    category = entry.get("category", "misc")
    if category not in CATEGORIES:
        print(f"Warning: unknown category '{category}', using 'misc'")
        category = "misc"
        entry["category"] = category

    # Assign ID and timestamp
    entry_id = generate_id(entry, existing_ids)
    entry["id"] = entry_id
    if "date_saved" not in entry:
        entry["date_saved"] = datetime.now().strftime("%Y-%m-%d")

    # Duplicate check (same author + date_posted + platform, only when date_posted known)
    date_posted = entry.get("date_posted", "")
    if not force and date_posted:
        for existing in index_data["entries"]:
            if (
                existing.get("author") == entry.get("author")
                and existing.get("date_posted") == date_posted
                and existing.get("source_platform") == entry.get("source_platform")
            ):
                print(
                    f"Warning: Possible duplicate detected.\n"
                    f"  Existing: {existing['id']} — {existing.get('summary', '')}\n"
                    f"  Add anyway? (y/N): ",
                    end="",
                )
                if input().strip().lower() != "y":
                    print("Skipped.")
                    return

    # Build index entry (compact version)
    content = entry.get("content", "")
    index_entry = {
        "id": entry_id,
        "date_saved": entry.get("date_saved"),
        "date_posted": entry.get("date_posted", ""),
        "source_platform": entry.get("source_platform", ""),
        "author": entry.get("author", ""),
        "category": category,
        "tags": entry.get("tags", []),
        "summary": entry.get("summary", ""),
        "url": entry.get("url", ""),
        "key_links": entry.get("key_links", []),
        "content_preview": content[:200] + ("..." if len(content) > 200 else ""),
    }

    # Append to index
    index_data["entries"].insert(0, index_entry)  # newest first
    save_index(kb_dir, index_data)

    # Append to category markdown file
    md_path = kb_dir / f"{category}.md"
    date_saved = entry.get("date_saved", "")
    date_posted = entry.get("date_posted", "")
    author = entry.get("author", "unknown")
    platform = entry.get("source_platform", "")
    summary = entry.get("summary", "")
    tags = entry.get("tags", [])
    url = entry.get("url", "not visible")
    key_links = entry.get("key_links", [])
    translation = entry.get("translation", "")

    tags_str = " ".join(f"`{t}`" for t in tags) if tags else "none"
    key_links_str = "\n".join(f"- {link}" for link in key_links) if key_links else "none"

    md_entry = (
        f"\n## {author} · {platform} · Saved {date_saved}\n\n"
        f"**ID**: `{entry_id}`  \n"
        f"**Posted**: {date_posted or 'not visible'}  \n"
        f"**Summary**: {summary}  \n"
        f"**Tags**: {tags_str}  \n"
        f"**URL**: {url}\n\n"
        f"> {chr(10).join('> ' + line for line in content.splitlines()) if content else '_no content extracted_'}\n\n"
    )

    if translation:
        md_entry += f"**Translation**: {translation}\n\n"

    md_entry += f"**Key links**:\n{key_links_str}\n\n---\n"

    with open(md_path, "a") as f:
        f.write(md_entry)

    print(f"Saved entry: {entry_id}")
    print(f"  Category : {category}")
    print(f"  Author   : {author}")
    print(f"  Source   : {platform}")
    print(f"  Summary  : {summary}")
    print(f"  Tags     : {', '.join(tags)}")


def search_entries(kb_dir: Path, query: str, category: str | None = None) -> None:
    """Search entries by keyword across all fields."""
    index_data = load_index(kb_dir)
    entries = index_data["entries"]

    query_lower = query.lower()
    query_hyphenated = query_lower.replace(" ", "-")
    results = []

    for entry in entries:
        if category and entry.get("category") != category:
            continue

        searchable = " ".join([
            entry.get("author", ""),
            entry.get("summary", ""),
            entry.get("content_preview", ""),
            entry.get("source_platform", ""),
            " ".join(entry.get("tags", [])),
            entry.get("url", ""),
        ]).lower()

        # Match both space-separated and hyphenated forms of the query
        if query_lower in searchable or query_hyphenated in searchable:
            results.append(entry)

    if not results:
        print(f"No results found for '{query}'" + (f" in category '{category}'" if category else ""))
        return

    print(f"Found {len(results)} result(s) for '{query}':\n")
    for i, entry in enumerate(results, 1):
        tags_str = ", ".join(entry.get("tags", []))
        print(f"{i:3}. [{entry['category']}] {entry['author']} ({entry['source_platform']}) — {entry['date_saved']}")
        print(f"       {entry['summary']}")
        if tags_str:
            print(f"       Tags: {tags_str}")
        print(f"       ID: {entry['id']}")
        print()


def list_entries(kb_dir: Path, category: str | None = None, limit: int = 20) -> None:
    """List entries, optionally filtered by category."""
    index_data = load_index(kb_dir)
    entries = index_data["entries"]

    if category:
        if category not in CATEGORIES:
            print(f"Unknown category '{category}'. Valid categories: {', '.join(CATEGORIES)}")
            return
        entries = [e for e in entries if e.get("category") == category]

    if not entries:
        label = f"category '{category}'" if category else "knowledge base"
        print(f"No entries in {label}.")
        return

    total = len(entries)
    entries = entries[:limit]
    label = f"category '{category}'" if category else "all categories"
    print(f"Showing {len(entries)} of {total} entries in {label}:\n")

    for i, entry in enumerate(entries, 1):
        print(f"{i:3}. [{entry['category']}] {entry['author']} · {entry['source_platform']} · {entry['date_saved']}")
        print(f"       {entry['summary']}")
        print()


def show_stats(kb_dir: Path) -> None:
    """Display knowledge base statistics."""
    index_data = load_index(kb_dir)
    entries = index_data["entries"]

    print(f"Knowledge Base Statistics")
    print(f"=========================")
    print(f"Total entries : {len(entries)}")
    print(f"Created       : {index_data.get('created', 'unknown')}")
    print()

    if not entries:
        return

    # Count by category
    counts: dict[str, int] = {}
    platforms: dict[str, int] = {}
    tags: dict[str, int] = {}

    for entry in entries:
        cat = entry.get("category", "misc")
        counts[cat] = counts.get(cat, 0) + 1

        plat = entry.get("source_platform", "unknown")
        platforms[plat] = platforms.get(plat, 0) + 1

        for tag in entry.get("tags", []):
            tags[tag] = tags.get(tag, 0) + 1

    print("By category:")
    for cat in CATEGORIES:
        count = counts.get(cat, 0)
        bar = "#" * count
        print(f"  {cat:<12} {count:>4}  {bar}")

    print("\nBy platform:")
    for plat, count in sorted(platforms.items(), key=lambda x: -x[1])[:8]:
        print(f"  {plat:<20} {count:>4}")

    print("\nTop tags:")
    for tag, count in sorted(tags.items(), key=lambda x: -x[1])[:15]:
        print(f"  {tag:<25} {count:>4}")


def export_markdown(kb_dir: Path, output_path: str | None = None) -> None:
    """Export all entries as a single consolidated markdown file."""
    index_data = load_index(kb_dir)
    entries = index_data["entries"]

    lines = [
        "# Knowledge Base Export\n",
        f"_Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')} — {len(entries)} entries_\n\n",
    ]

    # Group by category
    by_category: dict[str, list] = {cat: [] for cat in CATEGORIES}
    for entry in entries:
        cat = entry.get("category", "misc")
        by_category.setdefault(cat, []).append(entry)

    for cat in CATEGORIES:
        cat_entries = by_category.get(cat, [])
        if not cat_entries:
            continue

        lines.append(f"## {cat.replace('-', ' ').title()} ({len(cat_entries)} entries)\n\n")

        for entry in cat_entries:
            tags_str = " ".join(f"`{t}`" for t in entry.get("tags", []))
            lines.append(f"### {entry['author']} · {entry['source_platform']} · {entry['date_saved']}\n\n")
            lines.append(f"**Summary**: {entry['summary']}  \n")
            lines.append(f"**Tags**: {tags_str or 'none'}  \n")
            lines.append(f"**URL**: {entry.get('url', 'not visible')}\n\n")
            if entry.get("content_preview"):
                lines.append(f"> {entry['content_preview']}\n\n")
            lines.append("---\n\n")

    content = "".join(lines)

    if output_path:
        Path(output_path).write_text(content)
        print(f"Exported {len(entries)} entries to: {output_path}")
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Knowledge Base Manager for Screenshot Extractor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    subparsers.add_parser("init", help="Initialize the knowledge base")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new entry")
    add_parser.add_argument("--data", required=True, help="JSON string of the entry data")
    add_parser.add_argument("--force", action="store_true", help="Skip duplicate confirmation prompt")
    add_parser.add_argument("--kb-dir", help="Path to knowledge-base directory")

    # search
    search_parser = subparsers.add_parser("search", help="Search entries by keyword")
    search_parser.add_argument("--query", required=True, help="Search query")
    search_parser.add_argument("--category", choices=CATEGORIES, help="Filter by category")
    search_parser.add_argument("--kb-dir", help="Path to knowledge-base directory")

    # list
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("--category", choices=CATEGORIES, help="Filter by category")
    list_parser.add_argument("--limit", type=int, default=20, help="Max entries to show")
    list_parser.add_argument("--kb-dir", help="Path to knowledge-base directory")

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--kb-dir", help="Path to knowledge-base directory")

    # export
    export_parser = subparsers.add_parser("export", help="Export knowledge base")
    export_parser.add_argument("--format", choices=["md"], default="md")
    export_parser.add_argument("--output", help="Output file path (stdout if omitted)")
    export_parser.add_argument("--kb-dir", help="Path to knowledge-base directory")

    args = parser.parse_args()

    if args.command == "init":
        kb_dir = Path(args.kb_dir) if hasattr(args, "kb_dir") and args.kb_dir else get_kb_dir()
        init_kb(kb_dir)
        return

    kb_dir_arg = getattr(args, "kb_dir", None)
    kb_dir = Path(kb_dir_arg) if kb_dir_arg else get_kb_dir()

    if args.command == "add":
        try:
            entry = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON — {e}")
            sys.exit(1)
        add_entry(kb_dir, entry, force=getattr(args, "force", False))

    elif args.command == "search":
        search_entries(kb_dir, args.query, getattr(args, "category", None))

    elif args.command == "list":
        list_entries(kb_dir, getattr(args, "category", None), args.limit)

    elif args.command == "stats":
        show_stats(kb_dir)

    elif args.command == "export":
        export_markdown(kb_dir, getattr(args, "output", None))


if __name__ == "__main__":
    main()
