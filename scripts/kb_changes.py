#!/usr/bin/env python3
"""
GitHub Knowledge Base Change Tracker
Fetch and analyze changes in repositories - from major releases to minor API changes.
"""

import json
import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import urllib.request
import urllib.error
import re
import ssl

KB_DIR = Path.home() / ".config" / "github-kb"
INDEX_FILE = KB_DIR / "index.json"
REPOS_DIR = KB_DIR / "repos"
CHANGES_DIR = KB_DIR / "changes"


def init_changes_dir():
    """Initialize changes directory."""
    CHANGES_DIR.mkdir(parents=True, exist_ok=True)


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
    ssl_context = ssl.create_default_context()
    if os.environ.get("KB_SKIP_SSL_VERIFY"):
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(req, context=ssl_context) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        elif e.code == 403:
            print("Warning: GitHub API rate limit exceeded.", file=sys.stderr)
            print("Set GITHUB_TOKEN environment variable for higher limits.", file=sys.stderr)
            return None
        else:
            print(f"GitHub API error: {e.code} {e.reason}", file=sys.stderr)
            return None


def get_latest_release(owner: str, repo: str) -> Optional[Dict]:
    """Fetch the latest release from GitHub."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
    return fetch_github_api(api_url)


def get_all_releases(owner: str, repo: str, limit: int = 10) -> List[Dict]:
    """Fetch recent releases from GitHub."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/releases?per_page={limit}"
    data = fetch_github_api(api_url)
    return data if data else []


def get_recent_commits(owner: str, repo: str, limit: int = 20) -> List[Dict]:
    """Fetch recent commits from GitHub."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page={limit}"
    data = fetch_github_api(api_url)
    return data if data else []


def get_commit_details(owner: str, repo: str, sha: str) -> Optional[Dict]:
    """Fetch detailed commit information."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    return fetch_github_api(api_url)


def analyze_text_changes(text: str) -> Dict:
    """Analyze text for different types of changes."""
    changes = {
        "breaking_changes": [],
        "deprecations": [],
        "new_features": [],
        "bug_fixes": [],
        "api_changes": [],
        "naming_changes": [],
        "performance": [],
        "security": []
    }

    # Split into lines for analysis
    lines = text.split('\n')

    for line in lines:
        line_lower = line.lower()

        # Breaking changes
        if any(keyword in line_lower for keyword in ['breaking', 'breaking change', 'backwards incompatible', 'removed']):
            changes["breaking_changes"].append(line.strip())

        # Deprecations
        if any(keyword in line_lower for keyword in ['deprecat', 'obsolete', 'legacy']):
            changes["deprecations"].append(line.strip())

        # New features
        if any(keyword in line_lower for keyword in ['add', 'new', 'introduce', 'implement', 'feature']):
            changes["new_features"].append(line.strip())

        # Bug fixes
        if any(keyword in line_lower for keyword in ['fix', 'bug', 'issue', 'patch', 'resolve']):
            changes["bug_fixes"].append(line.strip())

        # API changes (including naming)
        if any(keyword in line_lower for keyword in ['api', 'interface', 'signature', 'parameter', 'method']):
            changes["api_changes"].append(line.strip())

        # Performance
        if any(keyword in line_lower for keyword in ['performance', 'optimize', 'faster', 'improve', 'speed']):
            changes["performance"].append(line.strip())

        # Security
        if any(keyword in line_lower for keyword in ['security', 'vulnerability', 'cve', 'exploit']):
            changes["security"].append(line.strip())

    # Detect naming convention changes (camelCase -> snake_case, etc.)
    naming_patterns = [
        (r'(\w+[A-Z]\w+)\s*->\s*(\w+_\w+)', 'camelCase to snake_case'),
        (r'(\w+_\w+)\s*->\s*(\w+[A-Z]\w+)', 'snake_case to camelCase'),
        (r'rename[d]?\s+(\w+)\s+to\s+(\w+)', 'renamed'),
        (r'(\w+)\s+is now\s+(\w+)', 'renamed'),
    ]

    for pattern, change_type in naming_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            changes["naming_changes"].append(f"{change_type}: {match.group(1)} -> {match.group(2)}")

    # Remove duplicates and empty lists
    for key in changes:
        changes[key] = list(set(changes[key]))

    return changes


def fetch_changelog(owner: str, repo: str) -> Optional[str]:
    """Fetch CHANGELOG file content from repository."""
    from kb import parse_repo_identifier, get_repo_key

    repo_key = get_repo_key(owner, repo)
    index = load_index()

    if repo_key not in index["repos"]:
        return None

    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if not local_path.exists():
        return None

    # Common changelog filenames
    changelog_patterns = [
        "CHANGELOG.md", "CHANGELOG", "CHANGELOG.txt",
        "CHANGES.md", "CHANGES", "CHANGES.txt",
        "HISTORY.md", "HISTORY", "HISTORY.txt",
        "RELEASES.md", "NEWS.md"
    ]

    for pattern in changelog_patterns:
        changelog_files = list(local_path.glob(pattern))
        if changelog_files:
            try:
                with open(changelog_files[0], 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            except Exception:
                pass

    return None


def show_latest_changes(repo_identifier: str, detailed: bool = False):
    """Show latest changes from releases and commits."""
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

    print(f"Latest Changes: {repo_key}")
    print("=" * 80)

    # Fetch latest release
    print("\n📦 Latest Release")
    print("-" * 80)

    latest_release = get_latest_release(owner, repo)

    if latest_release:
        print(f"Version: {latest_release.get('tag_name', 'N/A')}")
        print(f"Name: {latest_release.get('name', 'N/A')}")
        print(f"Published: {latest_release.get('published_at', 'N/A')}")
        print(f"Author: {latest_release.get('author', {}).get('login', 'N/A')}")

        body = latest_release.get('body', '')
        if body:
            print(f"\nRelease Notes:")
            # Limit to first 50 lines unless detailed
            lines = body.split('\n')
            if not detailed and len(lines) > 50:
                print('\n'.join(lines[:50]))
                print(f"\n... ({len(lines) - 50} more lines)")
            else:
                print(body)

            # Analyze changes
            if detailed:
                print("\n🔍 Change Analysis:")
                print("-" * 80)
                changes = analyze_text_changes(body)

                if changes["breaking_changes"]:
                    print("\n⚠️  Breaking Changes:")
                    for change in changes["breaking_changes"][:10]:
                        print(f"  • {change}")

                if changes["naming_changes"]:
                    print("\n🔄 Naming/API Changes:")
                    for change in changes["naming_changes"]:
                        print(f"  • {change}")

                if changes["deprecations"]:
                    print("\n⏳ Deprecations:")
                    for change in changes["deprecations"][:5]:
                        print(f"  • {change}")

                if changes["new_features"]:
                    print("\n✨ New Features:")
                    for change in changes["new_features"][:10]:
                        print(f"  • {change}")

                if changes["security"]:
                    print("\n🔒 Security:")
                    for change in changes["security"]:
                        print(f"  • {change}")
    else:
        print("No releases found.")

    # Fetch recent commits
    print("\n\n📝 Recent Commits")
    print("-" * 80)

    commits = get_recent_commits(owner, repo, limit=10)

    if commits:
        for i, commit in enumerate(commits[:10], 1):
            commit_data = commit.get('commit', {})
            message = commit_data.get('message', '').split('\n')[0]
            author = commit_data.get('author', {}).get('name', 'Unknown')
            date = commit_data.get('author', {}).get('date', 'N/A')
            sha = commit.get('sha', '')[:7]

            print(f"\n{i}. {message}")
            print(f"   {sha} by {author} on {date}")

            if detailed and len(commit_data.get('message', '').split('\n')) > 1:
                full_message = commit_data.get('message', '')
                lines = full_message.split('\n')[1:]
                for line in lines[:5]:
                    if line.strip():
                        print(f"   {line}")
    else:
        print("Could not fetch commits.")

    print("\n" + "=" * 80)


def compare_versions(repo_identifier: str, version1: str, version2: str):
    """Compare two versions/releases."""
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

    print(f"Comparing Versions: {repo_key}")
    print(f"{version1} → {version2}")
    print("=" * 80)

    # Try to use local git if cloned
    repo_data = index["repos"][repo_key]
    local_path = Path(repo_data["local_path"])

    if local_path.exists():
        # Use git log to compare
        try:
            result = subprocess.run(
                ["git", "-C", str(local_path), "log", f"{version1}..{version2}", "--oneline"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("\nCommits between versions:")
                print(result.stdout)

            # Get detailed diff stats
            result = subprocess.run(
                ["git", "-C", str(local_path), "diff", "--stat", version1, version2],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("\nFile changes:")
                print(result.stdout)

        except Exception as e:
            print(f"Error comparing with git: {e}", file=sys.stderr)
    else:
        print("Repository not cloned locally. Clone it first to see detailed comparison.")
        print(f"Run: python kb_explore.py clone {repo_key}")

    print("\n" + "=" * 80)


def track_api_changes(repo_identifier: str, file_pattern: str = None):
    """Track API changes by analyzing code files."""
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
        print(f"Error: Repository not cloned.", file=sys.stderr)
        print(f"Clone it first: python kb_explore.py clone {repo_key}")
        sys.exit(1)

    print(f"API Change Tracking: {repo_key}")
    print("=" * 80)

    # Get recent commits that modified API files
    try:
        # Default patterns for API files
        patterns = [
            "*.ts", "*.js",  # TypeScript/JavaScript
            "*.py",  # Python
            "*.go",  # Go
            "*.rs",  # Rust
            "*.java",  # Java
        ]

        if file_pattern:
            patterns = [file_pattern]

        for pattern in patterns:
            # Find recent changes in API files
            result = subprocess.run(
                ["git", "-C", str(local_path), "log", "-p", "-10", "--", f"**/{pattern}"],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                # Look for property/method renames
                diff_output = result.stdout

                # Patterns to detect API changes
                api_patterns = [
                    # Property renames: - oldName, + newName
                    (r'-\s*(\w+):\s*(\w+).*\n\+\s*(\w+):\s*(\w+)', 'Property renamed'),
                    # Function signature changes
                    (r'-\s*(?:function|def|fn)\s+(\w+)', 'Function removed/changed'),
                    (r'\+\s*(?:function|def|fn)\s+(\w+)', 'Function added/changed'),
                    # camelCase to snake_case
                    (r'-.*?([a-z]+[A-Z]\w+)', 'Possible camelCase removal'),
                    (r'\+.*?([a-z]+_[a-z_]+)', 'Possible snake_case addition'),
                ]

                findings = []
                for pattern_regex, description in api_patterns:
                    matches = re.finditer(pattern_regex, diff_output[:5000])  # First 5000 chars
                    for match in matches:
                        findings.append((description, match.group(0)[:100]))

                if findings:
                    print(f"\nDetected changes in {pattern} files:")
                    for desc, sample in findings[:20]:  # Limit to 20
                        print(f"  • {desc}")
                        print(f"    {sample.strip()}")

    except Exception as e:
        print(f"Error tracking API changes: {e}", file=sys.stderr)

    print("\n" + "=" * 80)


def show_changelog(repo_identifier: str, lines: int = 100):
    """Show repository changelog."""
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)

    changelog = fetch_changelog(owner, repo)

    if not changelog:
        print(f"No CHANGELOG found for {repo_key}")
        print(f"Try: python kb_changes.py latest {repo_key}")
        return

    print(f"CHANGELOG: {repo_key}")
    print("=" * 80)

    changelog_lines = changelog.split('\n')
    if len(changelog_lines) > lines:
        print('\n'.join(changelog_lines[:lines]))
        print(f"\n... ({len(changelog_lines) - lines} more lines)")
        print(f"\nView full changelog in: ~/.config/github-kb/repos/{owner}__{repo}/CHANGELOG*")
    else:
        print(changelog)

    print("\n" + "=" * 80)

    # Analyze the changelog
    print("\n🔍 Changelog Analysis:")
    print("-" * 80)

    changes = analyze_text_changes(changelog)

    if changes["breaking_changes"]:
        print(f"\n⚠️  Breaking Changes ({len(changes['breaking_changes'])} found)")
        for change in changes["breaking_changes"][:5]:
            print(f"  • {change}")

    if changes["naming_changes"]:
        print(f"\n🔄 Naming Changes ({len(changes['naming_changes'])} found)")
        for change in changes["naming_changes"][:10]:
            print(f"  • {change}")

    if changes["deprecations"]:
        print(f"\n⏳ Deprecations ({len(changes['deprecations'])} found)")
        for change in changes["deprecations"][:5]:
            print(f"  • {change}")


def watch_repo(repo_identifier: str):
    """Add a repository to watch list for changes."""
    from kb import parse_repo_identifier, get_repo_key

    init_changes_dir()

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

    # Save current state
    latest_release = get_latest_release(owner, repo)
    commits = get_recent_commits(owner, repo, limit=5)

    watch_data = {
        "repo": repo_key,
        "last_checked": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "latest_release": latest_release.get('tag_name') if latest_release else None,
        "latest_commit": commits[0].get('sha')[:7] if commits else None
    }

    watch_file = CHANGES_DIR / f"{owner}__{repo}.json"
    with open(watch_file, 'w') as f:
        json.dump(watch_data, f, indent=2)

    print(f"✓ Now watching {repo_key} for changes")
    print(f"  Latest release: {watch_data['latest_release'] or 'None'}")
    print(f"  Latest commit: {watch_data['latest_commit'] or 'Unknown'}")


def check_updates(repo_identifier: str = None):
    """Check for updates in watched repositories."""
    init_changes_dir()

    if repo_identifier:
        # Check specific repo
        from kb import parse_repo_identifier, get_repo_key

        try:
            owner, repo = parse_repo_identifier(repo_identifier)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        repo_key = get_repo_key(owner, repo)
        watch_file = CHANGES_DIR / f"{owner}__{repo}.json"

        if not watch_file.exists():
            print(f"Repository '{repo_key}' is not being watched.")
            print(f"Start watching: python kb_changes.py watch {repo_key}")
            return

        check_single_repo(owner, repo, watch_file)
    else:
        # Check all watched repos
        watch_files = list(CHANGES_DIR.glob("*.json"))

        if not watch_files:
            print("No repositories being watched.")
            print("Start watching: python kb_changes.py watch <repo>")
            return

        print(f"Checking {len(watch_files)} watched repositories...")
        print("=" * 80)

        for watch_file in watch_files:
            # Parse owner/repo from filename
            parts = watch_file.stem.split("__")
            if len(parts) == 2:
                owner, repo = parts
                check_single_repo(owner, repo, watch_file)


def check_single_repo(owner: str, repo: str, watch_file: Path):
    """Check a single repository for updates."""
    with open(watch_file, 'r') as f:
        old_data = json.load(f)

    repo_key = f"{owner}/{repo}"

    # Fetch current state
    latest_release = get_latest_release(owner, repo)
    commits = get_recent_commits(owner, repo, limit=5)

    current_release = latest_release.get('tag_name') if latest_release else None
    current_commit = commits[0].get('sha')[:7] if commits else None

    has_updates = False

    print(f"\n📦 {repo_key}")

    # Check for new release
    if current_release != old_data.get('latest_release'):
        print(f"  🆕 New release: {old_data.get('latest_release')} → {current_release}")
        has_updates = True

    # Check for new commits
    if current_commit != old_data.get('latest_commit'):
        print(f"  📝 New commits since last check")
        has_updates = True

    if not has_updates:
        print(f"  ✓ No updates since last check")

    # Update watch file
    old_data['last_checked'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    old_data['latest_release'] = current_release
    old_data['latest_commit'] = current_commit

    with open(watch_file, 'w') as f:
        json.dump(old_data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Knowledge Base Change Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Latest changes
    latest_parser = subparsers.add_parser("latest", help="Show latest changes and releases")
    latest_parser.add_argument("repo", help="Repository identifier")
    latest_parser.add_argument("--detailed", action="store_true", help="Show detailed analysis")

    # Compare versions
    compare_parser = subparsers.add_parser("compare", help="Compare two versions")
    compare_parser.add_argument("repo", help="Repository identifier")
    compare_parser.add_argument("version1", help="First version (tag/branch/commit)")
    compare_parser.add_argument("version2", help="Second version (tag/branch/commit)")

    # Track API changes
    api_parser = subparsers.add_parser("api-changes", help="Track API changes")
    api_parser.add_argument("repo", help="Repository identifier")
    api_parser.add_argument("--pattern", help="File pattern (e.g., '*.ts')")

    # Show changelog
    changelog_parser = subparsers.add_parser("changelog", help="Show repository changelog")
    changelog_parser.add_argument("repo", help="Repository identifier")
    changelog_parser.add_argument("--lines", type=int, default=100, help="Number of lines to show")

    # Watch for changes
    watch_parser = subparsers.add_parser("watch", help="Watch repository for changes")
    watch_parser.add_argument("repo", help="Repository identifier")

    # Check updates
    updates_parser = subparsers.add_parser("updates", help="Check for updates in watched repos")
    updates_parser.add_argument("repo", nargs="?", help="Optional: specific repository to check")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "latest":
        show_latest_changes(args.repo, detailed=args.detailed)
    elif args.command == "compare":
        compare_versions(args.repo, args.version1, args.version2)
    elif args.command == "api-changes":
        track_api_changes(args.repo, file_pattern=args.pattern)
    elif args.command == "changelog":
        show_changelog(args.repo, lines=args.lines)
    elif args.command == "watch":
        watch_repo(args.repo)
    elif args.command == "updates":
        check_updates(args.repo)


if __name__ == "__main__":
    main()
