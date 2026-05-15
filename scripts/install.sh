#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────────────────
# Apex Terminal — one-line installer
# Usage:  curl -sSL https://raw.githubusercontent.com/EnesDemir143/apex/main/scripts/install.sh | bash
#
# Supports: macOS (Intel + Apple Silicon), Linux (x86_64 + ARM64)
# Windows: use WSL2 (Ubuntu) — run this script inside WSL
# ────────────────────────────────────────────────────────────────────────────

set -euo pipefail

REPO="EnesDemir143/apex"
BRANCH="main"
INSTALL_DIR="${HOME}/.apex"
BIN_DIR="${HOME}/.local/bin"

# Detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux)  OS="linux" ;;
    Darwin) OS="macos" ;;
    *)      echo "Unsupported OS: ${OS} — try WSL2 on Windows"; exit 1 ;;
esac

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
VENV_APEX="${INSTALL_DIR}/.venv/bin/apex"
if [ -f "${VENV_APEX}" ]; then
    mkdir -p "${BIN_DIR}"
    ln -sf "${VENV_APEX}" "${BIN_DIR}/apex"
fi

# Detect if BIN_DIR is in PATH
IN_PATH=0
case ":${PATH}:" in
    *:"${BIN_DIR}":*) IN_PATH=1 ;;
esac

echo ""
echo -e "${GREEN}═══ Installation complete ═══${NC}"
echo ""

if [ "${IN_PATH}" -eq 0 ]; then
    SHELL_CONFIG="${HOME}/.bashrc"
    if [ "${OS}" = "macos" ]; then
        SHELL_CONFIG="${HOME}/.zshrc"
    fi
    echo "Add to your PATH (auto-detected shell config: ${SHELL_CONFIG}):"
    echo "  echo 'export PATH=\"\$HOME/.local/bin:\$PATH\"' >> ${SHELL_CONFIG}"
    echo "  source ${SHELL_CONFIG}"
    echo ""
fi

echo "Then set your API key and launch:"
echo "  cp ${INSTALL_DIR}/.env.example ${INSTALL_DIR}/.env"
echo "  # edit ${INSTALL_DIR}/.env → set OPENAI_API_KEY"
echo "  apex"
echo ""
echo "For quant ML support:"
echo "  cd ${INSTALL_DIR} && uv sync --group quant && bash scripts/train_models.sh"
