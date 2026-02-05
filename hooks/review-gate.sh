#!/usr/bin/env bash
# Trigger cortex review on completion-like prompts
#
# Hook event: UserPromptSubmit
# Runs review gate when user signals task completion.

set -euo pipefail

prompt="${CLAUDE_HOOK_PROMPT:-}"

# Trigger on completion signals
if echo "$prompt" | grep -qiE "(done|finished|complete|ready for review|ready to merge|wrap up|final check|ship it|lgtm|all set|that.s it|we.re good)"; then
    cortex review 2>/dev/null || true
fi

exit 0
