#!/usr/bin/env python3
"""
GitHub Knowledge Base Search
Search GitHub for repos, find related repos, and search code across your KB.
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional
import subprocess
import ssl

KB_DIR = Path.home() / ".config" / "github-kb"
INDEX_FILE = KB_DIR / "index.json"
REPOS_DIR = KB_DIR / "repos"
CACHE_DIR = KB_DIR / "cache"


def load_index() -> Dict:
    """Load the knowledge base index."""
    if not INDEX_FILE.exists():
        return {"repos": {}}

    with open(INDEX_FILE, 'r') as f:
        return json.load(f)


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
        if e.code == 403:
            print("Warning: GitHub API rate limit exceeded.", file=sys.stderr)
            print("Set GITHUB_TOKEN environment variable for higher limits (5000/hour).", file=sys.stderr)
            sys.exit(1)
        else:
            raise ValueError(f"GitHub API error: {e.code} {e.reason}")


def search_github(query: str, stars: Optional[str] = None, language: Optional[str] = None, limit: int = 10):
    """Search GitHub for repositories."""
    # Build search query
    search_parts = [query]

    if stars:
        search_parts.append(f"stars:{stars}")

    if language:
        search_parts.append(f"language:{language}")

    q = " ".join(search_parts)

    # Encode for URL
    encoded_q = urllib.parse.quote(q)

    # GitHub search API
    url = f"https://api.github.com/search/repositories?q={encoded_q}&sort=stars&order=desc&per_page={limit}"

    print(f"Searching GitHub: {q}")
    print(f"(Limit: {limit} results)\n")

    try:
        data = fetch_github_api(url)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    items = data.get("items", [])

    if not items:
        print("No repositories found.")
        return

    print(f"Found {data.get('total_count', 0):,} repositories (showing top {len(items)})")
    print("=" * 80)

    for i, repo in enumerate(items, 1):
        print(f"\n{i}. {repo['full_name']}")
        print(f"   {repo['description'] or 'No description'}")
        print(f"   ⭐ {repo['stargazers_count']:,} | "
              f"Language: {repo['language'] or 'N/A'} | "
              f"Forks: {repo['forks_count']:,}")
        print(f"   URL: {repo['html_url']}")

        # Check if already in KB
        index = load_index()
        if repo['full_name'] in index.get("repos", {}):
            print(f"   ✓ Already in your knowledge base")

    print("\n" + "=" * 80)
    print(f"\nTo add a repository: python kb.py add <owner/repo>")


def find_related(repo_identifier: str, limit: int = 10):
    """Find repositories related to one in your KB."""
    # Parse repo identifier
    from kb import parse_repo_identifier, get_repo_key

    try:
        owner, repo = parse_repo_identifier(repo_identifier)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    repo_key = get_repo_key(owner, repo)

    # Get repo info from index or GitHub
    index = load_index()

    if repo_key in index.get("repos", {}):
        repo_data = index["repos"][repo_key]
        language = repo_data["metadata"].get("language", "")
        topics = repo_data["metadata"].get("topics", [])
        summary = repo_data.get("summary", "")
    else:
        # Fetch from GitHub
        print(f"Fetching info for {repo_key}...")
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            github_data = fetch_github_api(api_url)
            language = github_data.get("language", "")
            topics = github_data.get("topics", [])
            summary = github_data.get("description", "")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    print(f"\nFinding repositories related to: {repo_key}")
    print(f"Language: {language}")
    if topics:
        print(f"Topics: {', '.join(topics)}")
    print()

    # Search by topics if available
    if topics:
        topic_query = " ".join(topics[:3])  # Use top 3 topics
        search_github(topic_query, language=language, limit=limit)
    elif language:
        # Extract keywords from summary
        import re
        words = re.findall(r'\b\w+\b', summary.lower())
        common_words = {'a', 'an', 'the', 'for', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'of'}
        keywords = [w for w in words if len(w) > 3 and w not in common_words][:3]

        if keywords:
            keyword_query = " ".join(keywords)
            search_github(keyword_query, language=language, limit=limit)
        else:
            search_github(language, limit=limit)
    else:
        print("Unable to determine search criteria for related repos.")


def search_code_in_kb(pattern: str, tag: Optional[str] = None, repo: Optional[str] = None):
    """Search for code patterns across locally cloned KB repositories."""
    index = load_index()

    if not index.get("repos"):
        print("Knowledge base is empty. Add repositories first.")
        sys.exit(1)

    # Filter repos
    repos_to_search = {}

    if repo:
        # Search specific repo
        from kb import parse_repo_identifier, get_repo_key

        try:
            owner, repo_name = parse_repo_identifier(repo)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        repo_key = get_repo_key(owner, repo_name)

        if repo_key not in index["repos"]:
            print(f"Error: Repository '{repo_key}' not found in KB.", file=sys.stderr)
            sys.exit(1)

        if not index["repos"][repo_key].get("last_synced"):
            print(f"Error: Repository '{repo_key}' not cloned yet.", file=sys.stderr)
            print(f"Clone it first: python kb_explore.py clone {repo_key}")
            sys.exit(1)

        repos_to_search[repo_key] = index["repos"][repo_key]
    else:
        # Search all cloned repos (optionally filtered by tag)
        for repo_key, repo_data in index["repos"].items():
            if not repo_data.get("last_synced"):
                continue  # Skip non-cloned repos

            if tag and tag not in repo_data.get("tags", []):
                continue  # Skip repos without the tag

            repos_to_search[repo_key] = repo_data

    if not repos_to_search:
        print("No cloned repositories to search.")
        if tag:
            print(f"(filtered by tag: {tag})")
        sys.exit(1)

    print(f"Searching for '{pattern}' across {len(repos_to_search)} repositories...")
    print("=" * 80)

    total_matches = 0

    for repo_key, repo_data in repos_to_search.items():
        local_path = Path(repo_data["local_path"])

        if not local_path.exists():
            continue

        # Use ripgrep if available, otherwise use grep
        try:
            # Try ripgrep first (faster)
            result = subprocess.run(
                ["rg", "-n", "-C", "2", pattern, str(local_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"\n📁 {repo_key}")
                print(result.stdout)
                # Count matches
                total_matches += result.stdout.count("\n") // 4  # Approximate

        except FileNotFoundError:
            # Fall back to grep
            try:
                result = subprocess.run(
                    ["grep", "-r", "-n", "-C", "2", pattern, str(local_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"\n📁 {repo_key}")
                    print(result.stdout)
                    total_matches += result.stdout.count("\n") // 4

            except Exception as e:
                print(f"Error searching {repo_key}: {e}", file=sys.stderr)

        except subprocess.TimeoutExpired:
            print(f"Warning: Search timed out for {repo_key}", file=sys.stderr)

    print("\n" + "=" * 80)
    if total_matches > 0:
        print(f"Found approximately {total_matches} matches")
    else:
        print("No matches found")


def compare_repos(repo1: str, repo2: str, pattern: str):
    """Compare how two repositories implement a specific pattern."""
    from kb import parse_repo_identifier, get_repo_key

    index = load_index()

    # Parse and validate repos
    repos_to_compare = []

    for repo_id in [repo1, repo2]:
        try:
            owner, repo_name = parse_repo_identifier(repo_id)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        repo_key = get_repo_key(owner, repo_name)

        if repo_key not in index.get("repos", {}):
            print(f"Error: Repository '{repo_key}' not in KB.", file=sys.stderr)
            sys.exit(1)

        if not index["repos"][repo_key].get("last_synced"):
            print(f"Error: Repository '{repo_key}' not cloned.", file=sys.stderr)
            print(f"Clone it: python kb_explore.py clone {repo_key}")
            sys.exit(1)

        repos_to_compare.append((repo_key, index["repos"][repo_key]))

    print(f"Comparing '{pattern}' implementation:")
    print("=" * 80)

    for repo_key, repo_data in repos_to_compare:
        local_path = Path(repo_data["local_path"])

        print(f"\n📁 {repo_key}")
        print("-" * 80)

        try:
            # Use ripgrep if available
            result = subprocess.run(
                ["rg", "-n", "-C", "3", pattern, str(local_path)],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"No matches found for '{pattern}'")

        except FileNotFoundError:
            # Fall back to grep
            try:
                result = subprocess.run(
                    ["grep", "-r", "-n", "-C", "3", pattern, str(local_path)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(result.stdout)
                else:
                    print(f"No matches found for '{pattern}'")

            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Knowledge Base Search",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # GitHub search
    github_parser = subparsers.add_parser("github", help="Search GitHub for repositories")
    github_parser.add_argument("query", help="Search query")
    github_parser.add_argument("--stars", help="Star filter (e.g., '>1000', '100..500')")
    github_parser.add_argument("--language", help="Programming language filter")
    github_parser.add_argument("--limit", type=int, default=10, help="Number of results")

    # Related repos
    related_parser = subparsers.add_parser("related", help="Find repos related to one in your KB")
    related_parser.add_argument("repo", help="Repository identifier")
    related_parser.add_argument("--limit", type=int, default=10, help="Number of results")

    # Code search
    code_parser = subparsers.add_parser("code", help="Search code across KB repositories")
    code_parser.add_argument("pattern", help="Code pattern to search for")
    code_parser.add_argument("--tag", help="Filter repos by tag")
    code_parser.add_argument("--repo", help="Search specific repo only")

    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare implementation between two repos")
    compare_parser.add_argument("repo1", help="First repository")
    compare_parser.add_argument("repo2", help="Second repository")
    compare_parser.add_argument("pattern", help="Pattern to compare")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "github":
        search_github(args.query, stars=args.stars, language=args.language, limit=args.limit)
    elif args.command == "related":
        find_related(args.repo, limit=args.limit)
    elif args.command == "code":
        search_code_in_kb(args.pattern, tag=args.tag, repo=args.repo)
    elif args.command == "compare":
        compare_repos(args.repo1, args.repo2, args.pattern)


if __name__ == "__main__":
    main()
