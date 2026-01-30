#!/usr/bin/env bash
# Fix permissions for all GitHub KB scripts

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Setting executable permissions..."

# Make all scripts executable
chmod +x "$SCRIPT_DIR"/scripts/*.py
chmod +x "$SCRIPT_DIR"/bin/*
chmod +x "$SCRIPT_DIR"/*.sh

echo "✓ Permissions fixed!"
echo ""
echo "Scripts:"
ls -l "$SCRIPT_DIR"/scripts/*.py
echo ""
echo "Commands:"
ls -l "$SCRIPT_DIR"/bin/*
