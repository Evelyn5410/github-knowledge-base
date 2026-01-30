#!/usr/bin/env python3
"""
GitHub Knowledge Base - Known Books Detection
Detects when users reference books already in Claude's training data
to avoid wasting tokens on re-reading content.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_config_dir() -> Path:
    """Get the configuration directory."""
    config_dir = Path.home() / ".config" / "github-kb"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def load_known_books() -> Dict:
    """Load the known books database."""
    script_dir = Path(__file__).parent
    books_file = script_dir / "known_books.json"

    if not books_file.exists():
        return {"books": {}, "curated_combinations": {}}

    with open(books_file, 'r') as f:
        return json.load(f)


def detect_book(query: str, books_db: Dict) -> Optional[Tuple[str, Dict]]:
    """
    Detect if a query matches a known book.
    Returns (book_id, book_data) or None.
    """
    query_lower = query.lower().strip()

    for book_id, book_data in books_db.get("books", {}).items():
        # Check title
        if query_lower in book_data["title"].lower():
            return (book_id, book_data)

        # Check aliases
        for alias in book_data.get("aliases", []):
            if query_lower in alias.lower() or alias.lower() in query_lower:
                return (book_id, book_data)

        # Check author
        if query_lower in book_data["author"].lower():
            return (book_id, book_data)

    return None


def print_book_info(book_id: str, book_data: Dict):
    """Print information about a known book."""
    print(f"\n📚 {book_data['title']}")
    print(f"   Author: {book_data['author']} ({book_data['year']})")
    print(f"   Topics: {', '.join(book_data['topics'])}")

    if book_data.get("in_claude_training"):
        print("\n✅ This book is already in Claude's training data!")
        print("   No need to waste tokens reading the PDF.")

    print("\n💡 Key Concepts:")
    for concept in book_data.get("key_concepts", [])[:5]:
        print(f"   • {concept}")

    if len(book_data.get("key_concepts", [])) > 5:
        print(f"   ... and {len(book_data['key_concepts']) - 5} more")


def print_prompts(book_data: Dict):
    """Print ready-to-use prompts for a book."""
    prompts = book_data.get("prompts", {})

    if not prompts:
        return

    print("\n🎯 Ready-to-use prompts:")
    print("   Copy and paste these to ask Claude about the book:\n")

    for prompt_type, prompt_text in prompts.items():
        print(f"   {prompt_type}:")
        print(f"   \"{prompt_text}\"")
        print()


def list_books(books_db: Dict):
    """List all known books."""
    books = books_db.get("books", {})

    if not books:
        print("No known books in database.")
        return

    print(f"\n📚 Known Books ({len(books)} total):\n")

    for book_id, book_data in books.items():
        in_training = "✅" if book_data.get("in_claude_training") else "❌"
        print(f"{in_training} {book_data['title']}")
        print(f"   {book_data['author']} ({book_data['year']})")
        print(f"   Topics: {', '.join(book_data['topics'][:3])}")
        print()


def list_combinations(books_db: Dict):
    """List curated book combinations."""
    combos = books_db.get("curated_combinations", {})

    if not combos:
        print("No curated combinations available.")
        return

    print(f"\n📦 Curated Combinations ({len(combos)} total):\n")

    for combo_id, combo_data in combos.items():
        print(f"🔖 {combo_data['name']}")
        print(f"   {combo_data['description']}")
        print(f"   Books: {', '.join(combo_data['books'])}")
        print(f"   Command: kb-books combo {combo_id}")
        print()


def show_combination(combo_id: str, books_db: Dict):
    """Show details of a specific combination."""
    combos = books_db.get("curated_combinations", {})
    combo_data = combos.get(combo_id)

    if not combo_data:
        print(f"❌ Combination '{combo_id}' not found.")
        print("\nAvailable combinations:")
        for cid in combos.keys():
            print(f"   • {cid}")
        return

    print(f"\n📦 {combo_data['name']}")
    print(f"   {combo_data['description']}\n")

    books = books_db.get("books", {})
    print("📚 Included Books:")
    for book_id in combo_data["books"]:
        book_data = books.get(book_id, {})
        if book_data:
            in_training = "✅" if book_data.get("in_claude_training") else "❌"
            print(f"   {in_training} {book_data.get('title', book_id)}")

    print("\n📖 Learning Path:")
    for step in combo_data.get("learning_path", []):
        print(f"   {step}")

    print("\n🎯 Ready-to-use prompts:")
    for prompt_type, prompt_text in combo_data.get("prompts", {}).items():
        print(f"\n   {prompt_type}:")
        print(f"   \"{prompt_text}\"")


def check_pdf_title(pdf_title: str, books_db: Dict) -> Optional[Tuple[str, Dict]]:
    """
    Check if a PDF title matches a known book.
    Used when adding PDFs to warn about token waste.
    """
    return detect_book(pdf_title, books_db)


def main():
    if len(sys.argv) < 2:
        print("GitHub Knowledge Base - Known Books")
        print("\nUsage:")
        print("  kb-books list              List all known books")
        print("  kb-books combos            List curated combinations")
        print("  kb-books combo <id>        Show combination details")
        print("  kb-books search <query>    Search for a book")
        print("  kb-books check <title>     Check if a book is known")
        print("\nExamples:")
        print("  kb-books search 'clean code'")
        print("  kb-books combo clean-code-fundamentals")
        print("  kb-books check 'Refactoring by Martin Fowler'")
        sys.exit(0)

    command = sys.argv[1]
    books_db = load_known_books()

    if command == "list":
        list_books(books_db)

    elif command == "combos":
        list_combinations(books_db)

    elif command == "combo":
        if len(sys.argv) < 3:
            print("❌ Error: Please specify a combination ID")
            print("\nExample: kb-books combo clean-code-fundamentals")
            sys.exit(1)

        combo_id = sys.argv[2]
        show_combination(combo_id, books_db)

    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a search query")
            print("\nExample: kb-books search 'clean code'")
            sys.exit(1)

        query = " ".join(sys.argv[2:])
        result = detect_book(query, books_db)

        if result:
            book_id, book_data = result
            print_book_info(book_id, book_data)
            print_prompts(book_data)
        else:
            print(f"❌ No known book found matching: {query}")
            print("\nTry: kb-books list")

    elif command == "check":
        if len(sys.argv) < 3:
            print("❌ Error: Please provide a title to check")
            print("\nExample: kb-books check 'Clean Code'")
            sys.exit(1)

        title = " ".join(sys.argv[2:])
        result = check_pdf_title(title, books_db)

        if result:
            book_id, book_data = result
            print("\n⚠️  TOKEN ALERT!")
            print_book_info(book_id, book_data)
            print_prompts(book_data)
            print("\n💰 Token Savings: Avoid reading this PDF - use the prompts above instead!")
        else:
            print(f"✅ '{title}' is not a known book.")
            print("   You can safely add this PDF to your knowledge base.")

    else:
        print(f"❌ Unknown command: {command}")
        print("\nRun 'kb-books' without arguments for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
