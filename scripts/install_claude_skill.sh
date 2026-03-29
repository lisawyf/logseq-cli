#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SOURCE_ROOT="${REPO_ROOT}/integrations/claude"
CLAUDE_HOME="${HOME}/.claude"
COMMANDS_DIR="${CLAUDE_HOME}/commands"
TARGET_MEMORY="${CLAUDE_HOME}/CLAUDE.md"
SOURCE_MEMORY="${SOURCE_ROOT}/CLAUDE.md"

mkdir -p "${COMMANDS_DIR}"
cp "${SOURCE_ROOT}/commands/"*.md "${COMMANDS_DIR}/"

if [[ -f "${TARGET_MEMORY}" ]] && grep -q "BEGIN LOGSEQ-CLI KB" "${TARGET_MEMORY}"; then
  echo "Claude memory snippet already installed in ${TARGET_MEMORY}"
else
  {
    printf "\n<!-- BEGIN LOGSEQ-CLI KB -->\n"
    cat "${SOURCE_MEMORY}"
    printf "\n<!-- END LOGSEQ-CLI KB -->\n"
  } >> "${TARGET_MEMORY}"
  echo "Installed Claude memory snippet into ${TARGET_MEMORY}"
fi

echo "Installed Claude commands:"
for file in "${SOURCE_ROOT}/commands/"*.md; do
  echo "  /$(basename "${file}" .md)"
done

echo
echo "Next steps:"
echo "1. Make sure logseq-cli is installed and on PATH."
echo "2. Run: logseq-cli graph use --graph /path/to/your/Logseq"
echo "3. Restart Claude Code or open a new session."
echo "4. Try: /logseq-status"

