#!/usr/bin/env bash
# Install GitHub KB commands to PATH

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$SCRIPT_DIR/bin"

# Detect shell
SHELL_NAME="$(basename "$SHELL")"
case "$SHELL_NAME" in
    bash)
        SHELL_RC="$HOME/.bashrc"
        ;;
    zsh)
        SHELL_RC="$HOME/.zshrc"
        ;;
    fish)
        SHELL_RC="$HOME/.config/fish/config.fish"
        ;;
    *)
        SHELL_RC="$HOME/.profile"
        ;;
esac

echo "GitHub Knowledge Base - Command Installation"
echo "=============================================="
echo ""
echo "This will add GitHub KB commands to your PATH."
echo "Commands: kb, kb-search, kb-explore, kb-changes, kb-pdf, kb-books"
echo ""
echo "Detected shell: $SHELL_NAME"
echo "Config file: $SHELL_RC"
echo ""

# Check if already in PATH
if echo "$PATH" | grep -q "$BIN_DIR"; then
    echo "✓ Commands already in PATH!"
    echo ""
    echo "Available commands:"
    echo "  kb          - Repository management"
    echo "  kb-search   - Search & discovery"
    echo "  kb-explore  - Repository exploration"
    echo "  kb-changes  - Change tracking"
    echo "  kb-pdf      - PDF management (token-aware)"
    echo "  kb-books    - Known books detection (avoid token waste)"
    echo ""
    exit 0
fi

# Prompt for installation
read -p "Add commands to PATH in $SHELL_RC? [y/N] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Installation cancelled."
    echo ""
    echo "To manually add commands to PATH, add this line to your shell config:"
    echo ""
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
    echo ""
    exit 0
fi

# Add to shell config
echo "" >> "$SHELL_RC"
echo "# GitHub Knowledge Base commands" >> "$SHELL_RC"
echo "export PATH=\"$BIN_DIR:\$PATH\"" >> "$SHELL_RC"

echo "✓ Added to $SHELL_RC"
echo ""
echo "To use the commands now, run:"
echo "  source $SHELL_RC"
echo ""
echo "Or restart your terminal."
echo ""
echo "Available commands:"
echo "  kb add <repo>                       - Add repository"
echo "  kb list                             - List repositories"
echo "  kb-search github <query>            - Search GitHub"
echo "  kb-explore clone <repo>             - Clone repository"
echo "  kb-changes latest <repo>            - Show latest changes"
echo "  kb-pdf add <file>                   - Add PDF (with token estimate)"
echo "  kb-books check 'Clean Code'         - Check if book is known"
echo "  kb-books combo clean-code-fundamentals - Get ready-to-use prompts"
echo ""
echo "Run 'kb --help' for full usage."
