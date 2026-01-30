# Setup Guide

## Installation

Install the skill in Claude Code:

```bash
claude skills add <PATH_TO_THE_REPO>/github-knowledge-base
```

Or navigate to the directory and install:

```bash
cd <PATH_TO_THE_REPO>/github-knowledge-base
claude skills add .
```

## Requirements

- **Python**: 3.7 or higher
- **Git**: For cloning repositories
- **Internet**: For GitHub API access

Optional but recommended:
- **ripgrep (rg)**: For faster code searching
- **tree**: For better directory visualization

### Installing Optional Tools

**macOS:**
```bash
brew install ripgrep tree
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ripgrep tree
```

**Linux (Fedora):**
```bash
sudo dnf install ripgrep tree
```

## Python SSL Certificates (macOS)

If you encounter SSL certificate errors on macOS:

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solution 1: Install Certificates (Recommended)**

If you installed Python from python.org:
```bash
/Applications/Python\ 3.x/Install\ Certificates.command
```

Replace `3.x` with your Python version (e.g., `3.11`, `3.12`).

**Solution 2: Use Homebrew Python**

```bash
brew install python3
```

Homebrew Python comes with certificates pre-configured.

**Solution 3: Install certifi**

```bash
pip3 install --upgrade certifi
```

## GitHub Token Setup (Recommended)

A GitHub token increases your API rate limit from 60 to 5,000 requests per hour.

### Creating a Token

1. Visit https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name it: "GitHub KB Tool"
4. Select scope: `public_repo` (read access to public repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)

### Setting the Token

**Temporary (current session only):**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Permanent (add to shell config):**

For bash (~/.bashrc):
```bash
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.bashrc
source ~/.bashrc
```

For zsh (~/.zshrc):
```bash
echo 'export GITHUB_TOKEN=ghp_your_token_here' >> ~/.zshrc
source ~/.zshrc
```


### Verifying the Token

```bash
echo $GITHUB_TOKEN
# Should output: ghp_your_token_here
```

Test the rate limit:
```bash
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit
```

Should show:
```json
{
  "resources": {
    "core": {
      "limit": 5000,
      ...
    }
  }
}
```

## First Use

After installation, the skill will automatically initialize the knowledge base on first use:

```bash
python3 scripts/kb.py list
# Output: Knowledge base is empty.
```

This creates:
```
~/.config/github-kb/
├── index.json
├── repos/
├── notes/
└── cache/
```

## Testing the Installation

### Test 1: Basic Commands

```bash
# Navigate to skill directory
cd ./github-knowledge-base

# List (should be empty)
python3 scripts/kb.py list

# Show stats (should be empty)
python3 scripts/kb.py stats
```

### Test 2: Adding a Repository

```bash
# Add a small repository
python3 scripts/kb.py add tj/commander.js

# Should output:
# ✓ Added 'tj/commander.js' to knowledge base
# Summary: The complete solution for node.js command-line interfaces
# ...
```

If this works, your setup is complete!

### Test 3: GitHub Search

```bash
# Search GitHub
python3 scripts/kb_search.py github "nodejs cli" --limit 5

# Should return top 5 Node.js CLI repositories
```

### Test 4: Clone and Explore

```bash
# Clone a repository
python3 scripts/kb_explore.py clone tj/commander.js

# Analyze structure
python3 scripts/kb_explore.py analyze tj/commander.js

# View README
python3 scripts/kb_explore.py readme tj/commander.js
```

## Troubleshooting

### Issue: "command not found: claude"

**Solution**: Install Claude Code CLI first
```bash
# Follow Claude Code installation instructions
```

### Issue: "python3: command not found"

**Solution**: Install Python 3
```bash
# macOS
brew install python3

# Linux
sudo apt install python3  # Ubuntu/Debian
sudo dnf install python3  # Fedora
```

### Issue: SSL Certificate Error

See "Python SSL Certificates" section above.

### Issue: API Rate Limit Exceeded

**Solution**: Set up GitHub token (see above)

### Issue: Git Clone Fails

**Check**:
1. Git is installed: `git --version`
2. Internet connection works
3. Repository URL is correct

### Issue: Permission Denied

**Solution**: Make scripts executable
```bash
chmod +x scripts/*.py
```

### Issue: Scripts Import Error

If you see:
```
ModuleNotFoundError: No module named 'kb'
```
**Solution 1**: 
For bash (~/.bashrc):
```bash 
source ~./bashrc
```

For zsh (~/.zshrc):
```bash
source ~./zshrc
```

**Solution 2**: Run scripts from skill directory or use full paths
```bash
cd <PATH_TO_THE_REPO>/github-knowledge-base
python3 scripts/kb_search.py related owner/repo
```

Or use full path:
```bash
python3 <PATH_TO_THE_REPO>/github-knowledge-base/scripts/kb.py list
```

## Uninstallation

### Remove Skill

```bash
claude skills remove github-knowledge-base
```

### Remove Data

To completely remove all data:

```bash
rm -rf ~/.config/github-kb
```

**Warning**: This deletes all your repository clones, notes, and index!

To keep the index but remove clones:
```bash
rm -rf ~/.config/github-kb/repos/*
```

## Directory Structure

After installation and use:

```
~/.config/github-kb/           # Persistent knowledge base
├── index.json                 # Repository registry
├── repos/                     # Cloned repositories
│   └── owner__repo/          # Repo clones
├── notes/                     # Your notes
│   └── owner__repo.md        # Note files
└── cache/                     # API cache (future use)

./github-knowledge-base/  # Skill files
├── SKILL.md                   # Claude instructions
├── README.md                  # User documentation
├── SETUP.md                   # This file
├── scripts/                   # Python scripts
│   ├── kb.py                 # Main management
│   ├── kb_search.py          # Search & discovery
│   └── kb_explore.py         # Exploration
└── references/                # Additional docs
    ├── workflows.md           # Workflow examples
    └── github-api.md          # API reference
```

## Advanced Configuration

### Custom Storage Location

Currently uses `~/.config/github-kb/`. To change:

1. Edit all three Python scripts
2. Change `KB_DIR = Path.home() / ".config" / "github-kb"`
3. To your preferred location

### Using with Virtual Environments

Not necessary - scripts use only Python standard library.

But if you prefer:

```bash
cd github-knowledge-base
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

python scripts/kb.py list
```

## Support

If you encounter issues:

1. Check this setup guide
2. Review README.md
3. Check references/workflows.md for examples
4. Ask Claude Code for help:
   - "Help me set up the github-knowledge-base skill"
   - "I'm getting an error with kb.py"

## Next Steps

Once setup is complete:

1. Read the [README.md](README.md) for usage guide
2. Check [references/workflows.md](references/workflows.md) for examples
3. Start building your knowledge base!

Quick start:
```
You: "Add the React repository to my knowledge base"
You: "Find me repos for authentication in Node.js"
You: "Show my repos"
```

Happy exploring!
