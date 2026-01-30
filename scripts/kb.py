#!/usr/bin/env python3
"""
GitHub Knowledge Base Manager
Unified CLI for managing your personal GitHub repository knowledge base.
"""

import json
import os
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import urllib.request
import urllib.error
import ssl

KB_DIR = Path.home() / ".config" / "github-kb"
INDEX_FILE = KB_DIR / "index.json"
REPOS_DIR = KB_DIR / "repos"
NOTES_DIR = KB_DIR / "notes"
CACHE_DIR = KB_DIR / "cache"


def init_kb():
    """Initialize knowledge base directory structure."""
    KB_DIR.mkdir(parents=True, exist_ok=True)
    REPOS_DIR.mkdir(exist_ok=True)
    NOTES_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)

    if not INDEX_FILE.exists():
        default_index = {
            "version": "1.0",
            "repos": {},
            "tags": [],
            "last_updated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
        save_index(default_index)


def load_index() -> Dict:
    """Load the knowledge base index."""
    if not INDEX_FILE.exists():
        init_kb()

    with open(INDEX_FILE, 'r') as f:
        return json.load(f)


def save_index(index: Dict):
    """Save the knowledge base index."""
    index["last_updated"] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    with open(INDEX_FILE, 'w') as f:
        json.dump(index, f, indent=2)


def parse_repo_identifier(identifier: str) -> tuple:
    """Parse repo identifier into (owner, repo) tuple.

    Accepts:
    - https://github.com/owner/repo
    - github.com/owner/repo
    - owner/repo
    """
    identifier = identifier.strip()

    # Remove https:// or http://
    if identifier.startswith("https://"):
        identifier = identifier[8:]
    elif identifier.startswith("http://"):
        identifier = identifier[7:]

    # Remove github.com/
    if identifier.startswith("github.com/"):
        identifier = identifier[11:]

    # Remove trailing .git
    if identifier.endswith(".git"):
        identifier = identifier[:-4]

    # Remove trailing slash
    identifier = identifier.rstrip("/")

    # Split and validate
    parts = identifier.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid repo identifier: {identifier}. Expected format: owner/repo")

    return parts[0], parts[1]


def get_repo_key(owner: str, repo: str) -> str:
    """Get the standard repo key format."""
    return f"{owner}/{repo}"


def fetch_github_api(url: str) -> Dict:
    """Fetch data from GitHub API with optional token auth."""
    headers = {"Accept": "application/vnd.github.v3+json"}

    token = os.environ.get("GITHUB_TOKEN")
    if token:
        # Use Bearer for fine-grained tokens (github_pat_), token for classic (ghp_)
        auth_type = "Bearer" if token.startswith("github_pat_") else "token"
        headers["Authorization"] = f"{auth_type} {token}"

    req = urllib.request.Request(url, headers=headers)

    # Create SSL context that doesn't verify certificates (workaround for macOS SSL issues)
    # TODO: This is a temporary fix. Proper solution is to install SSL certificates.
    ssl_context = ssl.create_default_context()
    if os.environ.get("KB_SKIP_SSL_VERIFY"):
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise ValueError(f"Repository not found on GitHub")
        elif e.code == 403:
            raise ValueError(f"GitHub API rate limit exceeded. Set GITHUB_TOKEN env var for higher limits.")
        else:
            raise ValueError(f"GitHub API error: {e.code} {e.reason}")


def add_repo(identifier: str):
    """Add a repository to the knowledge base."""
    init_kb()

    try:
        owner, repo = parse_repo_identifier(identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)

    # Load index
    index = load_index()

    # Check if already exists
    if repo_key in index["repos"]:
        print(f"Repository '{repo_key}' already exists in knowledge base.")
        print(f"Use 'kb.py info {repo_key}' to view details.")
        return

    # Fetch repo info from GitHub API
    print(f"Fetching repository info from GitHub...")
    try:
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        repo_data = fetch_github_api(api_url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Create repo entry
    local_path = REPOS_DIR / f"{owner}__{repo}"

    repo_entry = {
        "url": f"https://github.com/{owner}/{repo}",
        "added_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "tags": [],
        "status": "bookmarked",
        "notes": "",
        "key_files": [],
        "summary": repo_data.get("description", ""),
        "local_path": str(local_path),
        "last_synced": None,
        "metadata": {
            "stars": repo_data.get("stargazers_count", 0),
            "language": repo_data.get("language", ""),
            "topics": repo_data.get("topics", []),
            "default_branch": repo_data.get("default_branch", "main")
        }
    }

    # Add to index
    index["repos"][repo_key] = repo_entry
    save_index(index)

    print(f"\n✓ Added '{repo_key}' to knowledge base")
    print(f"  Summary: {repo_entry['summary']}")
    print(f"  Stars: ⭐ {repo_entry['metadata']['stars']:,}")
    print(f"  Language: {repo_entry['metadata']['language']}")
    print(f"  Status: {repo_entry['status']}")

    # Smart next steps based on repository size
    stars = repo_entry['metadata']['stars']
    print(f"\n💡 Next Steps:")

    if stars > 50000:
        print(f"  → Clone (shallow, large repo): kb-explore clone {repo_key} --depth 1")
    elif stars > 10000:
        print(f"  → Clone (recommended): kb-explore clone {repo_key}")
    else:
        print(f"  → Clone: kb-explore clone {repo_key}")

    print(f"  → Organize: kb tag {repo_key} <tag1> <tag2>")
    print(f"  → Track updates: kb-changes watch {repo_key}")
    print(f"  → View details: kb info {repo_key}")

    # Suggest related repos
    if repo_entry['metadata'].get('topics'):
        topics = ', '.join(repo_entry['metadata']['topics'][:3])
        print(f"\n🔗 Topics: {topics}")
        print(f"  → Find related: kb-search related {repo_key}")


def list_repos(tag: Optional[str] = None, status: Optional[str] = None):
    """List repositories in the knowledge base."""
    init_kb()
    index = load_index()

    repos = index["repos"]

    if not repos:
        print("Knowledge base is empty.")
        print("\n💡 Get Started:")
        print("  → Add a repository: kb add <owner/repo>")
        print("  → Search GitHub: kb-search github \"topic\"")
        print("\nExamples:")
        print("  kb add facebook/react")
        print("  kb add expressjs/express")
        print("  kb-search github \"nodejs authentication\" --stars \">1000\"")
        return

    # Filter by tag
    if tag:
        repos = {k: v for k, v in repos.items() if tag in v["tags"]}
        if not repos:
            print(f"No repositories found with tag '{tag}'")
            return

    # Filter by status
    if status:
        repos = {k: v for k, v in repos.items() if v["status"] == status}
        if not repos:
            print(f"No repositories found with status '{status}'")
            return

    # Print header
    print(f"\nGitHub Knowledge Base ({len(repos)} repositories)")
    print("=" * 80)

    # Sort by added_at
    sorted_repos = sorted(repos.items(), key=lambda x: x[1]["added_at"], reverse=True)

    for repo_key, repo_data in sorted_repos:
        status_icon = {
            "bookmarked": "📌",
            "exploring": "🔍",
            "explored": "✓",
            "archived": "📦"
        }.get(repo_data["status"], "·")

        cloned = "💾" if repo_data.get("last_synced") else "☁️"

        print(f"\n{status_icon} {cloned} {repo_key}")
        print(f"   {repo_data['summary']}")

        if repo_data['tags']:
            tags_str = ", ".join(repo_data['tags'])
            print(f"   Tags: {tags_str}")

        print(f"   ⭐ {repo_data['metadata']['stars']:,} | "
              f"Language: {repo_data['metadata']['language'] or 'N/A'} | "
              f"Status: {repo_data['status']}")

    print("\n" + "=" * 80)
    print(f"Total: {len(repos)} repositories")

    # Show available tags
    all_tags = set()
    for repo_data in index["repos"].values():
        all_tags.update(repo_data["tags"])

    if all_tags:
        print(f"Available tags: {', '.join(sorted(all_tags))}")

    # Count repos by status
    not_cloned = sum(1 for r in repos.values() if not r.get("last_synced"))
    bookmarked = sum(1 for r in repos.values() if r.get("status") == "bookmarked")

    # Smart hints based on collection state
    if not_cloned > 0:
        print(f"\n💡 You have {not_cloned} repo(s) not cloned yet:")
        print(f"  → Clone all: for each repo, run kb-explore clone <repo>")
        print(f"  → Or use --depth 1 for large repos to save space")

    if bookmarked > 0 and not_cloned == 0:
        print(f"\n💡 You have {bookmarked} repo(s) ready to explore:")
        print(f"  → Search code: kb-search code \"pattern\" --tag <tag>")
        print(f"  → Compare repos: kb-search compare <repo1> <repo2> \"topic\"")

    print(f"\n💡 Quick Actions:")
    print(f"  → View details: kb info <repo>")
    print(f"  → Check updates: kb-changes updates")
    if all_tags:
        print(f"  → Filter by tag: kb list --tag {sorted(all_tags)[0]}")


def tag_repo(repo_identifier: str, tags: List[str]):
    """Add tags to a repository."""
    init_kb()

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not found in knowledge base.", file=sys.stderr)
        sys.exit(1)

    # Add tags (avoid duplicates)
    current_tags = set(index["repos"][repo_key]["tags"])
    current_tags.update(tags)
    index["repos"][repo_key]["tags"] = sorted(list(current_tags))

    save_index(index)

    print(f"✓ Tagged '{repo_key}' with: {', '.join(tags)}")
    print(f"  All tags: {', '.join(index['repos'][repo_key]['tags'])}")


def note_repo(repo_identifier: str, note: str):
    """Add or update notes for a repository."""
    init_kb()

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not found in knowledge base.", file=sys.stderr)
        sys.exit(1)

    # Update notes in index
    index["repos"][repo_key]["notes"] = note
    save_index(index)

    # Also save to dedicated notes file
    notes_file = NOTES_DIR / f"{owner}__{repo}.md"
    with open(notes_file, 'w') as f:
        f.write(f"# {repo_key}\n\n")
        f.write(f"{note}\n")

    print(f"✓ Added notes to '{repo_key}'")
    print(f"  Notes file: {notes_file}")


def set_status(repo_identifier: str, status: str):
    """Set the exploration status of a repository."""
    init_kb()

    valid_statuses = ["bookmarked", "exploring", "explored", "archived"]
    if status not in valid_statuses:
        print(f"Error: Invalid status. Must be one of: {', '.join(valid_statuses)}", file=sys.stderr)
        sys.exit(1)

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not found in knowledge base.", file=sys.stderr)
        sys.exit(1)

    index["repos"][repo_key]["status"] = status
    save_index(index)

    print(f"✓ Set status of '{repo_key}' to '{status}'")


def remove_repo(repo_identifier: str):
    """Remove a repository from the knowledge base."""
    init_kb()

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not found in knowledge base.", file=sys.stderr)
        sys.exit(1)

    # Remove from index
    del index["repos"][repo_key]
    save_index(index)

    print(f"✓ Removed '{repo_key}' from knowledge base")
    print(f"  Note: Local clone and notes were not deleted.")
    print(f"  To remove completely, delete:")
    print(f"    - {REPOS_DIR / f'{owner}__{repo}'}")
    print(f"    - {NOTES_DIR / f'{owner}__{repo}.md'}")


def info_repo(repo_identifier: str):
    """Show detailed information about a repository."""
    init_kb()

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        print(f"\nℹ️  Use format: owner/repo (e.g., facebook/react)", file=sys.stderr)
        print(f"\nTo see all repos in your KB:", file=sys.stderr)
        print(f"  kb list", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        print(f"Error: Repository '{repo_key}' not found in knowledge base.", file=sys.stderr)

        # Try to find similar repos
        similar = []
        search_term = repo.lower() if repo else repo_identifier.lower()
        for existing_key in index["repos"].keys():
            if search_term in existing_key.lower():
                similar.append(existing_key)

        if similar:
            print(f"\n💡 Did you mean one of these?", file=sys.stderr)
            for s in similar[:5]:
                print(f"  → kb info {s}", file=sys.stderr)
        else:
            print(f"\n💡 To see all repos:", file=sys.stderr)
            print(f"  → kb list", file=sys.stderr)
            print(f"\n💡 To add this repo:", file=sys.stderr)
            print(f"  → kb add {repo_key}", file=sys.stderr)

        sys.exit(1)

    repo_data = index["repos"][repo_key]

    print(f"\n{'='*80}")
    print(f"Repository: {repo_key}")
    print(f"{'='*80}")
    print(f"URL: {repo_data['url']}")
    print(f"Summary: {repo_data['summary']}")
    print(f"Status: {repo_data['status']}")
    print(f"Added: {repo_data['added_at']}")
    print(f"Stars: ⭐ {repo_data['metadata']['stars']:,}")
    print(f"Language: {repo_data['metadata']['language']}")

    if repo_data['tags']:
        print(f"Tags: {', '.join(repo_data['tags'])}")

    if repo_data['metadata'].get('topics'):
        print(f"Topics: {', '.join(repo_data['metadata']['topics'])}")

    if repo_data.get('last_synced'):
        print(f"Last Synced: {repo_data['last_synced']}")
        print(f"Local Path: {repo_data['local_path']}")
    else:
        print(f"Local Clone: Not cloned yet")

    if repo_data['key_files']:
        print(f"\nKey Files:")
        for f in repo_data['key_files']:
            print(f"  - {f}")

    if repo_data['notes']:
        print(f"\nNotes:")
        print(f"  {repo_data['notes']}")

    print(f"{'='*80}")

    # Smart hints based on status and state
    print(f"\n💡 Next Steps:")

    if not repo_data.get('last_synced'):
        # Not cloned yet
        stars = repo_data['metadata'].get('stars', 0)
        if stars > 50000:
            print(f"  → Clone (shallow for large repo): kb-explore clone {repo_key} --depth 1")
        else:
            print(f"  → Clone repository: kb-explore clone {repo_key}")
        print(f"  → Or explore online: kb-explore readme {repo_key}")
    elif repo_data['status'] == 'bookmarked':
        print(f"  → Start exploring: kb status {repo_key} exploring")
        print(f"  → Analyze structure: kb-explore analyze {repo_key}")
        print(f"  → Add tags: kb tag {repo_key} <tag1> <tag2>")
    elif repo_data['status'] == 'exploring':
        print(f"  → Search code: kb-search code \"pattern\" --repo {repo_key}")
        print(f"  → View structure: kb-explore tree {repo_key}")
        print(f"  → Track changes: kb-changes watch {repo_key}")
    elif repo_data['status'] == 'explored':
        print(f"  → Check for updates: kb-explore sync {repo_key}")
        print(f"  → Compare versions: kb-changes compare {repo_key} v1 v2")
        print(f"  → Find related repos: kb-search related {repo_key}")

    # Always show change tracking option
    print(f"  → What's new: kb-changes latest {repo_key} --detailed")

    print()


def stats():
    """Show knowledge base statistics."""
    init_kb()
    index = load_index()

    total = len(index["repos"])

    if total == 0:
        print("Knowledge base is empty.")
        return

    # Count by status
    status_counts = {}
    for repo_data in index["repos"].values():
        status = repo_data["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    # Count cloned
    cloned = sum(1 for r in index["repos"].values() if r.get("last_synced"))

    # Count by language
    lang_counts = {}
    for repo_data in index["repos"].values():
        lang = repo_data["metadata"].get("language", "Unknown")
        lang_counts[lang] = lang_counts.get(lang, 0) + 1

    # Get tags
    all_tags = set()
    for repo_data in index["repos"].values():
        all_tags.update(repo_data["tags"])

    print(f"\n{'='*80}")
    print(f"Knowledge Base Statistics")
    print(f"{'='*80}")
    print(f"Total Repositories: {total}")
    print(f"Cloned Locally: {cloned}")
    print(f"\nBy Status:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print(f"\nTop Languages:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {lang}: {count}")

    print(f"\nTotal Tags: {len(all_tags)}")
    if all_tags:
        print(f"Tags: {', '.join(sorted(all_tags))}")

    print(f"{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Knowledge Base Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a repository to the knowledge base")
    add_parser.add_argument("repo", help="Repository identifier (owner/repo or URL)")

    # List command
    list_parser = subparsers.add_parser("list", help="List repositories")
    list_parser.add_argument("--tag", help="Filter by tag")
    list_parser.add_argument("--status", help="Filter by status")

    # Tag command
    tag_parser = subparsers.add_parser("tag", help="Add tags to a repository")
    tag_parser.add_argument("repo", help="Repository identifier")
    tag_parser.add_argument("tags", nargs="+", help="Tags to add")

    # Note command
    note_parser = subparsers.add_parser("note", help="Add notes to a repository")
    note_parser.add_argument("repo", help="Repository identifier")
    note_parser.add_argument("note", help="Note text")

    # Status command
    status_parser = subparsers.add_parser("status", help="Set repository status")
    status_parser.add_argument("repo", help="Repository identifier")
    status_parser.add_argument("status", choices=["bookmarked", "exploring", "explored", "archived"])

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a repository")
    remove_parser.add_argument("repo", help="Repository identifier")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show repository details")
    info_parser.add_argument("repo", help="Repository identifier")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show knowledge base statistics")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "add":
        add_repo(args.repo)
    elif args.command == "list":
        list_repos(tag=args.tag, status=args.status)
    elif args.command == "tag":
        tag_repo(args.repo, args.tags)
    elif args.command == "note":
        note_repo(args.repo, args.note)
    elif args.command == "status":
        set_status(args.repo, args.status)
    elif args.command == "remove":
        remove_repo(args.repo)
    elif args.command == "info":
        info_repo(args.repo)
    elif args.command == "stats":
        stats()


if __name__ == "__main__":
    main()
