#!/usr/bin/env python3
"""
GitHub Knowledge Base Explorer
Clone, analyze, and explore repositories in your knowledge base.
"""

import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone

KB_DIR = Path.home() / ".config" / "github-kb"
INDEX_FILE = KB_DIR / "index.json"
REPOS_DIR = KB_DIR / "repos"


def load_index() -> Dict:
    """Load the knowledge base index."""
    if not INDEX_FILE.exists():
        print("Knowledge base not initialized.", file=sys.stderr)
        print("Add a repository first: python kb.py add <owner/repo>")
        sys.exit(1)

    with open(INDEX_FILE, 'r') as f:
        return json.load(f)


def save_index(index: Dict):
    """Save the knowledge base index."""
    index["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)


def clone_repo(repo_identifier: str, depth: Optional[int] = None):
    """Clone a repository from the knowledge base."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        print(f"Add it first: python kb.py add {repo_key}")
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    # Check if already cloned
    if local_path.exists() and (local_path / ".git").exists():
        print(f"Repository '{repo_key}' already cloned at: {local_path}")
        print(f"To update, use: python kb_explore.py sync {repo_key}")
        return

    # Clone the repository
    print(f"Cloning {repo_key}...")
    print(f"Target: {local_path}")

    local_path.parent.mkdir(parents=True, exist_ok=True)

    clone_cmd = ["git", "clone"]

    if depth:
        clone_cmd.extend(["--depth", str(depth)])

    clone_cmd.extend([repo_data["url"], str(local_path)])

    try:
        result = subprocess.run(clone_cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            print(f"Error cloning repository:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

        print(f"✓ Successfully cloned {repo_key}")

        # Update index
        index["repos"][repo_key]["last_synced"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        save_index(index)

        # Automatically analyze after cloning
        print(f"\nAnalyzing repository structure...")
        analyze_repo(repo_key)

    except subprocess.TimeoutExpired:
        print(f"Error: Clone operation timed out.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def sync_repo(repo_identifier: str):
    """Sync (pull) a cloned repository."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"Syncing {repo_key}...")

    try:
        result = subprocess.run(
            ["git", "-C", str(local_path), "pull"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            print(f"Error syncing repository:", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(1)

        print(result.stdout)
        print(f"✓ Successfully synced {repo_key}")

        # Update index
        index["repos"][repo_key]["last_synced"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        save_index(index)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_repo(repo_identifier: str):
    """Analyze repository structure and identify key files."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"Analyzing {repo_key}...")
    print("=" * 80)

    # Identify key files
    key_files = []

    # Common entry points and important files
    important_patterns = [
        "package.json", "setup.py", "Cargo.toml", "go.mod", "pom.xml", "build.gradle",
        "Makefile", "CMakeLists.txt", "Dockerfile", "docker-compose.yml",
        "index.js", "index.ts", "main.py", "main.go", "main.rs", "main.c", "main.cpp",
        "app.py", "server.js", "server.ts", "index.html",
        "README.md", "CONTRIBUTING.md", "LICENSE"
    ]

    for pattern in important_patterns:
        matches = list(local_path.rglob(pattern))
        for match in matches:
            rel_path = match.relative_to(local_path)
            key_files.append(str(rel_path))

    # Count files by extension
    file_counts = {}
    for file_path in local_path.rglob("*"):
        if file_path.is_file() and not any(part.startswith(".") for part in file_path.parts):
            ext = file_path.suffix or "no-extension"
            file_counts[ext] = file_counts.get(ext, 0) + 1

    # Directory structure (top level)
    print("\nTop-level directories:")
    for item in sorted(local_path.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            # Count files in directory
            try:
                file_count = sum(1 for _ in item.rglob("*") if _.is_file())
                print(f"  📁 {item.name}/ ({file_count} files)")
            except:
                print(f"  📁 {item.name}/")

    print("\nKey files found:")
    for kf in sorted(key_files)[:20]:  # Limit to 20
        print(f"  📄 {kf}")

    if len(key_files) > 20:
        print(f"  ... and {len(key_files) - 20} more")

    print("\nFile type distribution:")
    for ext, count in sorted(file_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ext}: {count}")

    # Update index with key files
    index["repos"][repo_key]["key_files"] = sorted(key_files)[:50]
    save_index(index)

    print("\n" + "=" * 80)
    print(f"✓ Analysis complete. Key files saved to index.")


def show_tree(repo_identifier: str, depth: int = 2):
    """Show repository directory tree."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"Repository tree: {repo_key}")
    print("=" * 80)

    # Try to use 'tree' command if available
    try:
        result = subprocess.run(
            ["tree", "-L", str(depth), "-I", "node_modules|.git|__pycache__|*.pyc", str(local_path)],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            print(result.stdout)
            return

    except FileNotFoundError:
        pass

    # Fallback: simple tree implementation
    def print_tree(directory: Path, prefix: str = "", current_depth: int = 0):
        if current_depth >= depth:
            return

        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
        except PermissionError:
            return

        for i, item in enumerate(items):
            if item.name.startswith(".") or item.name in ["node_modules", "__pycache__"]:
                continue

            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            print(f"{prefix}{current_prefix}{item.name}")

            if item.is_dir():
                extension = "    " if is_last else "│   "
                print_tree(item, prefix + extension, current_depth + 1)

    print(local_path.name)
    print_tree(local_path)


def show_readme(repo_identifier: str):
    """Display repository README."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    # Find README
    readme_files = list(local_path.glob("README*"))

    if not readme_files:
        print(f"No README found in {repo_key}")
        return

    readme_path = readme_files[0]

    print(f"README: {repo_key}")
    print("=" * 80)

    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        # Limit output to first 100 lines
        lines = content.split('\n')[:100]
        print('\n'.join(lines))

        if len(content.split('\n')) > 100:
            print("\n... (truncated)")

    print("\n" + "=" * 80)


def find_docs(repo_identifier: str):
    """Find and list documentation files."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"Documentation files in {repo_key}:")
    print("=" * 80)

    # Find docs directories and markdown files
    doc_patterns = ["docs/", "doc/", "documentation/", "*.md"]

    found_docs = []

    # Find doc directories
    for pattern in ["docs", "doc", "documentation"]:
        doc_dirs = list(local_path.rglob(pattern))
        for doc_dir in doc_dirs:
            if doc_dir.is_dir() and not any(part.startswith(".") for part in doc_dir.parts):
                rel_path = doc_dir.relative_to(local_path)
                found_docs.append(("dir", str(rel_path)))

    # Find markdown files
    for md_file in local_path.rglob("*.md"):
        if not any(part.startswith(".") for part in md_file.parts):
            rel_path = md_file.relative_to(local_path)
            found_docs.append(("file", str(rel_path)))

    if not found_docs:
        print("No documentation found.")
        return

    # Group by type
    dirs = [d for t, d in found_docs if t == "dir"]
    files = [f for t, f in found_docs if t == "file"]

    if dirs:
        print("\nDocumentation directories:")
        for d in sorted(dirs):
            print(f"  📁 {d}")

    if files:
        print("\nMarkdown files:")
        for f in sorted(files)[:30]:  # Limit to 30
            print(f"  📄 {f}")

        if len(files) > 30:
            print(f"  ... and {len(files) - 30} more")

    print("\n" + "=" * 80)


def find_entry_points(repo_identifier: str):
    """Find potential entry points in the repository."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"Entry points in {repo_key}:")
    print("=" * 80)

    entry_patterns = [
        "index.js", "index.ts", "main.py", "main.go", "main.rs",
        "app.py", "server.js", "server.ts", "__main__.py",
        "cli.js", "cli.ts", "bin/*"
    ]

    found = []

    for pattern in entry_patterns:
        matches = list(local_path.rglob(pattern))
        for match in matches:
            if match.is_file() and not any(part.startswith(".") for part in match.parts):
                rel_path = match.relative_to(local_path)
                found.append(str(rel_path))

    if not found:
        print("No obvious entry points found.")
        return

    for entry in sorted(found):
        print(f"  🚪 {entry}")

    print("\n" + "=" * 80)


def find_tests(repo_identifier: str):
    """Find test files in the repository."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not in knowledge base.", file=sys.stderr)
        sys.exit(1)

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        print(f"Error: Repository not cloned yet.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"Test files in {repo_key}:")
    print("=" * 80)

    test_patterns = [
        "test", "tests", "spec", "__tests__",
        "*_test.py", "*_test.go", "*.test.js", "*.test.ts",
        "*.spec.js", "*.spec.ts"
    ]

    found_tests = []

    # Find test directories
    for pattern in ["test", "tests", "spec", "__tests__"]:
        test_dirs = list(local_path.rglob(pattern))
        for test_dir in test_dirs:
            if test_dir.is_dir() and not any(part.startswith(".") for part in test_dir.parts):
                rel_path = test_dir.relative_to(local_path)
                found_tests.append(("dir", str(rel_path)))

    # Find test files
    for pattern in ["*_test.py", "*_test.go", "*.test.js", "*.test.ts", "*.spec.js", "*.spec.ts"]:
        test_files = list(local_path.rglob(pattern))
        for test_file in test_files:
            if not any(part.startswith(".") for part in test_file.parts):
                rel_path = test_file.relative_to(local_path)
                found_tests.append(("file", str(rel_path)))

    if not found_tests:
        print("No test files found.")
        return

    # Group by type
    dirs = [d for t, d in found_tests if t == "dir"]
    files = [f for t, f in found_tests if t == "file"]

    if dirs:
        print("\nTest directories:")
        for d in sorted(dirs):
            print(f"  📁 {d}")

    if files:
        print("\nTest files:")
        for f in sorted(files)[:30]:
            print(f"  🧪 {f}")

        if len(files) > 30:
            print(f"  ... and {len(files) - 30} more")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Knowledge Base Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Clone
    clone_parser = subparsers.add_parser("clone", help="Clone a repository")
    clone_parser.add_argument("repo", help="Repository identifier")
    clone_parser.add_argument("--depth", type=int, help="Clone depth (shallow clone)")

    # Sync
    sync_parser = subparsers.add_parser("sync", help="Sync (pull) a cloned repository")
    sync_parser.add_argument("repo", help="Repository identifier")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze repository structure")
    analyze_parser.add_argument("repo", help="Repository identifier")

    # Tree
    tree_parser = subparsers.add_parser("tree", help="Show directory tree")
    tree_parser.add_argument("repo", help="Repository identifier")
    tree_parser.add_argument("--depth", type=int, default=2, help="Tree depth")

    # README
    readme_parser = subparsers.add_parser("readme", help="Display README")
    readme_parser.add_argument("repo", help="Repository identifier")

    # Docs
    docs_parser = subparsers.add_parser("docs", help="Find documentation files")
    docs_parser.add_argument("repo", help="Repository identifier")

    # Entry points
    entry_parser = subparsers.add_parser("entry-points", help="Find entry points")
    entry_parser.add_argument("repo", help="Repository identifier")

    # Tests
    tests_parser = subparsers.add_parser("find-tests", help="Find test files")
    tests_parser.add_argument("repo", help="Repository identifier")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "clone":
        clone_repo(args.repo, depth=args.depth)
    elif args.command == "sync":
        sync_repo(args.repo)
    elif args.command == "analyze":
        analyze_repo(args.repo)
    elif args.command == "tree":
        show_tree(args.repo, depth=args.depth)
    elif args.command == "readme":
        show_readme(args.repo)
    elif args.command == "docs":
        find_docs(args.repo)
    elif args.command == "entry-points":
        find_entry_points(args.repo)
    elif args.command == "find-tests":
        find_tests(args.repo)


if __name__ == "__main__":
    main()
