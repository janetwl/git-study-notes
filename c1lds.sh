#!/bin/bash
set -euo pipefail

# Claude Code against CyberNeurova
# DeepSeek V4 Flash on spark02.
BASE_URL="${CLLDS_BASE_URL:-http://100.100.1.6:8089}"
MODEL="${CLLDS_MODEL:-cyberneurova-fast}"
CONTEXT_TOKENS="${CLLDS_CONTEXT_TOKENS:-32768}"

if [[ "${1:-}" == '--help' || "${1:-}" == '-h' ]]; then
  printf 'Usage: c1lds [Claude Code arguments]\n\nSelect Fast, Low, Medium, or High in /model, or use --model cyberneurova-low.\nThese aliases control thinking budgets; the generic effort slider is ignored.\n\nUses %s at %s, with a separate ~/.claude-lds profile.\nPermission checks are bypassed, matching the previous clhh wrapper.\n\n' "$MODEL" "$BASE_URL"
  exec claude --help
fi

command -v claude >/dev/null 2>&1 || { printf 'c1lds: claude is not on PATH.\n' >&2; exit 127; }
if ! curl -fsS --max-time 180 "${BASE_URL%/}/health" >/dev/null; then
  printf 'c1lds: CyberNeurova is unavailable at %s.\nCheck: ssh spark02 systemctl --user status cyberneurova\n' "$BASE_URL" >&2
  exit 1
fi

export CLAUDE_CONFIG_DIR="$HOME/.claude-lds"
unset ANTHROPIC_API_KEY CLAUDE_CODE_OAUTH_TOKEN
unset CLAUDE_CODE_OAUTH_REFRESH_TOKEN CLAUDE_CODE_OAUTH_SCOPES
unset CLAUDE_CODE_USE_BEDROCK CLAUDE_CODE_USE_VERTEX
unset CLAUDE_CODE_USE_FOUNDRY CLAUDE_CODE_USE_ANTHROPIC_AWS
unset CLAUDE_CODE_EFFORT_LEVEL
export ANTHROPIC_BASE_URL="${BASE_URL%/}"
# Local server does not require authentication; this is a client placeholder.
export ANTHROPIC_AUTH_TOKEN='local-cyberneurova'
if [[ -n "${CLLDS_MODEL:-}" ]]; then
  export ANTHROPIC_MODEL="$CLLDS_MODEL"
else
  unset ANTHROPIC_MODEL
fi
export ANTHROPIC_DEFAULT_MODEL='cyberneurova-fast'
export ANTHROPIC_DEFAULT_OPUS_MODEL='cyberneurova-high'
export ANTHROPIC_DEFAULT_FABLE_MODEL='cyberneurova-high'
export ANTHROPIC_DEFAULT_SONNET_MODEL='cyberneurova-medium'
export ANTHROPIC_DEFAULT_HAIKU_MODEL='cyberneurova-fast'
# Effort is controlled by the gateway alias, rather than Claude's effort slider.
export ANTHROPIC_DEFAULT_OPUS_MODEL_SUPPORTED_CAPABILITIES='thinking'
export ANTHROPIC_DEFAULT_FABLE_MODEL_SUPPORTED_CAPABILITIES='thinking'
export ANTHROPIC_DEFAULT_SONNET_MODEL_SUPPORTED_CAPABILITIES='thinking'
export ANTHROPIC_DEFAULT_HAIKU_MODEL_SUPPORTED_CAPABILITIES=''
export ANTHROPIC_CUSTOM_MODEL_OPTION='cyberneurova-low'
export ANTHROPIC_CUSTOM_MODEL_OPTION_SUPPORTED_CAPABILITIES='thinking'

export CLAUDE_CODE_SUBAGENT_MODEL='cyberneurova-fast'
export CLAUDE_CODE_MAX_CONTEXT_TOKENS="$CONTEXT_TOKENS"
export CLAUDE_CODE_MAX_OUTPUT_TOKENS="${CLLDS_MAX_OUTPUT_TOKENS:-4096}"
export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
export API_TIMEOUT_MS="${CLLDS_API_TIMEOUT_MS:-7200000}"

mkdir -p "$CLAUDE_CONFIG_DIR"
exec claude --dangerously-skip-permissions "$@"
