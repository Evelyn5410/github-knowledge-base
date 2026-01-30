# Command Reference

Quick reference for all GitHub Knowledge Base commands.

## Installation

After installing the skill, set up the commands:

```bash
./install-commands.sh
source ~/.bashrc  # or ~/.zshrc, or restart terminal
```

This adds four commands to your PATH:
- `kb` - Repository management
- `kb-search` - Search & discovery
- `kb-explore` - Repository exploration
- `kb-changes` - Change tracking

## Repository Management (`kb`)

```bash
# Add repository
kb add facebook/react
kb add https://github.com/facebook/react

# List repositories
kb list
kb list --tag frontend
kb list --status explored

# Tag repositories
kb tag facebook/react frontend ui library

# Add notes
kb note facebook/react "Great hooks implementation"

# Set status
kb status facebook/react explored

# Get info
kb info facebook/react
kb stats

# Remove repository
kb remove facebook/react
```

## Search & Discovery (`kb-search`)

```bash
# Search GitHub
kb-search github "react state management"
kb-search github "nodejs cli" --stars ">1000" --language typescript

# Find related repos
kb-search related facebook/react
kb-search related facebook/react --limit 10

# Search code in your KB
kb-search code "useEffect"
kb-search code "useEffect" --tag frontend
kb-search code "handleError" --repo facebook/react

# Compare implementations
kb-search compare facebook/react preactjs/preact "virtual dom"
```

## Repository Exploration (`kb-explore`)

```bash
# Clone repository
kb-explore clone facebook/react
kb-explore clone facebook/react --depth 1  # shallow clone

# Sync (pull updates)
kb-explore sync facebook/react

# Analyze structure
kb-explore analyze facebook/react

# Show directory tree
kb-explore tree facebook/react
kb-explore tree facebook/react --depth 3

# View README
kb-explore readme facebook/react

# Find documentation
kb-explore docs facebook/react

# Find entry points
kb-explore entry-points facebook/react

# Find tests
kb-explore find-tests facebook/react
```

## Change Tracking (`kb-changes`)

```bash
# Show latest changes
kb-changes latest facebook/react
kb-changes latest facebook/react --detailed

# View changelog
kb-changes changelog facebook/react
kb-changes changelog facebook/react --lines 200

# Track API changes
kb-changes api-changes anthropics/anthropic-sdk-typescript
kb-changes api-changes facebook/react --pattern "*.ts"

# Compare versions
kb-changes compare facebook/react v17.0.0 v18.0.0

# Watch for updates
kb-changes watch facebook/react

# Check all watched repos
kb-changes updates
kb-changes updates facebook/react  # specific repo
```

## Common Workflows

### Quick Start

```bash
# Add and explore a repo
kb add fastify/fastify
kb-explore clone fastify/fastify
kb-explore analyze fastify/fastify

# Tag it
kb tag fastify/fastify nodejs backend framework

# Track changes
kb-changes watch fastify/fastify
```

### Research a Topic

```bash
# Search GitHub
kb-search github "graphql server" --stars ">5000"

# Add promising ones
kb add graphql/graphql-js
kb add apollographql/apollo-server

# Tag for organization
kb tag graphql/graphql-js graphql backend
kb tag apollographql/apollo-server graphql backend

# Explore
kb-explore clone graphql/graphql-js
kb-explore analyze graphql/graphql-js
```

### Monitor Dependencies

```bash
# Watch your key dependencies
kb-changes watch vercel/next.js
kb-changes watch tailwindlabs/tailwindcss
kb-changes watch prisma/prisma

# Weekly check
kb-changes updates
```

### Track API Changes

```bash
# Before upgrading
kb-changes latest anthropics/anthropic-sdk-typescript --detailed
kb-changes api-changes anthropics/anthropic-sdk-typescript
kb-changes compare anthropics/anthropic-sdk-typescript v0.9.0 v0.10.0
```

### Search Your Collection

```bash
# Find patterns
kb-search code "error handling" --tag backend
kb-search code "useEffect" --repo facebook/react

# Compare approaches
kb-search compare express fastify "middleware"
```

## Tips

1. **Use tab completion** - Most shells support tab completion for commands
2. **Combine commands** - Chain commands with `&&` for workflows
3. **Create aliases** - Add personal shortcuts in your shell config
4. **Use tags consistently** - Helps filter and organize your KB

## Examples with Shortcuts

Instead of:
```bash
python kb.py add facebook/react
python kb_explore.py clone facebook/react
python kb_changes.py latest facebook/react --detailed
```

Now just:
```bash
kb add facebook/react
kb-explore clone facebook/react
kb-changes latest facebook/react --detailed
```

Much cleaner! 🎉

## Shell Aliases (Optional)

For even shorter commands, add to your shell config:

```bash
# ~/.bashrc or ~/.zshrc
alias kba='kb add'
alias kbl='kb list'
alias kbs='kb-search'
alias kbe='kb-explore'
alias kbc='kb-changes'
```

Then use:
```bash
kba facebook/react      # kb add
kbl --tag frontend      # kb list
kbs github "nodejs"     # kb-search
kbe clone react         # kb-explore
kbc latest react        # kb-changes
```

## Troubleshooting

### Commands not found

Make sure you ran:
```bash
./install-commands.sh
source ~/.bashrc  # or your shell config
```

Or manually add to PATH:
```bash
export PATH="/path/to/github-knowledge-base/bin:$PATH"
```

### Permission denied

Make scripts executable:
```bash
chmod +x bin/*
```

### Wrong Python version

Commands use `python3` by default. If needed, edit the wrapper scripts in `bin/` to use a specific Python version.
