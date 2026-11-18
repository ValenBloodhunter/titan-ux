#!/usr/bin/env bash
set -euo pipefail

# Universal cross-agent installer for Titan-UX and its /titan-* wrapper skills.
# Usage:
#   ./install.sh [agent|custom-path] [--project] [--dry-run]
#
# Supported agents:
#   all          -> Install for all supported coding agents
#   claude       -> ~/.claude/skills/ (or .claude/skills/)
#   cursor       -> ~/.cursor/skills/ (or .cursor/skills/)
#   antigravity  -> ~/.gemini/config/skills/ (or .agents/skills/)
#   gemini       -> ~/.gemini/skills/ (or .gemini/skills/)
#   windsurf     -> ~/.codeium/windsurf/skills/ (or .windsurf/skills/)
#   cline        -> ~/.cline/skills/ (or .cline/skills/)
#   codex        -> ~/.codex/skills/ + ~/.agents/skills/ (or .agents/skills/)
#   opencode     -> ~/.config/opencode/skills/ (or .opencode/skills/)
#   copilot      -> ~/.copilot/skills/ (or .github/skills/)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="global"
DRY_RUN=0
AGENT=""

for arg in "$@"; do
  case "$arg" in
    --project|-p)
      MODE="project"
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    --help|-h)
      sed -n '3,19p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      AGENT="$arg"
      ;;
  esac
done

install_to_base() {
  local base="$1"
  local main_dir="$base/titan-ux"
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  [DRY-RUN] Would install titan-ux + 11 wrappers -> $base"
    return
  fi
  mkdir -p "$main_dir"
  cp "$SCRIPT_DIR/SKILL.md" "$SCRIPT_DIR/LICENSE" "$SCRIPT_DIR/requirements.txt" "$main_dir/"
  rm -rf "$main_dir/references" "$main_dir/scripts"
  cp -r "$SCRIPT_DIR/references" "$main_dir/references"
  cp -r "$SCRIPT_DIR/scripts" "$main_dir/scripts"
  for wrapper in "$SCRIPT_DIR"/skills/titan-*; do
    local name
    name="$(basename "$wrapper")"
    mkdir -p "$base/$name"
    cp -r "$wrapper"/* "$base/$name/"
  done
  echo "  [OK] Installed titan-ux + 11 /titan-* wrappers -> $base"
}

if [ -z "$AGENT" ]; then
  echo "Select target agent to install Titan-UX ($MODE):"
  echo "  1) All supported agents"
  echo "  2) Claude Code"
  echo "  3) Cursor"
  echo "  4) Antigravity"
  echo "  5) Gemini CLI"
  echo "  6) Windsurf"
  echo "  7) Cline"
  echo "  8) Codex / Generic Agents"
  echo "  9) OpenCode"
  echo " 10) GitHub Copilot"
  read -rp "Enter choice [1-10] (default: 1): " choice
  case "${choice:-1}" in
    1) AGENT="all" ;;
    2) AGENT="claude" ;;
    3) AGENT="cursor" ;;
    4) AGENT="antigravity" ;;
    5) AGENT="gemini" ;;
    6) AGENT="windsurf" ;;
    7) AGENT="cline" ;;
    8) AGENT="codex" ;;
    9) AGENT="opencode" ;;
    10) AGENT="copilot" ;;
    *) echo "Invalid choice." >&2; exit 1 ;;
  esac
fi

install_agent() {
  local target="$1"
  case "$target" in
    claude)
      [ "$MODE" = "project" ] && install_to_base ".claude/skills" || install_to_base "$HOME/.claude/skills"
      ;;
    cursor)
      [ "$MODE" = "project" ] && install_to_base ".cursor/skills" || install_to_base "$HOME/.cursor/skills"
      ;;
    antigravity)
      [ "$MODE" = "project" ] && install_to_base ".agents/skills" || install_to_base "$HOME/.gemini/config/skills"
      ;;
    gemini)
      [ "$MODE" = "project" ] && install_to_base ".gemini/skills" || install_to_base "$HOME/.gemini/skills"
      ;;
    windsurf)
      [ "$MODE" = "project" ] && install_to_base ".windsurf/skills" || install_to_base "$HOME/.codeium/windsurf/skills"
      ;;
    cline)
      [ "$MODE" = "project" ] && install_to_base ".cline/skills" || install_to_base "$HOME/.cline/skills"
      ;;
    codex|agents)
      if [ "$MODE" = "project" ]; then
        install_to_base ".agents/skills"
      else
        install_to_base "$HOME/.codex/skills"
        install_to_base "$HOME/.agents/skills"
      fi
      ;;
    opencode)
      [ "$MODE" = "project" ] && install_to_base ".opencode/skills" || install_to_base "$HOME/.config/opencode/skills"
      ;;
    copilot)
      [ "$MODE" = "project" ] && install_to_base ".github/skills" || install_to_base "$HOME/.copilot/skills"
      ;;
    *)
      install_to_base "$target"
      ;;
  esac
}

echo "Installing Titan-UX ($MODE mode)..."
if [ "$AGENT" = "all" ]; then
  for a in claude cursor antigravity gemini windsurf cline codex opencode copilot; do
    install_agent "$a"
  done
else
  install_agent "$AGENT"
fi

echo ""
echo "Titan-UX ready. Restart or open a new agent session and invoke /titan-ux or /titan-discover."
