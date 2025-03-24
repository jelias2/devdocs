#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Install Rust if not already installed
if ! command -v rustup &> /dev/null; then
    echo "Installing Rust..."
    rustup default stable
fi

# Install mdbook if not already installed
if ! command -v mdbook &> /dev/null; then
    echo "Installing mdbook..."
    # Detect architecture and OS
    ARCH=$(uname -m)
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')

    # Convert architecture names to match mdbook release format
    case "$ARCH" in
        "x86_64") MDBOOK_ARCH="x86_64" ;;
        "arm64"|"aarch64") MDBOOK_ARCH="aarch64" ;;
        *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
    esac

    # Set OS-specific variables
    case "$OS" in
        "linux") 
            MDBOOK_OS="unknown-linux-gnu"
            ARCHIVE_EXT="tar.gz" ;;
        "darwin") 
            MDBOOK_OS="apple-darwin"
            ARCHIVE_EXT="tar.gz" ;;
        *) echo "Unsupported operating system: $OS"; exit 1 ;;
    esac

    MDBOOK_VERSION="v0.4.47"
    MDBOOK_RELEASE="mdbook-${MDBOOK_VERSION}-${MDBOOK_ARCH}-${MDBOOK_OS}.${ARCHIVE_EXT}"
    MDBOOK_URL="https://github.com/rust-lang/mdBook/releases/download/${MDBOOK_VERSION}/${MDBOOK_RELEASE}"

    curl -L "$MDBOOK_URL" | tar xvz
    mv mdbook "$HOME/.cargo/bin"
fi

# Install mdbook-mermaid if not already installed
if ! command -v mdbook-mermaid &> /dev/null; then
    echo "Installing mdbook-mermaid..."
    cargo install mdbook-mermaid mdbook-template
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# echo "Updating submodules..."
# COMMIT=false bash "$SCRIPT_DIR/update-submodules.sh"

echo "Building..."
export PATH="$HOME/.cargo/bin:$PATH"
uv run run.py
