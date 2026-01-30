---
name: github-knowledge-base
version: 1.1.0
description: >
  Build and explore a personal knowledge base of GitHub repositories. Discover repos by topic,
  track API changes, clone and analyze codebases, search for implementation patterns, and compare
  different approaches across your collection.

  BONUS FEATURES for code reviews: Smart book detection (Clean Code, Refactoring, Design Patterns, etc.)
  uses Claude's training data instead of reading PDFs (saves 40K+ tokens per book). PDF summarization
  available for research papers and niche documents (80-90% token savings on re-reads).

  Use this skill when the user wants to: add/remove repos, search GitHub, explore codebases, track API changes,
  compare implementations, or review code using technical book principles.

  Triggers: "add repo", "find repos for", "search my KB", "how does X handle Y", "compare repos",
  "explore this repo", "track changes", "what's new in", "review code using Clean Code".

author: Eve
tags: [github, knowledge-base, code-exploration, search, repositories, code-review, api-tracking, token-optimization]
---

# GitHub Knowledge Base Skill

Build and maintain a personal knowledge base of GitHub repositories for code exploration, learning, and API tracking. Includes smart features for token-efficient code reviews.

## Core Capabilities

### 📚 GitHub Repository Knowledge Base
1. **Repository Management** - Add, tag, and organize GitHub repositories
2. **Discovery** - Search GitHub and find related repositories
3. **Exploration** - Clone and analyze repository structure
4. **Code Search** - Search for patterns across your knowledge base
5. **Comparison** - Compare how different repos solve similar problems
6. **Change Tracking** - Monitor API changes, breaking changes, and releases

### 🎯 Smart Code Reviews (Token-Optimized)
7. **Known Books Detection** - Auto-detect popular technical books (Clean Code, Refactoring, etc.) already in Claude's training data to avoid wasting 40,000-60,000 tokens per book
8. **Smart PDF Summarization** - Create structured summaries that save 80-90% tokens on repeated reads
9. **Token Cost Transparency** - Every PDF shows estimated token cost before reading

## Persistent Storage

All data is stored in `~/.config/github-kb/`:
- `index.json` - Registry of all repositories with metadata
- `repos/` - Cloned repositories
- `notes/` - Personal notes and PDFs
- `notes/pdf_index.json` - PDF metadata with token estimates
- `notes/*.summary.md` - Token-efficient PDF summaries
- `cache/` - Cached API responses

## Available Commands

> **Command Shortcuts:** Users can optionally install command shortcuts (`kb`, `kb-search`, `kb-explore`, `kb-changes`) by running `./install-commands.sh`. When invoking commands, prefer using the short form if available (e.g., `kb add` instead of `python kb.py add`). Both forms work identically.

### KB Management (`kb` / `kb.py`)

```bash
# Add a repository
python kb.py add facebook/react
python kb.py add https://github.com/facebook/react

# List repositories
python kb.py list
python kb.py list --tag frontend
python kb.py list --status explored

# Tag repositories
python kb.py tag facebook/react frontend ui library

# Add notes
python kb.py note facebook/react "Great hooks implementation"

# Set status (bookmarked, exploring, explored, archived)
python kb.py status facebook/react explored

# Get info
python kb.py info facebook/react
python kb.py stats

# Remove repository
python kb.py remove facebook/react
```

### Change Tracking (`kb_changes.py`)

```bash
# Show latest release and commits
python kb_changes.py latest facebook/react
python kb_changes.py latest facebook/react --detailed  # With change analysis

# Show changelog
python kb_changes.py changelog facebook/react

# Track API changes (detects property renames, function changes, etc.)
python kb_changes.py api-changes facebook/react
python kb_changes.py api-changes facebook/react --pattern "*.ts"

# Compare versions
python kb_changes.py compare facebook/react v17.0.0 v18.0.0

# Watch for updates
python kb_changes.py watch facebook/react

# Check all watched repos for updates
python kb_changes.py updates
python kb_changes.py updates facebook/react  # Check specific repo
```

### Search & Discovery (`kb_search.py`)

```bash
# Search GitHub
python kb_search.py github "react state management" --stars ">1000" --language typescript

# Find related repositories
python kb_search.py related facebook/react

# Search code in your KB
python kb_search.py code "useEffect" --tag frontend
python kb_search.py code "handleError" --repo facebook/react

# Compare implementations
python kb_search.py compare facebook/react preactjs/preact "virtual dom"
```

### Repository Exploration (`kb_explore.py`)

```bash
# Clone repository
python kb_explore.py clone facebook/react
python kb_explore.py clone facebook/react --depth 1  # shallow clone

# Sync (pull) repository
python kb_explore.py sync facebook/react

# Analyze structure
python kb_explore.py analyze facebook/react

# Show directory tree
python kb_explore.py tree facebook/react --depth 3

# View README
python kb_explore.py readme facebook/react

# Find documentation
python kb_explore.py docs facebook/react

# Find entry points
python kb_explore.py entry-points facebook/react

# Find tests
python kb_explore.py find-tests facebook/react
```

### PDF Management (`kb_pdf.py`)

```bash
# Add PDF from local file
python kb_pdf.py add ~/Documents/react-internals.pdf --title "React Internals Guide" --tags react architecture

# Add PDF from cloned repository
python kb_pdf.py scan-repo facebook/react  # Find PDFs in repo
python kb_pdf.py add ~/.config/github-kb/repos/facebook__react/docs/Architecture.pdf --source facebook/react

# Remove PDF from knowledge base (original file not affected)
python kb_pdf.py remove react-internals.pdf

# List all PDFs
python kb_pdf.py list
python kb_pdf.py list --tag architecture

# Get PDF info (shows token estimate)
python kb_pdf.py info react-internals.pdf

# Search PDFs by title/tags
python kb_pdf.py search "react"

# Create token-efficient summary
python kb_pdf.py summarize react-internals.pdf

# Tag PDFs for organization
python kb_pdf.py tag react-internals.pdf frontend performance
```

### Known Books Detection (`kb_books.py`)

**Smart Token Management**: Automatically detects when PDFs are popular technical books already in Claude's training data, preventing token waste.

```bash
# List all known books
python kb_books.py list

# Search for a book
python kb_books.py search "clean code"
python kb_books.py search "refactoring"

# Check if a book is known (before adding PDF)
python kb_books.py check "Clean Code by Robert Martin"

# View curated combinations
python kb_books.py combos

# Show combination details with ready-to-use prompts
python kb_books.py combo clean-code-fundamentals
python kb_books.py combo java-mastery
python kb_books.py combo software-architecture
python kb_books.py combo craftsmanship
```

**Currently Known Books**: Clean Code, Refactoring, Design Patterns, Clean Architecture, Effective Java, Effective Python, The Pragmatic Programmer, Domain-Driven Design

## Workflow Instructions for Claude

### When the user wants to add a repository:

1. Use `kb.py add <repo>` to add it to the knowledge base
2. Show the summary and metadata returned
3. Suggest related repositories they might want to add using `kb_search.py related <repo>`
4. Recommend next steps: cloning, tagging, or adding notes

Example:
```
User: "Add the fastify repo to my knowledge base"

Steps:
1. Run: kb add fastify/fastify
2. Show the repository summary, stars, language
3. Run: kb-search related fastify/fastify --limit 5
4. Suggest: "I've added Fastify. You might also want to add Express, Koa, or Hapi as related frameworks."
```

### When the user wants to find repositories:

1. Use `kb_search.py github <query>` with appropriate filters
2. Present the results with stars, language, and descriptions
3. Highlight any repos already in their KB
4. Offer to add promising ones

Example:
```
User: "Find me some good GitHub repos for rate limiting in Node.js"

Steps:
1. Run: kb-search github "rate limiting nodejs" --stars ">500"
2. Present top results with context
3. Ask: "Would you like to add any of these to your knowledge base?"
```

### When the user wants to explore a repository:

1. First check if it's in the KB, if not suggest adding it
2. Clone if not already cloned: `kb_explore.py clone <repo>`
3. Analyze structure: `kb_explore.py analyze <repo>`
4. Show README: `kb_explore.py readme <repo>`
5. Find key files: `kb_explore.py entry-points <repo>` and `kb_explore.py docs <repo>`

Example:
```
User: "Help me understand the architecture of the react repo"

Steps:
1. Check if react is in KB, if not: kb add facebook/react
2. Clone if needed: kb-explore clone facebook/react
3. Run: kb-explore analyze facebook/react
4. Run: kb-explore tree facebook/react --depth 2
5. Run: kb-explore readme facebook/react
6. Explain the structure based on the output
7. Suggest: kb status facebook/react exploring
```

### When the user wants to search their KB:

1. Use `kb_search.py code <pattern>` with appropriate filters
2. Show code snippets from matching repositories
3. Provide context about which repos matched and why

Example:
```
User: "What repos in my KB handle error handling? Show me examples"

Steps:
1. Run: python kb_search.py code "error|Error|handleError" --tag backend
2. Present the code snippets with file paths
3. Summarize the different approaches found
```

### When the user wants to compare implementations:

1. Ensure both repos are cloned
2. Use `kb_search.py compare <repo1> <repo2> <pattern>`
3. Analyze and explain the differences

Example:
```
User: "Compare how Express and Fastify handle middleware"

Steps:
1. Check if both are in KB and cloned
2. Run: python kb_search.py compare express fastify "middleware"
3. Show code from both repos
4. Explain the architectural differences
```

### When the user wants to see their collection:

1. Use `kb.py list` with appropriate filters
2. Show the organized list
3. Offer to explore specific repos or categories

Example:
```
User: "Show me all my frontend repos"

Steps:
1. Run: python kb.py list --tag frontend
2. Display the results
3. Ask: "Would you like to explore any of these in detail?"
```

### When the user wants to track changes or updates:

1. Use `kb_changes.py latest <repo>` to show recent releases and commits
2. Add `--detailed` for automatic change analysis (breaking changes, API changes, etc.)
3. Use `kb_changes.py api-changes` to detect property renames and API modifications
4. Use `kb_changes.py watch` to track repositories for future updates

Example:
```
User: "What's new in React?"

Steps:
1. Run: kb-changes latest facebook/react --detailed
2. Show the latest release with analysis
3. Highlight breaking changes, new features, and API changes
4. Note any naming convention changes (e.g., camelCase to snake_case)
```

Example:
```
User: "Has the API changed in version 18?"

Steps:
1. Run: python kb_changes.py compare facebook/react v17.0.0 v18.0.0
2. Run: python kb_changes.py api-changes facebook/react
3. Show detected API changes including property renames
4. Explain the impact of changes
```

Example:
```
User: "Keep me updated on Next.js changes"

Steps:
1. Run: python kb_changes.py watch vercel/next.js
2. Confirm watching
3. Later: python kb_changes.py updates
4. Show any new releases or commits
```

## Best Practices for Claude

1. **Be conversational** - Don't just run commands, explain what you're doing and why
2. **Be helpful** - Suggest next steps and related actions
3. **Be efficient** - Run multiple commands in sequence when it makes sense
4. **Handle errors gracefully** - If a repo isn't cloned, offer to clone it
5. **Suggest organization** - Recommend tags, status updates, and notes
6. **Make connections** - Point out related repos and patterns
7. **Educate** - Explain what you find in the repositories

## GitHub API Rate Limits

- **Without token**: 60 requests/hour
- **With GITHUB_TOKEN**: 5000 requests/hour

If rate limited, inform the user and suggest setting GITHUB_TOKEN:
```bash
export GITHUB_TOKEN=your_github_token_here
```

## Common User Intents and Responses

| User Says | What to Do |
|-----------|-----------|
| "Add [repo] to my KB" | `kb.py add`, then suggest related repos |
| "Find repos for [topic]" | `kb_search.py github` with appropriate filters |
| "What's in my KB?" | `kb.py list` or `kb.py stats` |
| "Explore [repo]" | Clone (if needed), analyze, show structure |
| "How does [repo] handle [topic]?" | Clone (if needed), search code for topic |
| "Compare [repo1] and [repo2]" | Ensure both cloned, use compare command |
| "Search my repos for [pattern]" | `kb_search.py code` |
| "What else should I add?" | Suggest based on existing repos and their tags |
| "Show my [tag] repos" | `kb.py list --tag` |
| "What's new in [repo]?" | `kb_changes.py latest` with detailed analysis |
| "Has [repo] been updated?" | `kb_changes.py updates` or check latest changes |
| "What changed in version X?" | `kb_changes.py compare` between versions |
| "Show me breaking changes" | `kb_changes.py latest --detailed`, highlight breaking changes |
| "Track API changes" | `kb_changes.py api-changes` to detect renames and modifications |
| "Watch [repo] for updates" | `kb_changes.py watch` to track future changes |

## Error Handling

- If KB not initialized: Scripts will auto-initialize on first use
- If repo not in KB: Suggest adding it first
- If repo not cloned: Offer to clone it
- If API rate limited: Suggest using GITHUB_TOKEN
- If command fails: Explain the error and suggest fixes

## Tips for Effective Use

1. **Start with discovery** - Search GitHub first, then add interesting repos
2. **Tag consistently** - Use tags like "frontend", "backend", "database", "auth", etc.
3. **Clone selectively** - Only clone repos you want to explore deeply
4. **Use shallow clones** - For large repos, use `--depth 1` to save space
5. **Keep notes** - Add context about why you added a repo and what you learned
6. **Track status** - Update status as you progress through exploration
7. **Compare similar repos** - Learn different approaches to the same problems

## Example Conversations

### Example 1: Adding and Exploring

```
User: Add the Next.js repo
Claude: [Runs kb.py add vercel/next.js]
        Added Next.js! It's a React framework with 120k+ stars.
        Related repos you might want to add: remix-run/remix, gatsbyjs/gatsby
        Want me to clone and explore it?

User: Yes, explore it
Claude: [Runs kb_explore.py clone vercel/next.js]
        [Runs kb_explore.py analyze vercel/next.js]
        Next.js has a well-organized monorepo structure...
        [Explains the architecture]
        I've set the status to 'exploring'. Want me to find the entry points?
```

### Example 2: Research and Discovery

```
User: I need to implement auth in my Node.js app. Find me some good auth libraries.
Claude: [Runs kb_search.py github "nodejs authentication" --stars ">2000"]
        Found several excellent auth libraries:
        1. passport (23k stars) - Simple authentication middleware
        2. jsonwebtoken (17k stars) - JWT implementation
        3. bcrypt (6k stars) - Password hashing
        Would you like to add any of these to your KB?

User: Add passport
Claude: [Runs kb.py add jaredhanson/passport]
        [Runs kb_search.py related jaredhanson/passport]
        Added passport! Also found 200+ passport strategy plugins.
        Popular ones: passport-local, passport-google-oauth20, passport-jwt
        Want to add any of these?
```

### Example 3: Code Search and Comparison

```
User: How do frameworks handle middleware? Search my KB
Claude: [Runs kb_search.py code "middleware|use\(" --tag backend]
        Found middleware implementations in 4 repos:

        Express: Uses .use() method with simple function composition
        Fastify: Uses plugin system with encapsulation
        Koa: Uses async/await with context object

        [Shows code snippets]

        Each has a different approach. Want me to do a detailed comparison?

User: Compare Express and Fastify
Claude: [Runs kb_search.py compare express fastify "middleware"]
        [Shows side-by-side code]

        Key differences:
        - Express: Synchronous by default, error handling via next()
        - Fastify: Async-first, uses plugin encapsulation
        - Fastify is generally faster due to schema-based validation
```

### Example 4: Adding PDFs with Smart Detection

```
User: I downloaded the Clean Code PDF. Can I add it to my knowledge base?
Claude: Let me check if that's a known book first...
        [Runs kb_books.py check "Clean Code"]

        ⚠️  TOKEN ALERT!

        Clean Code by Robert C. Martin is already in my training data!
        Adding the PDF would waste ~45,000 tokens.

        Instead, you can ask me directly:
        - "Summarize the main principles from Clean Code by Robert Martin"
        - "Review this code using Clean Code principles"
        - "Explain the naming conventions from Clean Code"

        Want to see curated combinations? Try:
        kb-books combo clean-code-fundamentals

User: Show me the clean code fundamentals combination
Claude: [Runs kb_books.py combo clean-code-fundamentals]

        📦 Clean Code Fundamentals
        Essential books for writing clean, maintainable code

        📚 Included Books:
        ✅ Clean Code
        ✅ Refactoring
        ✅ Design Patterns
        ✅ Clean Architecture

        📖 Learning Path:
        1. Start with Clean Code - learn the basics
        2. Study Refactoring - learn to improve existing code
        3. Master Design Patterns - learn reusable solutions
        4. Apply Clean Architecture - learn system-level organization

        🎯 Ready-to-use prompt:
        "Review this code using principles from Clean Code, Refactoring,
         Design Patterns, and Clean Architecture"

User: Review my authentication code using those principles
Claude: [Reviews code using Clean Code, Refactoring, Design Patterns, and
        Clean Architecture principles from training data - no PDF needed!]

        Based on these four books:

        Clean Code perspective:
        - Functions are too long (should be 5-10 lines)
        - Variable names like 'usr' should be 'user'

        Refactoring perspective:
        - Extract Method: auth logic should be separate function
        - Replace Conditional with Polymorphism for auth strategies

        Design Patterns perspective:
        - Strategy pattern for different auth methods
        - Factory pattern for creating auth handlers

        Clean Architecture perspective:
        - Auth logic mixed with infrastructure
        - Should be in use case layer, not controller
```

### Example 5: PDF Management for Research Papers

```
User: I have a research paper on React Fiber architecture. Can I add it?
Claude: [Runs kb_books.py check "React Fiber Architecture"]

        ✅ 'React Fiber Architecture' is not a known book.
        You can safely add this PDF to your knowledge base.

        [User proceeds]

User: Add the PDF
Claude: [Runs kb_pdf.py add ~/Downloads/fiber-arch.pdf --title "React Fiber Architecture"]

        ✓ Added PDF to knowledge base
        Title: React Fiber Architecture
        Size: 125.34 KB
        Estimated pages: ~2
        Estimated tokens: ~18,750

        ⚠️  Large PDF detected!
        Reading this entire PDF will consume ~18,750 tokens

        Consider creating a summary first:
          kb-pdf summarize fiber-arch.pdf

User: Create the summary
Claude: [Runs kb_pdf.py summarize fiber-arch.pdf]
        [Creates structured summary with sections]

        ✓ Created summary: fiber-arch.summary.md
        Summary tokens: ~1,850 (90% savings!)

        Now when you ask questions about Fiber, I'll read the summary
        instead of the full PDF - much more efficient!
```

### When to Use PDFs vs Known Books

**Use PDF**:
- Research papers
- Internal documentation
- Unpublished content
- Niche technical documents
- Books NOT in Claude's training data

**Use Known Books Feature**:
- Popular technical books (Clean Code, Refactoring, etc.)
- Gang of Four Design Patterns
- Effective Java, Pragmatic Programmer
- Books published before 2024
- Standard computer science texts

**Workflow**: Always run `kb-books check "<title>"` before adding a PDF to avoid token waste.

## Extending the Knowledge Base

As you use this skill, consider:

- **Creating categories** - Organize by topic, language, or use case
- **Building learning paths** - Track related repos for learning a topic
- **Documenting patterns** - Note common patterns across repos
- **Sharing insights** - Export your notes and key findings

## Script Locations

All scripts are in the skill's `scripts/` directory:
- `scripts/kb.py` - Main management script
- `scripts/kb_search.py` - Search and discovery
- `scripts/kb_explore.py` - Repository exploration
- `scripts/kb_changes.py` - Change tracking and analysis
- `scripts/kb_pdf.py` - PDF management with smart token optimization
- `scripts/kb_books.py` - Known books detection and prompt generation
- `scripts/known_books.json` - Database of popular technical books

Run scripts with Python 3.7+. They have no external dependencies except Git.

## Additional Resources

- `references/workflows.md` - Common workflow examples
- `references/github-api.md` - GitHub API reference and optimization
- `references/change-tracking.md` - Detailed change tracking workflows

---

**Remember**: This skill is about building knowledge, not just collecting repos. Help the user learn from the code, understand patterns, and make informed decisions.
