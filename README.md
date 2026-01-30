# GitHub Knowledge Base Skill

A **token-optimized** Claude Code skill for building and maintaining a personal knowledge base of GitHub repositories and technical documents.

---

## 💭 Why This Skill Exists

This started as a simple, personal need: I kept visiting the same GitHub repositories and noticed Google's GenAI documentation wasn't always up-to-date with the latest API changes. I found myself manually checking for updates every time, which was frustrating.

So I built a tool to track API changes across repositories I frequently reference.

Then I realized: *"If I'm already exploring these repos, why not use them for code reviews?"* I could reference well-known projects to validate patterns and best practices.

That led to: *"What about technical books for code reviews?"* - I added PDF support to reference books like Clean Code and Refactoring during reviews.

Then came the lightbulb moment: *"Wait... Claude already knows these books!"* These popular technical books are in Claude's training data. Reading the PDFs wastes 40,000+ tokens per book - and more importantly, wastes computational resources and energy.

What started as a simple API tracking tool evolved into something bigger: a knowledge base that helps you explore code **efficiently** - both in terms of your time and our planet's resources. Every token saved is energy not consumed, computation not wasted.

If this helps you learn from code while being mindful of resource consumption, that makes me happy. 🌱

---

## What This Skill Does

### 📚 GitHub Repository Knowledge Base
- **Discover** repositories based on topics and keywords
- **Track Changes** - Monitor API changes, breaking changes, and releases
- **Explore** repository structure and documentation
- **Search** code across your saved repositories
- **Compare** implementations between different repos
- **Manage** a persistent collection with tags and notes
- **Learn** from open source code systematically

### 🎯 Smart Code Reviews with Token Optimization
- **Known Books Detection** - Auto-detect popular technical books (Clean Code, Refactoring, Design Patterns, etc.) already in Claude's training data - saves 40K-60K tokens per book
- **Smart PDF Summarization** - Create structured summaries that save 80-90% tokens on repeated reads
- **Token Cost Transparency** - See estimated token cost before reading any PDF
- **Computational Efficiency** - Reduce unnecessary processing and environmental impact

## 🌟 What Makes This Different

### 1. Built for Exploration AND Efficiency
**Problem**: Reading large PDFs and technical books repeatedly wastes hundreds of thousands of tokens.

**Solution**:
- **Structured summaries**: 80-90% token reduction on subsequent reads
- **Known books database**: 8 popular technical books (Clean Code, Refactoring, etc.) already in Claude's training data - skip the PDF entirely!
- **Break-even point**: After just 2 uses, summaries save massive tokens

**Example**:
```
Full PDF reading (10 times): 450,000 tokens
With summaries (10 times): 50,000 tokens
Savings: 400,000 tokens (89%)
```

### 2. Smart Detection
- Automatically warns when you try to add a PDF of a known book
- Provides ready-to-use prompts instead of wasting 40K+ tokens
- Currently detects: Clean Code, Refactoring, Design Patterns, Clean Architecture, Effective Java, Effective Python, Pragmatic Programmer, Domain-Driven Design

### 3. Environmental Efficiency
- Reduces computational waste from redundant processing
- Token-aware operations minimize unnecessary API calls
- Long-term ROI: 10x usage = 80% cumulative savings

## Use Cases

### 🔍 Code Review & Quality Assurance

Review code against best practices from established projects:

```bash
# Build reference knowledge base
kb add passport/passport
kb add auth0/node-jsonwebtoken

# Search for patterns during review
kb-search code "passport.*strategy" --repo passport/passport
kb-search compare passport/passport auth0/node-jsonwebtoken "authentication"

# Check for recent security fixes
kb-changes latest passport/passport --detailed
```

### 📚 Learning New Technologies

Study frameworks systematically:

```bash
# Add and explore GraphQL ecosystem
kb add graphql/graphql-js
kb add apollographql/apollo-server

kb-explore clone graphql/graphql-js
kb-explore analyze graphql/graphql-js
kb-search code "resolver|schema" --tag graphql
```

### ⚖️ Framework Comparison

Make informed technology choices:

```bash
# Compare Express vs Fastify
kb add expressjs/express
kb add fastify/fastify

kb-search compare expressjs/express fastify/fastify "middleware"
kb-search compare expressjs/express fastify/fastify "performance"
kb-changes latest expressjs/express --detailed
```

### 🔄 Dependency Updates

Plan upgrades with confidence:

```bash
# Upgrading React 17 → 18
kb add facebook/react
kb-changes compare facebook/react v17.0.0 v18.0.0
kb-changes latest facebook/react --detailed  # Shows breaking changes
kb-search code "createRoot|useId" --repo facebook/react
```

### 🔒 Security Auditing

Audit application security:

```bash
# Add security references
kb add OWASP/CheatSheetSeries
kb add helmetjs/helmet

kb-search code "sanitize|csrf|xss" --tag security
kb-changes latest helmetjs/helmet --detailed
```

### 🚀 API Design Research

Design better APIs:

```bash
# Study well-designed APIs
kb add stripe/stripe-node
kb add twilio/twilio-node

kb-search code "pagination|error.*response" --tag api-design
kb-search compare stripe/stripe-node twilio/twilio-node "error"
```

### 🎯 Building Expertise

Become an expert in your domain:

```bash
# Node.js backend expertise
kb add nodejs/node
kb add expressjs/express
kb add prisma/prisma
kb add goldbergyoni/nodebestpractices

kb tag expressjs/express nodejs framework
kb-changes watch nodejs/node  # Track updates
kb-changes updates  # Weekly review
```

### 📊 Architecture Study

Learn architectural patterns:

```bash
# Microservices patterns
kb add nestjs/nest
kb add moleculerjs/moleculer

kb-search code "service.*discovery|event.*bus" --tag microservices
kb-explore tree nestjs/nest --depth 3
```

## Installation

### 1. Install the Skill

```bash
claude skills add ./github-knowledge-base
```

Or from the skill directory:

```bash
cd github-knowledge-base
claude skills add .
```

### 2. Install Commands (Recommended)

For convenient short commands like `kb add` instead of `python kb.py add`:

```bash
cd github-knowledge-base
./install-commands.sh
source ~/.bashrc  # or ~/.zshrc, or restart terminal
```

This adds:
- `kb` - Repository management
- `kb-search` - Search & discovery
- `kb-explore` - Repository exploration
- `kb-changes` - Change tracking

## Quick Start

### First Steps

```bash
# 1. Check your KB (will be empty initially)
kb list

# 2. Add your first repository
kb add facebook/react

# 3. Tag and organize
kb tag facebook/react frontend library ui

# 4. View repository info
kb info facebook/react

# 5. See your collection
kb list
kb stats
```

### Complete Example Workflow

**Scenario: Learning React best practices**

```bash
# Step 1: Build your knowledge base
kb add facebook/react
kb add vercel/next.js
kb add remix-run/remix

# Step 2: Organize with tags
kb tag facebook/react react framework frontend
kb tag vercel/next.js react framework ssr
kb tag remix-run/remix react framework fullstack

# Step 3: Clone for deep exploration
kb-explore clone facebook/react
kb-explore analyze facebook/react

# Step 4: Study specific patterns
kb-search code "useState|useEffect" --tag react
kb-search code "getServerSideProps" --repo vercel/next.js

# Step 5: Compare approaches
kb-search compare vercel/next.js remix-run/remix "data loading"

# Step 6: Track for updates
kb-changes watch facebook/react
kb-changes watch vercel/next.js

# Step 7: Check what's new
kb-changes latest facebook/react --detailed
```

### Using with Claude Code

Ask Claude naturally - the skill activates automatically:

```
You: "Add the React repository to my knowledge base"
Claude: [Runs: kb add facebook/react]
       ✓ Added 'facebook/react' to knowledge base
       Summary: A declarative, efficient JavaScript library...

You: "What's new in the latest release?"
Claude: [Runs: kb-changes latest facebook/react --detailed]
       📦 Latest Release: v18.2.0
       ⚠️ Breaking Changes: ...

You: "Find authentication libraries for Node.js"
Claude: [Runs: kb-search github "nodejs authentication" --stars ">1000"]
       Found 10 repositories:
       1. passport/passport (22k ⭐)
       ...
```

### Direct Terminal Usage

```bash
# Repository management
kb add expressjs/express
kb list --tag nodejs
kb info expressjs/express

# Search and discover
kb-search github "rate limiting nodejs" --stars ">500"
kb-search related expressjs/express

# Explore repositories
kb-explore clone expressjs/express
kb-explore analyze expressjs/express
kb-explore readme expressjs/express

# Track changes
kb-changes latest expressjs/express --detailed
kb-changes api-changes expressjs/express
kb-changes watch expressjs/express

# Check all watched repos
kb-changes updates
```

## Features

### 1. Repository Management

- Add repositories with full metadata (stars, language, topics)
- Tag and categorize your collection
- Track exploration status (bookmarked → exploring → explored)
- Add personal notes about each repo
- Persistent storage across sessions

### 2. Discovery & Search

- Search GitHub for repositories by topic, stars, language
- Find repositories related to ones you've added
- Smart suggestions based on your collection

### 3. Code Exploration

- Clone repositories for local analysis
- Analyze structure and identify key files
- Find entry points, tests, and documentation
- Display README and docs without opening files
- Show directory tree structure

### 4. Code Search

- Search for patterns across all your repos
- Filter searches by tag or specific repo
- Compare implementations between repos
- Find examples of specific techniques

### 5. Change Tracking

- Track latest releases and commits
- Detect breaking changes automatically
- Identify API changes and property renames (e.g., camelCase → snake_case)
- Compare versions and show differences
- Watch repositories for updates
- Analyze changelogs for important changes

### 6. PDF Management (NEW!)

- **Smart Token Management** - Estimates token cost before reading
- **Repository PDFs** - Discover and index PDFs from cloned repos
- **Local Storage** - Store PDFs in `~/.config/github-kb/notes/`
- **Intelligent Summaries** - Create summaries to save 80%+ tokens
- **Search & Organization** - Tag and search PDFs by topic
- **Cost Transparency** - Always shows token estimates before reading

## 📄 PDF Knowledge Base

### Token-Aware PDF Management

One of the most important features of this skill is **smart token management for PDFs**. Reading large PDFs can consume significant tokens, so the skill provides transparency and tools to minimize waste.

### Token Estimation Methodology

**How we estimate tokens:**
```
File Size (KB) × 150 = Estimated Tokens
Pages ≈ File Size / 50KB
Tokens per Page ≈ 500
```

**Example estimates:**
- 10-page paper (500 KB) → ~7,500 tokens
- 30-page guide (1.5 MB) → ~22,500 tokens
- 300-page book (15 MB) → ~225,000 tokens

**Why this matters:**
- Claude has a 200K token context window
- Reading a large book could consume your entire context!
- Summaries reduce token usage by 80-90%

### Smart Token-Saving Features

**1. Pre-Read Estimates**
```bash
kb-pdf info research-paper.pdf

# Output shows:
# Estimated tokens: ~18,500
# ⚠️ Large PDF - summary recommended
```

**2. Structured Summaries** (NEW - Enhanced!)
```bash
kb-pdf summarize research-paper.pdf

# Creates intelligent template with:
# - Section-by-section breakdown
# - Topic index for quick lookup
# - Multiple reading strategies
# - Token estimates per section

# Result: ~2,000 token summary (saves ~16,500 tokens!)
# Plus: Can read individual sections (~500 tokens each)
```

**3. Repository PDF Discovery**
```bash
kb-pdf scan-repo facebook/react

# Shows all PDFs in repo with token estimates
# Lets you selectively add important ones
```

### PDF Commands

```bash
# Add PDF from local file
kb-pdf add ~/Documents/react-internals.pdf --title "React Internals Guide" --tags react architecture

# Add PDF from cloned repository
kb-pdf scan-repo facebook/react  # Find PDFs
kb-pdf add ~/.config/github-kb/repos/facebook__react/docs/Architecture.pdf --source facebook/react

# Remove PDF from knowledge base
kb-pdf remove react-internals.pdf  # Original file not affected

# List all PDFs
kb-pdf list
kb-pdf list --tag architecture

# Get detailed info (with token estimate)
kb-pdf info react-internals.pdf

# Search PDFs
kb-pdf search "react"

# Create summary (token-saving!)
kb-pdf summarize react-internals.pdf

# Tag PDFs
kb-pdf tag react-internals.pdf frontend performance
```

### 🎯 Smart Book Detection (Avoid Token Waste!)

**The Problem**: Many popular technical books (Clean Code, Refactoring, Design Patterns, etc.) are already in Claude's training data. Reading the PDF of these books wastes thousands of tokens unnecessarily.

**The Solution**: The skill automatically detects when you're adding a known book and provides ready-to-use prompts instead.

#### Known Books Detection

When you try to add a known book, you'll get a warning (make sure to use a proper title):

```bash
kb-pdf add ~/Downloads/clean-code.pdf --title "Clean Code by Robert Martin"

# Output:
⚠️  TOKEN ALERT!

📚 Clean Code: A Handbook of Agile Software Craftsmanship
   Author: Robert C. Martin (2008)

✅ This book is already in Claude's training data!
   Reading the PDF will waste ~45,000 tokens.

💡 Instead, use these ready-to-use prompts:

   summary:
   "Summarize the main principles from Clean Code by Robert Martin"

   apply_to_code:
   "Review this code using Clean Code principles and suggest improvements"

   specific_topic:
   "Explain the [TOPIC] principles from Clean Code with examples"

💰 Token Savings: Skip the PDF and use the prompts above!

🔍 For more info: kb-books search "Clean Code"
📦 See combinations: kb-books combos
```

#### Known Books Commands

```bash
# List all known books
kb-books list

# Search for a book
kb-books search "clean code"
kb-books search "refactoring"

# Check if a book is known before adding PDF
kb-books check "Clean Code by Robert Martin"

# View curated combinations
kb-books combos

# Show combination details with prompts
kb-books combo clean-code-fundamentals
kb-books combo java-mastery
kb-books combo software-architecture
```

#### Currently Known Books (8 books)

✅ **Clean Code** - Robert C. Martin (2008)
✅ **Refactoring** - Martin Fowler (2018)
✅ **Design Patterns** - Gang of Four (1994)
✅ **Clean Architecture** - Robert C. Martin (2017)
✅ **Effective Java** - Joshua Bloch (2017)
✅ **Effective Python** - Brett Slatkin (2019)
✅ **The Pragmatic Programmer** - Hunt & Thomas (2019)
✅ **Domain-Driven Design** - Eric Evans (2003)

#### Curated Book Combinations

**1. Clean Code Fundamentals** (`clean-code-fundamentals`)
- Books: Clean Code, Refactoring, Design Patterns, Clean Architecture
- Use: "Review this code using Clean Code, Refactoring, Design Patterns, and Clean Architecture"

**2. Java Best Practices** (`java-mastery`)
- Books: Effective Java, Clean Code, Design Patterns
- Use: "Review this Java code using Effective Java, Clean Code, and Design Patterns principles"

**3. Python Best Practices** (`python-mastery`)
- Books: Effective Python, Clean Code, Design Patterns
- Use: "Review this Python code using Effective Python, Clean Code, and Design Patterns principles"

**4. Software Architecture** (`software-architecture`)
- Books: Clean Architecture, Design Patterns, Domain-Driven Design
- Use: "Design architecture for [SYSTEM] using Clean Architecture, Design Patterns, and DDD"

**5. Software Craftsmanship** (`craftsmanship`)
- Books: Pragmatic Programmer, Clean Code, Refactoring, Clean Architecture
- Use: "Evaluate my development approach using all four craftsmanship books"

#### Token Savings Example

```bash
# ❌ WITHOUT Detection (Wasteful)
kb-pdf add clean-code.pdf           # Adds PDF
Later: "Summarize Clean Code"       # Reads 45,000 tokens

# ✅ WITH Detection (Efficient)
kb-pdf add clean-code.pdf           # Warns + provides prompts
Instead: Use prompt directly        # 0 tokens, instant response!

Token Savings: 45,000 tokens (100%)
```

### Token Usage Examples

**Without Summaries (Token-Heavy):**
```
You: "What do my PDFs say about React Fiber?"

Claude reads:
- react-fiber-architecture.pdf (20,000 tokens)
- react-reconciliation.pdf (15,000 tokens)
- react-performance.pdf (18,000 tokens)

Total: 53,000 tokens consumed! 💸
```

**With Summaries (Token-Efficient):**
```
You: "What do my PDFs say about React Fiber?"

Claude reads summaries:
- react-fiber-architecture.summary.md (1,500 tokens)
- react-reconciliation.summary.md (1,200 tokens)
- react-performance.summary.md (1,800 tokens)

Total: 4,500 tokens (saves 48,500 tokens!) ✅
```

### Structured Summaries: Maximum Token Efficiency

The skill creates **intelligent, structured summaries** that maximize token savings and usability:

#### Summary Structure

```markdown
# Structured Summary: React Fiber Architecture

**Total Pages**: 48 | **Full PDF**: ~18,500 tokens
**This Summary**: ~2,000 tokens | **Savings**: ~16,500 tokens (89%)

## 📋 Document Overview
- Main topic and key takeaway (~200 tokens)
- Quick decision: Is this document relevant?

## 🗂️ Document Structure

### Section 1: Introduction (Pages 1-8, ~3,200 tokens)
**Summary**: Introduces React Fiber as a rewrite...
**Key Concepts**: reconciliation, async rendering
**When to Read**: Understanding fundamentals

### Section 2: Architecture (Pages 9-25, ~6,800 tokens)
**Summary**: Describes Fiber node structure...
**Key Concepts**: work loop, priority queue
**When to Read**: Implementation details

### Section 3: Examples (Pages 26-48, ~8,500 tokens)
**Summary**: Practical code examples...
**When to Read**: Working code needed

## 🔍 Topic Index
| Topic | Sections | Pages | Why Important |
|-------|----------|-------|---------------|
| Reconciliation | 1, 2 | 5-20 | Core algorithm |
| Priority Queue | 2 | 15-18 | Scheduling |
| Code Examples | 3 | 30-45 | Implementation |

## 💡 Reading Strategies
- **Overview only**: Read Document Overview (~200 tokens)
- **Specific topic**: Use Topic Index + read 1 section (~800 tokens)
- **Full understanding**: Read entire summary (~2,000 tokens)
- **Deep dive**: Read full PDF (18,500 tokens)
```

#### Token Savings by Use Case

| Your Need | Read This | Tokens | vs Full PDF |
|-----------|-----------|---------|-------------|
| "Is this relevant?" | Overview | ~200 | 99% saved |
| "Quick reference on X" | Topic Index + 1 section | ~800 | 96% saved |
| "General understanding" | Full summary | ~2,000 | 89% saved |
| "Deep research" | Full PDF | 18,500 | 0% saved |

#### Long-Term ROI

**Investment**: Create summary once (18,500 tokens to read + summarize)

**Returns**: Every future use

| # of Uses | Without Summary | With Summary | Savings |
|-----------|----------------|--------------|---------|
| 1 | 18,500 | 18,500 | 0 |
| 2 | 37,000 | 20,500 | 16,500 (45%) |
| 5 | 92,500 | 26,500 | 66,000 (71%) |
| 10 | 185,000 | 36,500 | 148,500 (80%) |
| 20 | 370,000 | 56,500 | 313,500 (85%) |

**Break-even**: After just 2 uses!

#### Smart Section Reading

Instead of reading entire PDF, read only relevant sections:

```
User: "How does React Fiber handle scheduling?"

Strategy 1 (Wasteful):
→ Read full PDF: 18,500 tokens

Strategy 2 (Smart):
→ Check summary topic index: 0 tokens (already loaded)
→ Find "scheduling" in Section 2
→ Read Section 2 summary: ~300 tokens
→ If need more, read Section 2 only: ~6,800 tokens

Token savings: 11,700 tokens (63%)
```

### Workflow: Adding PDFs from Repository

```bash
# 1. Clone a repository with documentation
kb add facebook/react
kb-explore clone facebook/react

# 2. Discover PDFs in the repo
kb-pdf scan-repo facebook/react

# Output:
# 📚 Found 3 PDF(s) in facebook/react
# 📄 docs/Architecture.pdf
#    Size: 2.4 MB | ~48 pages | ~18,500 tokens
# 📄 docs/Fiber.pdf
#    Size: 1.8 MB | ~36 pages | ~14,000 tokens

# 3. Selectively add important PDFs
kb-pdf add ~/.config/github-kb/repos/facebook__react/docs/Fiber.pdf \
  --source facebook/react \
  --tags react fiber architecture

# 4. Create summary to save tokens
kb-pdf summarize Fiber.pdf

# 5. Ask Claude to complete the summary
# "Please read ~/.config/github-kb/notes/Fiber.pdf and complete
#  the summary at ~/.config/github-kb/notes/Fiber.summary.md"

# 6. Future usage reads summary (saves ~12,000 tokens)
```

### Computational Efficiency: Beyond Token Savings

Structured summaries don't just save tokens - they reduce unnecessary computation:

#### Traditional Approach (Wasteful)
```
User asks 5 questions about a PDF over 1 week:

Day 1: "What's this about?" → Read full PDF (18,500 tokens)
Day 2: "How does X work?" → Read full PDF again (18,500 tokens)
Day 3: "Where's the code?" → Read full PDF again (18,500 tokens)
Day 4: "What about Y?" → Read full PDF again (18,500 tokens)
Day 5: "Summary please" → Read full PDF again (18,500 tokens)

Total: 92,500 tokens
Computational waste: Read same content 5 times
Environmental impact: 5× the energy consumption
```

#### Structured Summary Approach (Efficient)
```
Day 0: Create summary once (18,500 tokens)

Day 1: "What's this about?" → Read overview (200 tokens)
Day 2: "How does X work?" → Read relevant section summary (300 tokens)
Day 3: "Where's the code?" → Check topic index → Section 3 (400 tokens)
Day 4: "What about Y?" → Read Section 2 summary (300 tokens)
Day 5: "Summary please" → Already have it! (0 tokens, point to summary)

Total: 19,700 tokens
Savings: 72,800 tokens (79%)
Computation reduction: Read full content once, reuse compressed version
Environmental benefit: 79% less energy per use
```

#### Benefits

**1. Token Efficiency**
- 79-89% reduction in token usage
- Lower API costs
- More conversation capacity

**2. Computational Efficiency**
- Process document once, not repeatedly
- Faster responses (reading summary vs full PDF)
- Reduced server load

**3. Environmental Impact**
- Less computation = less energy
- Sustainable AI usage
- Responsible resource management

**4. Better User Experience**
- Quick answers from summaries
- Option to deep-dive when needed
- Clear token costs upfront

### Best Practices for Token Efficiency

**1. Always Check Estimates First**
```bash
kb-pdf info document.pdf  # See token cost before reading
```

**2. Create Summaries for Large PDFs**
```bash
# If PDF > 10,000 tokens, create summary
kb-pdf summarize large-document.pdf
```

**3. Use Tags to Find PDFs Without Reading**
```bash
kb-pdf search "architecture"  # Find relevant PDFs
kb-pdf list --tag react       # Filter by topic
```

**4. Selective Reading**
```
# Good: Read specific PDF
"Read the Fiber architecture PDF"

# Wasteful: Read all PDFs
"Read all my React PDFs"  # Could be 100K+ tokens!
```

## Data Storage

All data is stored in `~/.config/github-kb/`:

```
~/.config/github-kb/
├── index.json              # Registry of all repositories
├── repos/                  # Cloned repositories
├── notes/                  # Your notes about repos
│   ├── *.pdf              # Stored PDFs
│   ├── *.summary.md       # PDF summaries (token-efficient!)
│   ├── pdf_index.json     # PDF metadata and token estimates
│   └── owner__repo.md     # Repository notes
├── changes/                # Change tracking data for watched repos
└── cache/                  # Cached data
```

This persists across Claude Code sessions.

## Scripts

The skill includes five Python scripts:

- **kb.py** - Repository management (add, list, tag, note)
- **kb_search.py** - Search GitHub and your KB
- **kb_explore.py** - Clone and explore repositories
- **kb_changes.py** - Track changes, releases, and API modifications
- **kb_pdf.py** - PDF management with smart token optimization

You can run these directly or let Claude handle them conversationally.

## GitHub Token (Optional but Recommended)

Without a token: 60 API requests/hour
With a token: 5,000 API requests/hour

### Setup

1. Create token at https://github.com/settings/tokens
2. Select scope: `public_repo`
3. Export in your shell:

```bash
export GITHUB_TOKEN=ghp_your_token_here
```

Add to `~/.bashrc` or `~/.zshrc` to persist.

## Example Workflows

### Learning a New Framework

```
You: "I want to learn GraphQL. Find me the best repos."
Claude: [Searches, suggests graphql-js, apollo-server, etc.]

You: "Add the top 3"
Claude: [Adds them, tags as 'graphql', 'learning']

You: "Explore the graphql-js repo"
Claude: [Clones, analyzes structure, shows key files]

You: "How does it handle validation?"
Claude: [Searches code, shows examples]
```

### Solving a Problem

```
You: "I need to add rate limiting to my API. Find solutions."
Claude: [Searches GitHub for rate limiting libraries]

You: "Add express-rate-limit"
Claude: [Adds, shows info]

You: "Clone and show me usage examples"
Claude: [Clones, finds tests and examples]

You: "Compare it with node-rate-limiter-flexible"
Claude: [Adds second lib, compares approaches]
```

### Building Expertise

```
You: "Show my backend repos"
Claude: [Lists all repos tagged 'backend']

You: "How do they handle authentication?"
Claude: [Searches for auth patterns across repos, shows examples]

You: "Compare Express and Fastify middleware"
Claude: [Shows side-by-side comparison]
```

## Commands Reference

> **Note:** After running `./install-commands.sh`, you can use short commands like `kb add` instead of `python kb.py add`.

### KB Management

```bash
# Add repository
kb add facebook/react

# List all repos
kb list

# List by tag
kb list --tag frontend

# Tag a repo
kb tag facebook/react frontend ui library

# Add notes
kb note facebook/react "Great hooks implementation"

# Set status
kb status facebook/react explored

# Show details
kb info facebook/react

# Show statistics
kb stats

# Remove repo
kb remove facebook/react
```

<details>
<summary>Using Python directly (without install-commands.sh)</summary>

```bash
python kb.py add facebook/react
python kb.py list
python kb.py tag facebook/react frontend ui library
# etc...
```
</details>

### Search & Discovery

```bash
# Search GitHub
kb-search github "react state" --stars ">1000"

# Find related repos
kb-search related facebook/react

# Search your KB
kb-search code "useEffect" --tag frontend

# Compare repos
kb-search compare express fastify "middleware"
```

### Exploration

```bash
# Clone repository
kb-explore clone facebook/react

# Sync (pull updates)
kb-explore sync facebook/react

# Analyze structure
kb-explore analyze facebook/react

# Show tree
kb-explore tree facebook/react --depth 2

# View README
kb-explore readme facebook/react

# Find docs
kb-explore docs facebook/react

# Find entry points
kb-explore entry-points facebook/react

# Find tests
kb-explore find-tests facebook/react
```

### Change Tracking

```bash
# Show latest changes
kb-changes latest facebook/react
kb-changes latest facebook/react --detailed

# View changelog
kb-changes changelog facebook/react

# Track API changes (detects property renames)
kb-changes api-changes facebook/react
kb-changes api-changes facebook/react --pattern "*.ts"

# Compare versions
kb-changes compare facebook/react v17.0.0 v18.0.0

# Watch for updates
kb-changes watch facebook/react

# Check watched repos
kb-changes updates
```

### PDF Management

```bash
# Add PDF to knowledge base
kb-pdf add ~/Documents/paper.pdf --title "Research Paper" --tags ml research

# Remove PDF from knowledge base
kb-pdf remove paper.pdf

# List PDFs (with token estimates)
kb-pdf list
kb-pdf list --tag architecture

# Get PDF info (shows token cost)
kb-pdf info paper.pdf

# Find PDFs in cloned repository
kb-pdf scan-repo facebook/react

# Create summary (saves 80%+ tokens!)
kb-pdf summarize paper.pdf

# Search PDFs
kb-pdf search "machine learning"

# Tag PDFs
kb-pdf tag paper.pdf ai transformers
```

## Tips

1. **Start with search** - Find repos before adding
2. **Tag consistently** - Use standard tags (frontend, backend, auth, etc.)
3. **Clone selectively** - Only clone what you'll explore
4. **Use shallow clones** - Add `--depth 1` for large repos
5. **Document as you learn** - Add notes immediately
6. **Track progress** - Update status as you explore
7. **Regular reviews** - Check your KB weekly

## Advanced Usage

### Find repositories for a topic
```
You: "Find the best TypeScript testing libraries"
```

### Build a learning path
```
You: "I want to learn microservices. Create a collection."
Claude: [Finds and adds relevant repos, tags them, organizes by difficulty]
```

### Research best practices
```
You: "How do popular repos handle configuration?"
Claude: [Searches across your KB, shows different approaches]
```

### Architecture study
```
You: "Compare monorepo vs single-repo structures"
Claude: [Finds examples, analyzes structure, compares approaches]
```

### Track breaking changes
```
You: "What's new in React 18? Any breaking changes?"
Claude: [Shows latest release with detailed analysis]
       "React 18 introduced:
        - Breaking: Automatic batching for all updates
        - API Change: createRoot replaces render
        - New: Concurrent features and Suspense"
```

### Monitor API changes
```
You: "Track API changes in the Anthropic SDK"
Claude: [Runs api-changes detection]
       "Detected changes:
        - Property renamed: maxTokens → max_tokens
        - Property renamed: stopSequences → stop_sequences
        - Function signature changed: create() now requires model param"
```

### Compare versions
```
You: "What changed between Next.js 13 and 14?"
Claude: [Compares versions, shows commits and file changes]
       "196 commits, major changes in:
        - app/ directory improvements
        - Server Actions stability
        - Turbopack updates"
```

## Troubleshooting

**"Knowledge base is empty"**
→ Add repositories: `python kb.py add owner/repo`

**"Repository not cloned yet"**
→ Clone it: `python kb_explore.py clone owner/repo`

**"API rate limit exceeded"**
→ Set GITHUB_TOKEN environment variable

**"No matches found"**
→ Ensure repo is cloned, try broader search pattern

## Requirements

- Python 3.7+
- Git
- Internet connection (for GitHub API)
- Optional: ripgrep (rg) for faster code search

No Python packages required - uses only standard library!

## File Structure

```
github-knowledge-base/
├── SKILL.md              # Main skill instructions for Claude
├── README.md             # This file
├── SETUP.md              # Installation and setup guide
├── scripts/
│   ├── kb.py            # Repository management
│   ├── kb_search.py     # Search and discovery
│   ├── kb_explore.py    # Repository exploration
│   └── kb_changes.py    # Change tracking and analysis
└── references/
    ├── workflows.md     # Detailed workflow examples
    └── github-api.md    # GitHub API reference
```

## Contributing Ideas

This skill can be extended with:
- Dependency graph visualization
- Automated summarization of repos
- Export to different formats
- Integration with note-taking apps
- Collaborative knowledge bases
- ML-based recommendations

## License

This skill is part of Claude Code and follows its licensing.

## Support

For issues or questions:
- Check the `references/` directory for detailed docs
- Ask Claude Code for help with specific tasks
- Refer to workflow examples in `references/workflows.md`

---

**Happy exploring!** Build your knowledge, one repository at a time.
