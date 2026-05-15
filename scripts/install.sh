#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────────────────
# Apex Terminal — one-line installer
# Usage:  curl -sSL https://raw.githubusercontent.com/EnesDemir143/apex/main/scripts/install.sh | bash
# ────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO="EnesDemir143/apex"
BRANCH="main"
INSTALL_DIR="${HOME}/.apex"
BIN_DIR="${HOME}/.local/bin"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}═══ Apex Terminal Installer ═══${NC}"
echo ""

# ── Check prerequisites ──────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
    echo "Error: git is required. Install it first:"
    echo "  macOS: brew install git"
    echo "  Ubuntu: sudo apt install git"
    exit 1
fi

if ! command -v uv &>/dev/null; then
    echo "uv not found — installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # shellcheck disable=SC1091
    . "${HOME}/.cargo/env" 2>/dev/null || true
    export PATH="${HOME}/.cargo/bin:${PATH}"
fi

# ── Clone or update ──────────────────────────────────────────────────────
if [ -d "${INSTALL_DIR}" ]; then
    echo "Updating existing installation in ${INSTALL_DIR}..."
    cd "${INSTALL_DIR}"
    git fetch origin
    git checkout "${BRANCH}"
    git reset --hard "origin/${BRANCH}"
else
    echo "Cloning into ${INSTALL_DIR}..."
    git clone --depth=1 --branch "${BRANCH}" "https://github.com/${REPO}.git" "${INSTALL_DIR}"
    cd "${INSTALL_DIR}"
fi

# ── Install dependencies ─────────────────────────────────────────────────
echo ""
echo "Installing Python dependencies..."
uv sync

# ── Symlink to PATH ──────────────────────────────────────────────────────
mkdir -p "${BIN_DIR}"
ln -sf "${INSTALL_DIR}/.venv/bin/apex" "${BIN_DIR}/apex"

echo ""
echo -e "${GREEN}═══ Installation complete ═══${NC}"
echo ""
echo "Add to your PATH (if not already):"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "Then set your API key and launch:"
echo "  cp ${INSTALL_DIR}/.env.example ${INSTALL_DIR}/.env"
echo "  # edit ${INSTALL_DIR}/.env → set OPENAI_API_KEY"
echo "  apex"
echo ""
echo "For quant ML support:"
echo "  cd ${INSTALL_DIR} && uv sync --group quant && bash scripts/train_models.sh"
