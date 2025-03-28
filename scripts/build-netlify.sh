#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Configure Git with PAT if it exists
if [ -n "${GITHUB_PAT:-}" ]; then
    echo "Configuring Git with PAT..."
    git config --global url."https://${GITHUB_PAT}:x-oauth-basic@github.com/".insteadOf "https://github.com/"
fi

# Install Rust and set default toolchain if not already configured
if ! command -v rustup &> /dev/null || ! rustup show active-toolchain &> /dev/null; then
    echo "Installing/configuring Rust..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
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
    source "$HOME/.cargo/env"  # Ensure cargo is in PATH
    cargo install mdbook-mermaid mdbook-template
fi

# Install uv if not already installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "Building..."
export PATH="$HOME/.cargo/bin:$PATH"

# Before running uv check for netifly CI variables
if [ -n "${NETLIFY_URL:-}" ]; then
    DEPLOY_URL="$NETLIFY_URL"
elif [ -n "${DEPLOY_URL:-}" ]; then
    DEPLOY_URL="$DEPLOY_URL"
elif [ -n "${URL:-}" ]; then
    DEPLOY_URL="$URL"
else
    echo "Warning: No Netlify deployment URL found in environment variables"
    DEPLOY_URL="http://localhost:8000"  # fallback for local development
fi

echo "Deploy URL: $DEPLOY_URL"

# Export the URL so it's available to the Python script
export DEPLOY_URL

# Run the Python script with the config
CONFIG_FILE=${1:-"dependencies.toml"}  # Use first argument or default
uv run run.py -c "$CONFIG_FILE"
