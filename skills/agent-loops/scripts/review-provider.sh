#!/usr/bin/env bash
#
# review-provider.sh — Shared provider helpers for agent-loops review scripts.
#
# Source this file from specialist-review.sh and test-review-request.sh.

review_provider_detect_self() {
  local self_provider="${AGENT_LOOPS_SELF_PROVIDER:-}"

  case "$self_provider" in
    claude | gemini | codex)
      echo "$self_provider"
      return 0
      ;;
    "")
      ;;
    *)
      echo "Warning: Unsupported AGENT_LOOPS_SELF_PROVIDER '$self_provider'; ignoring it." >&2
      ;;
  esac

  if [[ -n "${CODEX_THREAD_ID:-}" || -n "${CODEX_MANAGED_BY_NPM:-}" ]]; then
    echo "codex"
    return 0
  fi

  if [[ -n "${GEMINI_CLI_NO_RELAUNCH:-}" || -n "${GEMINI_CLI_ACTIVITY_LOG_TARGET:-}" ]]; then
    echo "gemini"
    return 0
  fi

  if [[ -n "${CLAUDECODE:-}" ]]; then
    echo "claude"
    return 0
  fi

  echo ""
}

review_provider_candidates() {
  local requested="${1:-auto}"
  local self_provider="${2:-}"
  local -a default_order=(claude gemini codex)
  local provider

  case "$requested" in
    auto)
      for provider in "${default_order[@]}"; do
        if [[ "$provider" != "$self_provider" ]]; then
          printf '%s\n' "$provider"
        fi
      done
      if [[ -n "$self_provider" ]]; then
        printf '%s\n' "$self_provider"
      fi
      ;;
    claude | gemini | codex)
      printf '%s\n' "$requested"
      ;;
    *)
      echo "Error: Unsupported provider '$requested'. Use auto, claude, gemini, or codex." >&2
      return 1
      ;;
  esac
}

review_provider_is_available() {
  local provider="$1"
  command -v "$provider" >/dev/null 2>&1
}

review_provider_display_name() {
  case "$1" in
    claude)
      echo "Claude"
      ;;
    gemini)
      echo "Gemini"
      ;;
    codex)
      echo "Codex"
      ;;
    *)
      echo "$1"
      ;;
  esac
}

review_provider_timeout() {
  local provider="$1"
  local fallback="$2"

  case "$provider" in
    claude)
      echo "${CLAUDE_TIMEOUT:-$fallback}"
      ;;
    gemini)
      echo "${GEMINI_TIMEOUT:-$fallback}"
      ;;
    codex)
      echo "${CODEX_TIMEOUT:-$fallback}"
      ;;
    *)
      echo "$fallback"
      ;;
  esac
}

review_provider_claude_auth() {
  # Check if Claude CLI can authenticate in this process context.
  # Returns 0 if auth is available, 1 if not.
  # On failure, prints diagnostic guidance to stderr.

  # Fast path: API key is always portable across process contexts.
  if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
    return 0
  fi

  # Fast path: setup-token OAuth is file-based, works from sandboxed apps.
  if [[ -n "${CLAUDE_CODE_OAUTH_TOKEN:-}" ]]; then
    return 0
  fi

  # Probe keychain-based OAuth — this fails from sandboxed apps (e.g. Codex)
  # whose subprocesses can't read the "Claude Code-credentials" keychain item.
  local status_json
  status_json="$(claude auth status 2>/dev/null)" || true

  if printf '%s' "$status_json" | grep -q '"loggedIn": *true'; then
    return 0
  fi

  echo "Error: Claude CLI is not authenticated in this process context." >&2
  echo "" >&2
  echo "  Claude stores OAuth tokens in the macOS keychain. Subprocesses spawned" >&2
  echo "  by sandboxed apps (Codex, etc.) often cannot read that keychain item." >&2
  echo "" >&2
  echo "  Fix (pick one):" >&2
  echo "    1. Run 'claude setup-token' in a terminal, then add to your shell profile:" >&2
  echo "       export CLAUDE_CODE_OAUTH_TOKEN=<token>" >&2
  echo "    2. Export an API key:  export ANTHROPIC_API_KEY=sk-ant-..." >&2
  echo "    3. Use a different provider:  --provider gemini  or  --provider codex" >&2
  echo "" >&2
  return 1
}

review_provider_run() {
  local provider="$1"
  local prompt_file="$2"
  local output_file="$3"
  local stderr_log="$4"
  local timeout_seconds="$5"

  case "$provider" in
    claude)
      local max_budget="${CLAUDE_MAX_BUDGET:-2.00}"

      unset CLAUDECODE 2>/dev/null || true

      if ! review_provider_claude_auth; then
        return 1
      fi

      local -a claude_cmd=(claude --print
        --no-session-persistence
        --max-budget-usd "$max_budget"
        --strict-mcp-config
      )

      # --bare skips hooks, plugins, LSP, CLAUDE.md, and keychain reads
      # that commonly fail in sandboxed subprocesses.
      # IMPORTANT: --bare only supports ANTHROPIC_API_KEY, not OAuth tokens.
      # Do NOT use --bare with CLAUDE_CODE_OAUTH_TOKEN — it will be ignored.
      if [[ -n "${ANTHROPIC_API_KEY:-}" ]]; then
        claude_cmd+=(--bare)
      fi

      echo "Claude command: ${claude_cmd[*]}" >&2
      echo "Prompt size: $(wc -c <"$prompt_file" | tr -d ' ') bytes" >&2

      timeout "$timeout_seconds" "${claude_cmd[@]}" \
        <"$prompt_file" >"$output_file" 2>"$stderr_log"
      local claude_exit=$?

      # Detect auth failures that slip past the pre-flight check.
      # Claude sometimes exits 0 but writes "Not logged in" to output
      # instead of a review — catch it early so the fallback chain
      # picks up immediately without leaving a partial artifact.
      if [[ -s "$output_file" ]] && head -5 "$output_file" | grep -qi "not logged in\|please run /login\|sign in required"; then
        echo "Error: Claude output indicates auth failure (not logged in)." >&2
        rm -f "$output_file"
        return 1
      fi

      return "$claude_exit"
      ;;
    gemini)
      local -a cmd
      cmd=(gemini --prompt "" --output-format text --approval-mode plan
        --allowed-mcp-server-names _none_
      )

      if [[ -n "${GEMINI_MODEL:-}" ]]; then
        cmd+=(--model "${GEMINI_MODEL}")
      fi

      echo "Gemini command: ${cmd[*]}" >&2

      timeout "$timeout_seconds" "${cmd[@]}" \
        <"$prompt_file" >"$output_file" 2>"$stderr_log"
      ;;
    codex)
      local -a cmd
      cmd=(codex exec --ephemeral --skip-git-repo-check -C "$(pwd -P)" -s read-only -o "$output_file" -)

      if [[ -n "${CODEX_MODEL:-}" ]]; then
        cmd=(codex exec --ephemeral --skip-git-repo-check -C "$(pwd -P)" -m "${CODEX_MODEL}" -s read-only -o "$output_file" -)
      fi

      # Clear parent session env vars so the nested codex exec doesn't
      # try to join or conflict with the calling Codex session.
      unset CODEX_THREAD_ID 2>/dev/null || true
      unset CODEX_MANAGED_BY_NPM 2>/dev/null || true

      echo "Codex command: ${cmd[*]}" >&2

      timeout "$timeout_seconds" "${cmd[@]}" \
        <"$prompt_file" >/dev/null 2>"$stderr_log"
      ;;
    *)
      echo "Error: Unsupported provider '$provider'." >&2
      return 1
      ;;
  esac
}
