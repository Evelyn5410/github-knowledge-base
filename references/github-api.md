# GitHub API Reference

This document explains how the GitHub Knowledge Base skill uses the GitHub API and how to optimize API usage.

## API Endpoints Used

The skill uses these GitHub API v3 endpoints:

### 1. Repository Information
```
GET https://api.github.com/repos/{owner}/{repo}
```

Used by: `kb.py add`

Returns:
- Repository description
- Star count
- Primary language
- Topics/tags
- Default branch
- Fork/parent info

**Rate limit impact**: 1 request per repository added

### 2. Repository Search
```
GET https://api.github.com/search/repositories?q={query}&sort=stars&order=desc
```

Used by: `kb_search.py github`

Query parameters:
- `q`: Search query (can include filters)
- `sort`: stars, forks, updated
- `order`: asc, desc
- `per_page`: Results per page (max 100)

**Rate limit impact**: 1 request per search

### Search Query Syntax

The skill constructs GitHub search queries using these operators:

- `topic:react` - Repositories with topic "react"
- `language:javascript` - JavaScript repositories
- `stars:>1000` - More than 1000 stars
- `stars:100..500` - Between 100 and 500 stars
- `forks:>50` - More than 50 forks
- `size:<1000` - Smaller than 1000 KB
- `pushed:>2024-01-01` - Updated after date
- `is:public` - Public repositories only
- `user:facebook` - Repos from specific user/org
- `org:nodejs` - Repos from specific organization

Combined example:
```bash
python kb_search.py github "state management" --stars ">5000" --language typescript
# Translates to: q=state management stars:>5000 language:typescript
```

## Rate Limits

GitHub API has two rate limit tiers:

### Unauthenticated Requests
- **Limit**: 60 requests per hour
- **Scope**: Per IP address
- **Reset**: Every hour on the clock

### Authenticated Requests (with GITHUB_TOKEN)
- **Limit**: 5,000 requests per hour
- **Scope**: Per token/user
- **Reset**: Every hour on the clock

### How to Check Rate Limit
```bash
# Unauthenticated
curl https://api.github.com/rate_limit

# Authenticated
curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/rate_limit
```

Response:
```json
{
  "resources": {
    "core": {
      "limit": 5000,
      "remaining": 4999,
      "reset": 1372700873
    },
    "search": {
      "limit": 30,
      "remaining": 30,
      "reset": 1372700873
    }
  }
}
```

Note: Search endpoints have a separate, lower limit (30/min authenticated, 10/min unauthenticated)

## Setting Up GitHub Token

### Creating a Token

1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "GitHub KB Tool"
4. Select scopes:
   - `public_repo` (read access to public repos)
5. Click "Generate token"
6. Copy the token (you won't see it again!)

### Using the Token

**Option 1: Environment Variable (Recommended)**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Add to your shell config (~/.bashrc, ~/.zshrc):
```bash
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
source ~/.bashrc
```

**Option 2: Per-Command**
```bash
GITHUB_TOKEN=ghp_your_token_here python kb.py add facebook/react
```

**Security**: Never commit tokens to git or share them publicly!

## Caching Strategy

The skill caches API responses in `~/.config/github-kb/cache/` to reduce API calls.

### What Gets Cached

Currently, no automatic caching is implemented (can be added as enhancement).

### Manual Cache Strategy

The index.json serves as a cache - once you add a repo, its metadata is stored and reused.

To refresh repo metadata:
```bash
# Remove and re-add
python kb.py remove facebook/react
python kb.py add facebook/react
```

## API Usage Patterns

### Efficient Usage

**Good**: Add repos one at a time based on research
```bash
python kb_search.py github "topic" --limit 10  # 1 API call
# Review results
python kb.py add selected/repo  # 1 API call per selected repo
```

**Inefficient**: Adding many repos without research
```bash
# Don't do this:
for repo in $(cat huge-list.txt); do
    python kb.py add "$repo"  # 1000 API calls!
done
```

### Search API Special Considerations

GitHub search API is more restricted:
- **Authenticated**: 30 requests/minute
- **Unauthenticated**: 10 requests/minute

Best practices:
- Use specific queries to get relevant results
- Use `--limit` to control results count
- Cache search results manually if needed

### Related Repository Discovery

The `kb_search.py related` command is smart about API usage:

1. First checks if repo is in your KB (no API call)
2. If yes, uses cached metadata (no API call)
3. If no, fetches from API (1 API call)
4. Then searches based on topics/language (1 API call)

Total: 1-2 API calls

## Error Handling

### Rate Limit Exceeded

When you hit the rate limit:

```
Error: GitHub API rate limit exceeded.
Set GITHUB_TOKEN environment variable for higher limits (5000/hour).
```

**Solutions**:
1. Set GITHUB_TOKEN (best solution)
2. Wait for rate limit reset
3. Use cached data (repos already in KB)

### Repository Not Found

```
Error: Repository not found on GitHub
```

**Possible causes**:
- Typo in repo name
- Repository is private
- Repository was deleted/renamed
- Incorrect owner name

**Solutions**:
- Verify repo exists on GitHub
- Check spelling: `owner/repo`
- Use full URL if unsure

### Network Issues

```
Error: GitHub API error: [code] [reason]
```

**Solutions**:
- Check internet connection
- Try again (transient errors)
- Check GitHub status: https://www.githubstatus.com/

## Advanced API Features

### Topics (Tags)

GitHub topics are retrieved automatically:

```python
# In kb.py add command
repo_data = fetch_github_api(api_url)
topics = repo_data.get("topics", [])
```

Topics can help with:
- Tagging repositories
- Finding related repos
- Search refinement

### Repository Relationships

Detecting related repositories:

1. **Same language**: repos.language
2. **Similar topics**: repos.topics
3. **Same organization**: repos.owner
4. **Forks**: repos.parent (not currently used)
5. **Dependencies**: (requires additional API calls)

## Extending API Usage

### Ideas for Enhancement

**1. Dependency Analysis**

Fetch package.json, requirements.txt, etc. to find dependencies:
```
GET https://api.github.com/repos/{owner}/{repo}/contents/package.json
```

Use this to suggest related libraries.

**2. Contributor Analysis**

Find what else contributors work on:
```
GET https://api.github.com/repos/{owner}/{repo}/contributors
GET https://api.github.com/users/{username}/repos
```

**3. Star History**

Track repo popularity over time:
```
GET https://api.github.com/repos/{owner}/{repo}/stargazers
# With Accept: application/vnd.github.v3.star+json
```

**4. Issue/PR Analysis**

Understand repo activity and patterns:
```
GET https://api.github.com/repos/{owner}/{repo}/issues
GET https://api.github.com/repos/{owner}/{repo}/pulls
```

**5. README Fetching**

Get README without cloning:
```
GET https://api.github.com/repos/{owner}/{repo}/readme
```

Returns base64-encoded content.

### Implementation Example

To add README caching without cloning:

```python
import base64

def fetch_readme(owner, repo):
    """Fetch and cache README without cloning."""
    cache_file = CACHE_DIR / f"{owner}__{repo}__readme.md"

    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return f.read()

    # Fetch from API
    api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    data = fetch_github_api(api_url)

    # Decode base64 content
    content = base64.b64decode(data['content']).decode('utf-8')

    # Cache it
    with open(cache_file, 'w') as f:
        f.write(content)

    return content
```

## API Best Practices

1. **Use tokens** - Always set GITHUB_TOKEN for serious use
2. **Cache aggressively** - Store metadata to avoid re-fetching
3. **Batch operations** - Plan your queries to minimize API calls
4. **Handle errors** - Always check for rate limits and errors
5. **Respect limits** - Don't abuse the API
6. **Use ETags** - For caching (not currently implemented)
7. **Monitor usage** - Check remaining rate limit periodically

## Monitoring API Usage

### Check Rate Limit Before Heavy Operations

Create a helper script:

```bash
#!/bin/bash
# check-rate-limit.sh

TOKEN="${GITHUB_TOKEN:-}"

if [ -z "$TOKEN" ]; then
    echo "Unauthenticated (60/hour)"
    curl -s https://api.github.com/rate_limit | \
        jq '.resources.core | "Remaining: \(.remaining)/\(.limit)"'
else
    echo "Authenticated (5000/hour)"
    curl -s -H "Authorization: token $TOKEN" https://api.github.com/rate_limit | \
        jq '.resources.core | "Remaining: \(.remaining)/\(.limit)"'
fi
```

Usage:
```bash
./check-rate-limit.sh
# Output: Remaining: 4850/5000
```

### Log API Calls

Add to scripts for debugging:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_github_api(url: str) -> Dict:
    logger.info(f"API call: {url}")
    # ... existing code ...
    logger.info(f"Rate limit remaining: {response.headers.get('X-RateLimit-Remaining')}")
```

## GraphQL API Alternative

For advanced users, GitHub's GraphQL API v4 is more efficient:

### Benefits
- Fetch exactly what you need
- Combine multiple requests
- Better for complex queries

### Example Query

```graphql
query {
  repository(owner: "facebook", name: "react") {
    description
    stargazerCount
    primaryLanguage { name }
    repositoryTopics(first: 10) {
      nodes { topic { name } }
    }
  }
}
```

### Not Currently Used

The skill uses REST API v3 for simplicity and no dependencies. GraphQL support could be added as an enhancement.

## Resources

- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Rate Limiting](https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting)
- [Search Syntax](https://docs.github.com/en/search-github/searching-on-github/searching-for-repositories)
- [Authentication](https://docs.github.com/en/rest/overview/other-authentication-methods)
- [GitHub Status](https://www.githubstatus.com/)
