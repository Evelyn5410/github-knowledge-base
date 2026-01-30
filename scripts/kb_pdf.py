#!/usr/bin/env python3
"""
GitHub Knowledge Base PDF Manager
Manage PDFs from repositories and local files with smart token management.
"""

import json
import os
import sys
import argparse
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import hashlib

KB_DIR = Path.home() / ".config" / "github-kb"
NOTES_DIR = KB_DIR / "notes"
PDF_INDEX_FILE = NOTES_DIR / "pdf_index.json"

# Token estimation: ~4 characters per token, ~500 words per page
CHARS_PER_TOKEN = 4
TOKENS_PER_PAGE = 500  # Conservative estimate
LARGE_PDF_THRESHOLD = 10000  # Tokens


def init_pdf_system():
    """Initialize PDF management system."""
    NOTES_DIR.mkdir(parents=True, exist_ok=True)

    if not PDF_INDEX_FILE.exists():
        default_index = {
            "version": "1.0",
            "pdfs": {},
            "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        save_pdf_index(default_index)


def load_pdf_index() -> Dict:
    """Load PDF index."""
    if not PDF_INDEX_FILE.exists():
        init_pdf_system()

    with open(PDF_INDEX_FILE, 'r') as f:
        return json.load(f)


def save_pdf_index(index: Dict):
    """Save PDF index."""
    index["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    with open(PDF_INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)


def get_file_hash(file_path: Path) -> str:
    """Get SHA256 hash of file."""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256.update(chunk)
    return sha256.hexdigest()[:16]


def estimate_pdf_tokens(file_path: Path) -> Dict:
    """Estimate token count for a PDF.

    Uses file size heuristics since we can't parse PDF without external libs.
    More accurate estimation would require PyPDF2 or similar.
    """
    file_size = file_path.stat().st_size

    # Rough estimation based on file size
    # PDF files are compressed, so this is conservative
    # Typical: 1KB ≈ 100-200 tokens for text-heavy PDFs
    estimated_tokens = int(file_size / 1024 * 150)

    # Estimate pages (very rough: ~50KB per page for typical PDF)
    estimated_pages = max(1, int(file_size / (50 * 1024)))

    return {
        "file_size_kb": round(file_size / 1024, 2),
        "estimated_pages": estimated_pages,
        "estimated_tokens": estimated_tokens,
        "confidence": "low (based on file size)",
        "note": "Actual token count may vary. Install PyPDF2 for accurate page counts."
    }


def load_known_books() -> Dict:
    """Load the known books database."""
    script_dir = Path(__file__).parent
    books_file = script_dir / "known_books.json"

    if not books_file.exists():
        return {"books": {}, "curated_combinations": {}}

    with open(books_file, 'r') as f:
        return json.load(f)


def check_known_book(title: str) -> Optional[Tuple[str, Dict]]:
    """Check if a title matches a known book in Claude's training data."""
    books_db = load_known_books()
    title_lower = title.lower().strip()

    for book_id, book_data in books_db.get("books", {}).items():
        # Check title
        if title_lower in book_data["title"].lower() or book_data["title"].lower() in title_lower:
            return (book_id, book_data)

        # Check aliases
        for alias in book_data.get("aliases", []):
            if title_lower in alias.lower() or alias.lower() in title_lower:
                return (book_id, book_data)

        # Check author
        if title_lower in book_data["author"].lower():
            return (book_id, book_data)

    return None


def add_pdf(pdf_path: str, title: Optional[str] = None, tags: List[str] = None,
            source: Optional[str] = None):
    """Add a PDF to the knowledge base."""
    init_pdf_system()

    source_path = Path(pdf_path).expanduser()

    if not source_path.exists():
        print(f"Error: PDF not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    if not source_path.suffix.lower() == '.pdf':
        print(f"Error: File is not a PDF: {source_path}", file=sys.stderr)
        sys.exit(1)

    # Generate destination filename
    if title:
        # Sanitize title for filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '-')
        dest_filename = f"{safe_title}.pdf"
    else:
        dest_filename = source_path.name

    dest_path = NOTES_DIR / dest_filename

    # Check if already exists
    index = load_pdf_index()
    if dest_filename in index["pdfs"]:
        print(f"PDF '{dest_filename}' already exists in knowledge base.")
        print(f"Use --force to overwrite or choose a different title.")
        return

    # Copy PDF to notes directory
    print(f"Adding PDF to knowledge base...")
    shutil.copy2(source_path, dest_path)

    # Calculate hash
    file_hash = get_file_hash(dest_path)

    # Estimate tokens
    token_info = estimate_pdf_tokens(dest_path)

    # Check if this is a known book in Claude's training data
    pdf_title = title or source_path.stem
    known_book_match = check_known_book(pdf_title)

    if known_book_match:
        book_id, book_data = known_book_match
        print(f"\n⚠️  TOKEN ALERT!")
        print(f"\n📚 {book_data['title']}")
        print(f"   Author: {book_data['author']} ({book_data['year']})")

        if book_data.get("in_claude_training"):
            print(f"\n✅ This book is already in Claude's training data!")
            print(f"   Reading the PDF will waste ~{token_info['estimated_tokens']:,} tokens.")
            print(f"\n💡 Instead, use these ready-to-use prompts:\n")

            for prompt_type, prompt_text in book_data.get("prompts", {}).items():
                print(f"   {prompt_type}:")
                print(f"   \"{prompt_text}\"\n")

            print(f"💰 Token Savings: Skip the PDF and use the prompts above!")
            print(f"\n🔍 For more info: kb-books search \"{book_data['title']}\"")
            print(f"📦 See combinations: kb-books combos")

            # Ask user if they still want to proceed
            print(f"\n⚠️  Do you still want to add this PDF?")
            response = input("   Type 'yes' to proceed or anything else to cancel: ").strip().lower()

            if response != 'yes':
                print(f"\n✓ Cancelled. Use the prompts above to reference {book_data['title']}.")
                # Remove the copied PDF
                if dest_path.exists():
                    dest_path.unlink()
                return

            print(f"\n⚠️  Proceeding with PDF addition (not recommended)...")

    # Create index entry
    pdf_entry = {
        "filename": dest_filename,
        "title": title or source_path.stem,
        "original_path": str(source_path),
        "local_path": str(dest_path),
        "added_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "tags": tags or [],
        "source": source or "local",
        "file_hash": file_hash,
        "size_kb": token_info["file_size_kb"],
        "estimated_pages": token_info["estimated_pages"],
        "estimated_tokens": token_info["estimated_tokens"],
        "summary": None,
        "has_summary": False
    }

    # Add to index
    index["pdfs"][dest_filename] = pdf_entry
    save_pdf_index(index)

    # Display info
    print(f"\n✓ Added PDF to knowledge base")
    print(f"  Title: {pdf_entry['title']}")
    print(f"  Filename: {dest_filename}")
    print(f"  Size: {token_info['file_size_kb']:.2f} KB")
    print(f"  Estimated pages: ~{token_info['estimated_pages']}")
    print(f"  Estimated tokens: ~{token_info['estimated_tokens']:,}")

    if token_info['estimated_tokens'] > LARGE_PDF_THRESHOLD:
        print(f"\n⚠️  Large PDF detected!")
        print(f"  Reading this entire PDF will consume ~{token_info['estimated_tokens']:,} tokens")
        print(f"  Consider creating a summary first:")
        print(f"    kb-pdf summarize {dest_filename}")

    if tags:
        print(f"  Tags: {', '.join(tags)}")

    print(f"\n💡 Next Steps:")
    print(f"  → View info: kb-pdf info {dest_filename}")
    print(f"  → Create summary: kb-pdf summarize {dest_filename}")
    print(f"  → List all PDFs: kb-pdf list")


def remove_pdf(filename: str):
    """Remove a PDF from the knowledge base."""
    init_pdf_system()
    index = load_pdf_index()

    # Check if PDF exists in index
    if filename not in index["pdfs"]:
        print(f"❌ PDF '{filename}' not found in knowledge base.")
        print("\n💡 List all PDFs:")
        print("  kb-pdf list")
        sys.exit(1)

    pdf_entry = index["pdfs"][filename]
    pdf_path = Path(pdf_entry["local_path"])
    summary_path = NOTES_DIR / f"{pdf_path.stem}.summary.md"

    # Store original path for display
    original_path = pdf_entry.get("original_path", "N/A")
    title = pdf_entry.get("title", filename)

    # Remove PDF file from notes directory
    if pdf_path.exists():
        pdf_path.unlink()

    # Remove summary file if it exists
    if summary_path.exists():
        summary_path.unlink()

    # Remove from index
    del index["pdfs"][filename]
    save_pdf_index(index)

    # Display confirmation
    print(f"\n✓ PDF removed from knowledge base")
    print(f"  Title: {title}")
    print(f"  Filename: {filename}")

    if summary_path.exists() or (NOTES_DIR / f"{pdf_path.stem}.summary.md").exists():
        print(f"  Summary: Also removed")

    print(f"\n📝 Note: Original file not affected")
    if original_path != "N/A" and original_path != str(pdf_path):
        print(f"  Original: {original_path}")

    print(f"\n💡 Remaining PDFs:")
    remaining_count = len(index["pdfs"])
    if remaining_count > 0:
        print(f"  → View list: kb-pdf list")
    else:
        print(f"  → Knowledge base is now empty")


def list_pdfs(tag: Optional[str] = None):
    """List all PDFs in the knowledge base."""
    init_pdf_system()
    index = load_pdf_index()

    pdfs = index["pdfs"]

    if not pdfs:
        print("No PDFs in knowledge base.")
        print("\n💡 Add a PDF:")
        print("  kb-pdf add /path/to/document.pdf")
        print("  kb-pdf add /path/to/document.pdf --title \"My Document\" --tags research ml")
        return

    # Filter by tag
    if tag:
        pdfs = {k: v for k, v in pdfs.items() if tag in v.get("tags", [])}
        if not pdfs:
            print(f"No PDFs found with tag '{tag}'")
            return

    print(f"\n📚 PDF Knowledge Base ({len(pdfs)} PDFs)")
    print("=" * 80)

    # Sort by added date
    sorted_pdfs = sorted(pdfs.items(), key=lambda x: x[1]["added_at"], reverse=True)

    total_tokens = 0

    for filename, pdf_data in sorted_pdfs:
        icon = "📄"
        if pdf_data.get("has_summary"):
            icon = "📄✓"

        print(f"\n{icon} {pdf_data['title']}")
        print(f"   Filename: {filename}")
        print(f"   Size: {pdf_data['size_kb']:.2f} KB | ~{pdf_data['estimated_pages']} pages | ~{pdf_data['estimated_tokens']:,} tokens")

        if pdf_data.get("tags"):
            print(f"   Tags: {', '.join(pdf_data['tags'])}")

        if pdf_data.get("source") and pdf_data["source"] != "local":
            print(f"   Source: {pdf_data['source']}")

        if pdf_data.get("has_summary"):
            print(f"   ✓ Summary available (token-efficient)")

        total_tokens += pdf_data['estimated_tokens']

    print("\n" + "=" * 80)
    print(f"Total: {len(pdfs)} PDFs | ~{total_tokens:,} tokens if all read")

    # Token warning
    if total_tokens > 50000:
        print(f"\n⚠️  Reading all PDFs would consume ~{total_tokens:,} tokens!")
        print(f"   Create summaries to reduce token usage:")
        print(f"     kb-pdf summarize <filename>")


def show_pdf_info(filename: str):
    """Show detailed info about a PDF."""
    init_pdf_system()
    index = load_pdf_index()

    if filename not in index["pdfs"]:
        print(f"Error: PDF '{filename}' not found in knowledge base.", file=sys.stderr)
        print(f"\nAvailable PDFs:", file=sys.stderr)
        for pdf_name in list(index["pdfs"].keys())[:5]:
            print(f"  - {pdf_name}", file=sys.stderr)
        sys.exit(1)

    pdf_data = index["pdfs"][filename]

    print(f"\n{'='*80}")
    print(f"PDF: {pdf_data['title']}")
    print(f"{'='*80}")
    print(f"Filename: {filename}")
    print(f"Added: {pdf_data['added_at']}")
    print(f"Source: {pdf_data.get('source', 'local')}")
    print(f"Size: {pdf_data['size_kb']:.2f} KB")
    print(f"Estimated pages: ~{pdf_data['estimated_pages']}")
    print(f"Estimated tokens: ~{pdf_data['estimated_tokens']:,}")

    if pdf_data.get("tags"):
        print(f"Tags: {', '.join(pdf_data['tags'])}")

    print(f"\nLocal path: {pdf_data['local_path']}")

    if pdf_data.get("has_summary"):
        print(f"\n✓ Summary available")
        summary_path = Path(pdf_data['local_path']).with_suffix('.summary.md')
        print(f"  Summary path: {summary_path}")

    if pdf_data.get("summary"):
        print(f"\nSummary:")
        print(f"  {pdf_data['summary']}")

    print(f"\n{'='*80}")

    # Token guidance
    tokens = pdf_data['estimated_tokens']
    print(f"\n💡 Token Usage Guidance:")

    if tokens < 5000:
        print(f"  → Small PDF (~{tokens:,} tokens) - safe to read directly")
        print(f"  → Read in Claude: Provide path to Claude")
    elif tokens < 15000:
        print(f"  → Medium PDF (~{tokens:,} tokens) - consider summary")
        print(f"  → Create summary: kb-pdf summarize {filename}")
    else:
        print(f"  ⚠️  Large PDF (~{tokens:,} tokens) - summary recommended")
        print(f"  → Create summary: kb-pdf summarize {filename}")
        print(f"  → Summary will save ~{int(tokens * 0.8):,} tokens")

    print(f"\n💡 Usage:")
    print(f"  → In Claude: \"Read and summarize {pdf_data['local_path']}\"")
    print(f"  → Create summary: kb-pdf summarize {filename}")
    print(f"  → Tag: kb-pdf tag {filename} <tag1> <tag2>")


def tag_pdf(filename: str, tags: List[str]):
    """Add tags to a PDF."""
    init_pdf_system()
    index = load_pdf_index()

    if filename not in index["pdfs"]:
        print(f"Error: PDF '{filename}' not found.", file=sys.stderr)
        sys.exit(1)

    current_tags = set(index["pdfs"][filename].get("tags", []))
    current_tags.update(tags)
    index["pdfs"][filename]["tags"] = sorted(list(current_tags))

    save_pdf_index(index)

    print(f"✓ Tagged '{filename}' with: {', '.join(tags)}")
    print(f"  All tags: {', '.join(index['pdfs'][filename]['tags'])}")


def search_pdfs(query: str):
    """Search PDFs by title, filename, or tags."""
    init_pdf_system()
    index = load_pdf_index()

    query_lower = query.lower()
    matches = []

    for filename, pdf_data in index["pdfs"].items():
        if (query_lower in filename.lower() or
            query_lower in pdf_data['title'].lower() or
            any(query_lower in tag.lower() for tag in pdf_data.get('tags', []))):
            matches.append((filename, pdf_data))

    if not matches:
        print(f"No PDFs found matching '{query}'")
        return

    print(f"\n🔍 Found {len(matches)} PDF(s) matching '{query}'")
    print("=" * 80)

    for filename, pdf_data in matches:
        print(f"\n📄 {pdf_data['title']}")
        print(f"   {filename} | ~{pdf_data['estimated_tokens']:,} tokens")
        if pdf_data.get('tags'):
            print(f"   Tags: {', '.join(pdf_data['tags'])}")
        print(f"   Path: {pdf_data['local_path']}")


def scan_repo_pdfs(repo_key: str):
    """Scan a cloned repository for PDFs."""
    from kb import load_index as load_kb_index

    kb_index = load_kb_index()

    if repo_key not in kb_index["repos"]:
        print(f"Error: Repository '{repo_key}' not found.", file=sys.stderr)
        sys.exit(1)

    repo_data = kb_index["repos"][repo_key]
    repo_path = Path(repo_data["local_path"])

    if not repo_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone first: kb-explore clone {repo_key}")
        sys.exit(1)

    # Find all PDFs
    pdfs = list(repo_path.rglob("*.pdf"))

    if not pdfs:
        print(f"No PDFs found in {repo_key}")
        return

    print(f"\n📚 Found {len(pdfs)} PDF(s) in {repo_key}")
    print("=" * 80)

    total_tokens = 0

    for pdf_path in pdfs:
        rel_path = pdf_path.relative_to(repo_path)
        token_info = estimate_pdf_tokens(pdf_path)
        total_tokens += token_info['estimated_tokens']

        print(f"\n📄 {rel_path}")
        print(f"   Size: {token_info['file_size_kb']:.2f} KB | ~{token_info['estimated_pages']} pages | ~{token_info['estimated_tokens']:,} tokens")
        print(f"   Path: {pdf_path}")

    print("\n" + "=" * 80)
    print(f"Total: {len(pdfs)} PDFs | ~{total_tokens:,} tokens if all read")

    print(f"\n💡 To add PDFs from this repo:")
    for pdf_path in pdfs[:3]:
        rel_path = pdf_path.relative_to(repo_path)
        print(f"  kb-pdf add \"{pdf_path}\" --source {repo_key}")


def create_summary_placeholder(filename: str):
    """Create a structured summary template with sections and token optimization."""
    init_pdf_system()
    index = load_pdf_index()

    if filename not in index["pdfs"]:
        print(f"Error: PDF '{filename}' not found.", file=sys.stderr)
        sys.exit(1)

    pdf_data = index["pdfs"][filename]
    pdf_path = Path(pdf_data['local_path'])
    summary_path = pdf_path.with_suffix('.summary.md')

    # Estimate sections based on page count
    total_pages = pdf_data['estimated_pages']
    total_tokens = pdf_data['estimated_tokens']
    target_summary_tokens = min(2500, int(total_tokens * 0.15))  # 15% of original or 2500, whichever is smaller

    # Create structured summary template
    summary_template = f"""# Structured Summary: {pdf_data['title']}

**Source PDF**: {filename}
**Location**: {pdf_path}
**Total Pages**: {total_pages} | **Full PDF Tokens**: ~{total_tokens:,}
**This Summary**: ~{target_summary_tokens:,} tokens | **Token Savings**: ~{total_tokens - target_summary_tokens:,} ({int((total_tokens - target_summary_tokens) / total_tokens * 100)}%)

---

## 📋 Document Overview

**Main Topic**: [1-2 sentence overview]

**Document Type**: [Research paper / Technical guide / Tutorial / Reference / Other]

**Target Audience**: [Who should read this?]

**Key Takeaway**: [Single most important point]

---

## 🗂️ Document Structure

> **Instructions for Claude**: After reading the PDF, fill in this structure.
> Create 3-6 logical sections based on the document's actual organization.
> Estimate tokens per section (pages × 400 tokens/page)

### Section 1: [Title] (Pages X-Y, ~Z tokens)

**Summary**: [2-3 sentences summarizing this section]

**Key Concepts**:
- Concept 1: Brief explanation
- Concept 2: Brief explanation
- Concept 3: Brief explanation

**Important Details**: [Any formulas, code, or specific data worth noting]

**When to Read Full Section**: [e.g., "Need implementation details" / "Understanding fundamentals"]

---

### Section 2: [Title] (Pages X-Y, ~Z tokens)

**Summary**: [2-3 sentences summarizing this section]

**Key Concepts**:
- Concept 1: Brief explanation
- Concept 2: Brief explanation

**Important Details**: [Any formulas, code, or specific data worth noting]

**When to Read Full Section**: [e.g., "Working examples needed"]

---

### Section 3: [Title] (Pages X-Y, ~Z tokens)

**Summary**: [2-3 sentences summarizing this section]

**Key Concepts**:
- Concept 1: Brief explanation
- Concept 2: Brief explanation

**Important Details**: [Any formulas, code, or specific data worth noting]

**When to Read Full Section**: [e.g., "Deep dive into architecture"]

---

[Add more sections as needed - typically 3-6 sections total]

---

## 🔍 Topic Index

> **Instructions**: List key topics and where to find them

| Topic | Sections | Pages | Why Important |
|-------|----------|-------|---------------|
| [Topic 1] | 1, 3 | 5-8, 20-25 | [Brief explanation] |
| [Topic 2] | 2 | 10-15 | [Brief explanation] |
| [Topic 3] | 3, 4 | 18-30 | [Brief explanation] |

**Search Keywords**: [List 10-15 important keywords from the document]

---

## 💡 Quick Reference Guide

### For Different Use Cases

**Just need overview**: Read "Document Overview" above (~200 tokens)

**Understanding basics**: Read Section [X] (~Z tokens)

**Implementation details**: Read Sections [X, Y] (~Z tokens)

**Complete understanding**: Read full summary (~{target_summary_tokens:,} tokens)

**Deep dive**: Read full PDF ({total_tokens:,} tokens)

### Most Important Sections

1. **[Section name]** - [Why it's important]
2. **[Section name]** - [Why it's important]
3. **[Section name]** - [Why it's important]

---

## 🎯 Recommended Reading Strategy

**First Time Learning**:
1. Read Document Overview (above)
2. Read Section summaries for all sections
3. Deep dive into specific sections as needed
**Token Cost**: ~{target_summary_tokens:,} tokens

**Quick Reference**:
1. Check Topic Index for specific topic
2. Read only relevant section summaries
**Token Cost**: ~500-1,000 tokens

**Detailed Study**:
1. Read this full summary first
2. Then read full PDF with context
**Token Cost**: ~{target_summary_tokens + total_tokens:,} tokens (but more effective)

---

## 📊 Token Efficiency Metrics

| Reading Approach | Token Cost | When to Use |
|------------------|------------|-------------|
| **Full PDF** | {total_tokens:,} | Deep research, first-time comprehensive study |
| **This Summary** | ~{target_summary_tokens:,} | General understanding, reference |
| **Single Section Summary** | ~300-800 | Quick lookup, specific topic |
| **Overview Only** | ~200 | Deciding relevance |

**Break-Even Point**: After reading this summary 2-3 times instead of full PDF, you've saved more tokens than the initial investment.

**Long-term Savings**: If you reference this document 10 times:
- Without summary: {total_tokens * 10:,} tokens
- With summary: {total_tokens + (target_summary_tokens * 9):,} tokens
- **Savings**: {(total_tokens * 10) - (total_tokens + (target_summary_tokens * 9)):,} tokens ({int(((total_tokens * 10) - (total_tokens + (target_summary_tokens * 9))) / (total_tokens * 10) * 100)}%)

---

## 🚀 Instructions for Claude

To complete this summary:

1. **Read the PDF**: Open and read {pdf_path}

2. **Identify Structure**: Note the actual sections/chapters in the PDF

3. **Fill in Sections**: For each major section:
   - Write 2-3 sentence summary
   - Extract 3-5 key concepts
   - Note page ranges and estimate tokens (pages × 400)
   - Indicate when reading the full section is necessary

4. **Create Topic Index**: List 8-12 important topics with locations

5. **Complete Overview**: Write the main topic, document type, and key takeaway

6. **Verify Token Estimates**: Ensure section token estimates add up to total

7. **Save This File**: Keep this summary for future reference

**Estimated Time**: 5-10 minutes to create a high-quality summary that saves hours of token costs.

---

*Summary Status*: 🔴 **Not yet completed** - Awaiting Claude to read PDF and fill in details

*Last Updated*: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
"""

    with open(summary_path, 'w') as f:
        f.write(summary_template)

    # Update index
    index["pdfs"][filename]["has_summary"] = True
    index["pdfs"][filename]["summary_path"] = str(summary_path)
    index["pdfs"][filename]["summary_tokens"] = target_summary_tokens
    save_pdf_index(index)

    print(f"✓ Created structured summary template: {summary_path}")
    print(f"\n📋 Summary Structure:")
    print(f"  → Document overview (~200 tokens)")
    print(f"  → Section-by-section analysis (~1,500-2,000 tokens)")
    print(f"  → Topic index for quick reference")
    print(f"  → Reading strategies for different needs")
    print(f"\n💡 Next Step:")
    print(f"  Ask Claude:")
    print(f'  "Read the PDF at {pdf_path}')
    print(f'   and complete the structured summary template at {summary_path}"')
    print(f"\n📊 Token Economics:")
    print(f"  One-time cost: Read PDF once (~{total_tokens:,} tokens)")
    print(f"  Future reads: Use summary (~{target_summary_tokens:,} tokens)")
    print(f"  Per-use savings: ~{total_tokens - target_summary_tokens:,} tokens ({int((total_tokens - target_summary_tokens) / total_tokens * 100)}%)")
    print(f"  Break-even: After 2nd use")
    print(f"  10 uses: Save ~{(total_tokens * 10) - (total_tokens + (target_summary_tokens * 9)):,} tokens total")
    print(f"\n🎯 Benefits:")
    print(f"  ✓ Section-level granularity (read only what you need)")
    print(f"  ✓ Topic index (find information fast)")
    print(f"  ✓ Multiple reading strategies (overview vs deep dive)")
    print(f"  ✓ Token transparency (know cost before reading)")
    print(f"  ✓ Long-term efficiency (massive savings over time)")


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Knowledge Base PDF Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add PDF
    add_parser = subparsers.add_parser("add", help="Add a PDF to knowledge base")
    add_parser.add_argument("pdf_path", help="Path to PDF file")
    add_parser.add_argument("--title", help="PDF title (default: filename)")
    add_parser.add_argument("--tags", nargs="+", help="Tags for the PDF")
    add_parser.add_argument("--source", help="Source identifier (e.g., repo name)")

    # Remove PDF
    remove_parser = subparsers.add_parser("remove", help="Remove a PDF from knowledge base")
    remove_parser.add_argument("filename", help="PDF filename to remove")

    # List PDFs
    list_parser = subparsers.add_parser("list", help="List all PDFs")
    list_parser.add_argument("--tag", help="Filter by tag")

    # PDF info
    info_parser = subparsers.add_parser("info", help="Show PDF details")
    info_parser.add_argument("filename", help="PDF filename")

    # Tag PDF
    tag_parser = subparsers.add_parser("tag", help="Add tags to a PDF")
    tag_parser.add_argument("filename", help="PDF filename")
    tag_parser.add_argument("tags", nargs="+", help="Tags to add")

    # Search PDFs
    search_parser = subparsers.add_parser("search", help="Search PDFs")
    search_parser.add_argument("query", help="Search query")

    # Scan repo for PDFs
    scan_parser = subparsers.add_parser("scan-repo", help="Find PDFs in a cloned repository")
    scan_parser.add_argument("repo", help="Repository identifier (owner/repo)")

    # Create summary
    summary_parser = subparsers.add_parser("summarize", help="Create summary template for PDF")
    summary_parser.add_argument("filename", help="PDF filename")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "add":
        add_pdf(args.pdf_path, title=args.title, tags=args.tags, source=args.source)
    elif args.command == "remove":
        remove_pdf(args.filename)
    elif args.command == "list":
        list_pdfs(tag=args.tag)
    elif args.command == "info":
        show_pdf_info(args.filename)
    elif args.command == "tag":
        tag_pdf(args.filename, args.tags)
    elif args.command == "search":
        search_pdfs(args.query)
    elif args.command == "scan-repo":
        scan_repo_pdfs(args.repo)
    elif args.command == "summarize":
        create_summary_placeholder(args.filename)


if __name__ == "__main__":
    main()
