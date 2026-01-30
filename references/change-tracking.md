# Change Tracking Workflows

This document provides detailed workflows for tracking changes, updates, and API modifications in your GitHub knowledge base.

## Overview

The `kb_changes.py` script helps you:
- Monitor releases and commits
- Detect breaking changes automatically
- Track API changes including property renames
- Compare versions
- Watch repositories for updates

## Key Features

### 1. Automatic Change Analysis

The script analyzes release notes and changelogs to detect:
- **Breaking changes** - Incompatible API changes
- **Deprecations** - Features marked for removal
- **New features** - Additions to the API
- **Bug fixes** - Problem resolutions
- **API changes** - Method/property modifications
- **Naming changes** - Property renames (e.g., `maxTokens` → `max_tokens`)
- **Performance improvements**
- **Security fixes**

### 2. Property Rename Detection

Automatically detects common naming convention changes:
- `camelCase` → `snake_case`
- `snake_case` → `camelCase`
- Explicit renames in commit messages
- Property name changes in code diffs

### 3. Version Comparison

Compare any two versions using:
- Tags (e.g., `v1.0.0`)
- Branches (e.g., `main`, `develop`)
- Commit SHAs

## Workflow 1: Checking What's New

**Scenario**: You want to know what's new in a repository.

### Steps:

1. **Basic check** - Show latest release and recent commits
   ```bash
   python kb_changes.py latest facebook/react
   ```

   Output:
   ```
   📦 Latest Release
   Version: v18.2.0
   Published: 2023-06-14

   Release Notes:
   - Fix crash in development mode
   - Improve error messages
   ...

   📝 Recent Commits
   1. Fix memory leak in useEffect
   2. Update TypeScript definitions
   ...
   ```

2. **Detailed analysis** - Get automatic change categorization
   ```bash
   python kb_changes.py latest facebook/react --detailed
   ```

   Output:
   ```
   🔍 Change Analysis:

   ⚠️  Breaking Changes:
   • Removed legacy context API
   • createRoot replaces ReactDOM.render

   🔄 Naming/API Changes:
   • maxDuration → max_duration
   • unstable_batchedUpdates removed

   ✨ New Features:
   • useId hook for SSR
   • useDeferredValue for transitions

   🔒 Security:
   • Fixed XSS vulnerability in href sanitization
   ```

### When to Use:

- Before upgrading a dependency
- Learning about new features
- Checking for security updates
- Understanding migration requirements

## Workflow 2: Tracking API Changes

**Scenario**: You need to know if and how the API has changed.

### Steps:

1. **Check for any API modifications**
   ```bash
   python kb_changes.py api-changes anthropics/anthropic-sdk-typescript
   ```

   This analyzes recent commits for:
   - Property additions/removals
   - Function signature changes
   - Naming convention changes
   - Parameter modifications

2. **Focus on specific file types**
   ```bash
   python kb_changes.py api-changes anthropics/anthropic-sdk-typescript --pattern "*.ts"
   ```

   Output:
   ```
   API Change Tracking: anthropics/anthropic-sdk-typescript

   Detected changes in *.ts files:
   • Property renamed
     - max_tokens_to_sample
     + max_tokens

   • Property renamed
     - stop_sequences
     + stop

   • Function signature changed
     - async create(params)
     + async create(params: CreateParams)
   ```

### Real-World Example:

**Tracking Anthropic SDK changes:**

```bash
# Clone if not already cloned
python kb_explore.py clone anthropics/anthropic-sdk-typescript

# Track API changes
python kb_changes.py api-changes anthropics/anthropic-sdk-typescript

# Compare versions
python kb_changes.py compare anthropics/anthropic-sdk-typescript v0.9.0 v0.10.0
```

This helps you:
- Update your code to match new API
- Understand property renames
- Identify breaking changes
- Plan migration strategy

## Workflow 3: Version Comparison

**Scenario**: You're upgrading from one version to another and need to know what changed.

### Steps:

1. **Ensure repository is cloned**
   ```bash
   python kb_explore.py clone nextjs/next.js
   ```

2. **Compare two versions**
   ```bash
   python kb_changes.py compare vercel/next.js v13.0.0 v14.0.0
   ```

   Output:
   ```
   Comparing Versions: vercel/next.js
   v13.0.0 → v14.0.0

   Commits between versions:
   abc1234 Stable Server Actions
   def5678 Turbopack improvements
   ghi9012 App Router enhancements
   ...

   File changes:
   packages/next/src/server/app-render.tsx    | 234 ++++++++---
   packages/next/src/server/config.ts         |  45 ++-
   packages/next/types/index.d.ts             | 128 ++++--
   ```

3. **Check detailed API changes**
   ```bash
   python kb_changes.py api-changes vercel/next.js --pattern "*.d.ts"
   ```

### Use Cases:

- Planning major version upgrades
- Understanding migration requirements
- Reviewing changelog comprehensively
- Identifying affected areas in your code

## Workflow 4: Monitoring Multiple Repositories

**Scenario**: You maintain projects that depend on several libraries and need to stay updated.

### Steps:

1. **Start watching key dependencies**
   ```bash
   python kb_changes.py watch facebook/react
   python kb_changes.py watch vercel/next.js
   python kb_changes.py watch tailwindlabs/tailwindcss
   python kb_changes.py watch prisma/prisma
   ```

   Each command outputs:
   ```
   ✓ Now watching facebook/react for changes
     Latest release: v18.2.0
     Latest commit: a1b2c3d
   ```

2. **Regularly check for updates**
   ```bash
   python kb_changes.py updates
   ```

   Output:
   ```
   Checking 4 watched repositories...

   📦 facebook/react
     ✓ No updates since last check

   📦 vercel/next.js
     🆕 New release: v14.0.0 → v14.1.0
     📝 New commits since last check

   📦 tailwindlabs/tailwindcss
     ✓ No updates since last check

   📦 prisma/prisma
     🆕 New release: v5.5.0 → v5.6.0
   ```

3. **Investigate updates**
   ```bash
   python kb_changes.py latest vercel/next.js --detailed
   python kb_changes.py latest prisma/prisma --detailed
   ```

### Automation Idea:

Create a weekly check script:

```bash
#!/bin/bash
# weekly-updates.sh

echo "=== Weekly Dependency Updates ==="
date

python kb_changes.py updates

echo ""
echo "Run 'python kb_changes.py latest <repo> --detailed' for details"
```

Run with cron:
```cron
0 9 * * MON /path/to/weekly-updates.sh
```

## Workflow 5: Analyzing Changelogs

**Scenario**: A repository has a detailed CHANGELOG and you want to review it.

### Steps:

1. **Ensure repository is cloned**
   ```bash
   python kb_explore.py clone facebook/react
   ```

2. **View changelog**
   ```bash
   python kb_changes.py changelog facebook/react
   ```

   Shows first 100 lines by default, with analysis:
   ```
   CHANGELOG: facebook/react

   ## 18.2.0 (June 14, 2023)

   ### React DOM
   - Fix hydration mismatch...
   ...

   🔍 Changelog Analysis:

   ⚠️  Breaking Changes (3 found)
   • Removed legacy context API
   • createRoot replaces render

   🔄 Naming Changes (5 found)
   • unstable_batchedUpdates → automatic batching
   • maxDuration → max_duration
   ...
   ```

3. **View more lines**
   ```bash
   python kb_changes.py changelog facebook/react --lines 500
   ```

### When to Use:

- Before major upgrades
- Understanding project evolution
- Learning about historical changes
- Researching specific features

## Workflow 6: Detecting Breaking Changes

**Scenario**: You need to upgrade a dependency but want to identify all breaking changes first.

### Complete Analysis:

```bash
REPO="facebook/react"
OLD_VERSION="v17.0.0"
NEW_VERSION="v18.0.0"

echo "=== Comprehensive Breaking Change Analysis ==="

# 1. Show latest release with analysis
echo -e "\n1. Latest Release Analysis:"
python kb_changes.py latest $REPO --detailed | grep -A 20 "Breaking Changes"

# 2. Compare versions
echo -e "\n2. Version Comparison:"
python kb_changes.py compare $REPO $OLD_VERSION $NEW_VERSION

# 3. Check API changes
echo -e "\n3. API Changes:"
python kb_changes.py api-changes $REPO

# 4. Review changelog
echo -e "\n4. Changelog Review:"
python kb_changes.py changelog $REPO | grep -i "breaking\|removed\|deprecated" | head -20
```

This gives you:
- Explicit breaking changes from release notes
- Code-level changes between versions
- API modifications detected in commits
- Historical context from changelog

## Workflow 7: Pre-Upgrade Checklist

**Scenario**: You're about to upgrade a critical dependency.

### Checklist Process:

```bash
#!/bin/bash
# pre-upgrade-check.sh

REPO=$1
CURRENT=$2
TARGET=$3

echo "Pre-Upgrade Analysis: $REPO"
echo "Current: $CURRENT → Target: $TARGET"
echo "========================================="

# 1. Latest release info
echo -e "\n✓ Fetching latest release..."
python kb_changes.py latest $REPO --detailed

# 2. Version comparison
echo -e "\n✓ Comparing versions..."
python kb_changes.py compare $REPO $CURRENT $TARGET

# 3. API changes
echo -e "\n✓ Checking API changes..."
python kb_changes.py api-changes $REPO

# 4. Summary
echo -e "\n========================================="
echo "Review the output above before upgrading."
echo "Key things to check:"
echo "  • Breaking changes marked with ⚠️"
echo "  • API changes marked with 🔄"
echo "  • Deprecations marked with ⏳"
echo "  • Security fixes marked with 🔒"
```

Usage:
```bash
./pre-upgrade-check.sh facebook/react v17.0.0 v18.2.0
```

## Detecting Specific Types of Changes

### Property Naming Changes

The script automatically detects:

**Pattern 1: camelCase → snake_case**
```
Detected: maxOutputTokens → max_output_tokens
Detected: stopSequences → stop_sequences
```

**Pattern 2: Explicit renames**
```
Detected: Renamed maxTokens to max_tokens
Detected: maxDuration is now max_duration
```

**Pattern 3: Code diff analysis**
```diff
- interface Options {
-   maxTokens: number;
+ interface Options {
+   max_tokens: number;
```

### Breaking Changes

Keywords detected:
- "breaking change"
- "backwards incompatible"
- "removed"
- "no longer supported"
- "breaking:"

### Deprecations

Keywords detected:
- "deprecated"
- "will be removed"
- "legacy"
- "obsolete"
- "use X instead"

## Tips for Effective Change Tracking

1. **Watch actively-developed repos** - High-activity repos benefit most from watching
2. **Check before upgrading** - Always run analysis before major version upgrades
3. **Use detailed mode** - Add `--detailed` for important repos
4. **Clone for deep analysis** - API change detection requires local clone
5. **Regular updates check** - Run `kb_changes.py updates` weekly
6. **Combine multiple views** - Use latest, changelog, and compare together
7. **Focus on your file types** - Use `--pattern` to filter API changes

## Integration with Development Workflow

### Daily Standup
```bash
# Quick check of watched repos
python kb_changes.py updates
```

### Sprint Planning
```bash
# Detailed review of planned upgrades
python kb_changes.py latest framework/repo --detailed
python kb_changes.py compare framework/repo current-version target-version
```

### Code Review
```bash
# When reviewing dependency updates
python kb_changes.py api-changes dependency/repo
```

### Documentation Updates
```bash
# Extract changelog for release notes
python kb_changes.py changelog your/repo --lines 1000 > CHANGELOG_REVIEW.md
```

## Troubleshooting

### "No releases found"

Some repos don't use GitHub releases. Try:
```bash
python kb_changes.py changelog repo
# or check commits directly
python kb_changes.py latest repo  # Shows commits even without releases
```

### "Repository not cloned yet"

For API change tracking and version comparison:
```bash
python kb_explore.py clone owner/repo
```

### "Could not fetch commits"

Usually a network or auth issue:
```bash
# Check if GITHUB_TOKEN is set
echo $GITHUB_TOKEN

# Test API access
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

### API changes not detected

Ensure:
1. Repository is cloned
2. Recent commits modify relevant files
3. Use `--pattern` to specify file types

## Advanced Examples

### Track Anthropic SDK API Changes

```bash
# Add to KB
python kb.py add anthropics/anthropic-sdk-typescript

# Clone
python kb_explore.py clone anthropics/anthropic-sdk-typescript

# Check what's new
python kb_changes.py latest anthropics/anthropic-sdk-typescript --detailed

# Track API changes
python kb_changes.py api-changes anthropics/anthropic-sdk-typescript --pattern "*.ts"

# Compare versions
python kb_changes.py compare anthropics/anthropic-sdk-typescript v0.9.0 v0.10.0

# Watch for updates
python kb_changes.py watch anthropics/anthropic-sdk-typescript
```

### Monitor Framework Ecosystem

```bash
# Add all framework repos
python kb.py add facebook/react
python kb.py add vercel/next.js
python kb.py add remix-run/remix
python kb.py add gatsbyjs/gatsby

# Tag them
for repo in facebook/react vercel/next.js remix-run/remix gatsbyjs/gatsby; do
  python kb.py tag $repo react framework
done

# Watch all
for repo in facebook/react vercel/next.js remix-run/remix gatsbyjs/gatsby; do
  python kb_changes.py watch $repo
done

# Weekly check
python kb_changes.py updates
```

## Summary

The change tracking feature helps you:
- ✓ Stay updated on releases and commits
- ✓ Detect breaking changes before they break your code
- ✓ Track API changes including subtle renames
- ✓ Compare versions comprehensively
- ✓ Monitor multiple dependencies efficiently
- ✓ Make informed upgrade decisions

Use it regularly to maintain awareness of your dependencies and plan updates strategically.
