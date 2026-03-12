#!/usr/bin/env bash
#
# review-provider.sh — Shared provider helpers for agent-loops review scripts.
#
# Source this file from specialist-review.sh and test-review-request.sh.

review_provider_candidates() {
  local requested="${1:-auto}"

  case "$requested" in
    auto)
      printf '%s\n' claude gemini
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

review_provider_run() {
  local provider="$1"
  local prompt_file="$2"
  local output_file="$3"
  local stderr_log="$4"
  local timeout_seconds="$5"

  case "$provider" in
    claude)
      local max_budget="${CLAUDE_MAX_BUDGET:-0.50}"

      unset CLAUDECODE 2>/dev/null || true

      timeout "$timeout_seconds" claude --print \
        --no-session-persistence \
        --max-budget-usd "$max_budget" \
        --tools "" \
        <"$prompt_file" >"$output_file" 2>"$stderr_log"
      ;;
    gemini)
      local -a cmd
      cmd=(gemini --prompt "" --output-format text --approval-mode plan)

      if [[ -n "${GEMINI_MODEL:-}" ]]; then
        cmd+=(--model "${GEMINI_MODEL}")
      fi

      timeout "$timeout_seconds" "${cmd[@]}" \
        <"$prompt_file" >"$output_file" 2>"$stderr_log"
      ;;
    codex)
      local -a cmd
      cmd=(codex exec --ephemeral --skip-git-repo-check -C "$(pwd -P)" -s read-only -o "$output_file" -)

      if [[ -n "${CODEX_MODEL:-}" ]]; then
        cmd=(codex exec --ephemeral --skip-git-repo-check -C "$(pwd -P)" -m "${CODEX_MODEL}" -s read-only -o "$output_file" -)
      fi

      timeout "$timeout_seconds" "${cmd[@]}" \
        <"$prompt_file" >/dev/null 2>"$stderr_log"
      ;;
    *)
      echo "Error: Unsupported provider '$provider'." >&2
      return 1
      ;;
  esac
}
