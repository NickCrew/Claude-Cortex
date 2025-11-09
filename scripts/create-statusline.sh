#!/usr/bin/env bash
# Claude Code statusLine based on Powerlevel10k lean theme

ESC='\033'
NC="${ESC}[0m"        # Reset

# Bright colors
B_RED="${ESC}[1;31m"
B_GRE="${ESC}[1;32m"
B_YEL="${ESC}[1;33m"
B_BLU="${ESC}[1;34m"
B_MAG="${ESC}[1;35m"
B_CYA="${ESC}[1;36m"
B_WHI="${ESC}[1;37m"

# Regular colors
RED="${ESC}[0;31m"
GRE="${ESC}[0;32m"
YEL="${ESC}[0;33m"
BLU="${ESC}[0;34m"
MAG="${ESC}[0;35m"
CYA="${ESC}[0;36m"
WHI="${ESC}[0;37m"

SEP="  "

# Convert milliseconds to HH:MM:SS
# Usage: ms_to_hhmmss <milliseconds>
# Example: ms_to_hhmmss 123456789
#          123456789 ms -> 34:17:36
ms_to_hhmmss() {
    local ms=$1
    if [[ -z "$ms" || ! "$ms" =~ ^-?[0-9]+$ ]]; then
        echo "00:00:00"
        return 1
    fi

    # Work with absolute value to avoid negative pitfalls
    local neg=0
    if (( ms < 0 )); then
        neg=1
        ms=$(( -ms ))
    fi

    local total_seconds=$(( ms / 1000 ))
    local hours=$(( total_seconds / 3600 ))
    local minutes=$(( (total_seconds % 3600) / 60 ))
    local seconds=$(( total_seconds % 60 ))

    if (( neg )); then
        printf "-%02d:%02d:%02d" "$hours" "$minutes" "$seconds"
    else
        printf "%02d:%02d:%02d" "$hours" "$minutes" "$seconds"
    fi
}

# Shorten path for display
shorten_path_custom() {
    local path="${1:-$PWD}"

    # Replace $HOME with ~
    if [[ $path == "$HOME"* ]]; then
        path="~${path#$HOME}"
    fi

    # Split by '/'
    local IFS='/'
    read -r -a parts <<< "$path"
    local n=${#parts[@]}

    # Return as-is if very short
    if (( n <= 2 )); then
        printf "%s\n" "$path"
        return 0
    fi

    # Build output
    local out="" seg i
    out="${parts[0]}"  # first segment (could be ~ or empty before leading /)

    # Determine index of second-to-last
    local second_last_index=$((n - 2))

    for (( i=1; i<n-1; i++ )); do
        seg=${parts[i]}
        if (( i == 1 )); then
            # First directory after root/home: take first 3 chars
            out+="/${seg:0:3}"
        elif (( i == second_last_index )); then
            # Second-to-last directory: first 3 chars
            out+="/${seg:0:3}"
        else
            # Other middle directories: first char
            out+="/${seg:0:1}"
        fi
    done

    # Append last directory in full
    out+="/${parts[n-1]}"

    printf "%s\n" "$out"
}

# Read input JSON from stdin
input=$(cat)

model="${BLU}  $(echo "$input" | jq -r '.model.display_name // .model.id')${SEP}${NC}"

cwd=$(echo "$input" | jq -r '.workspace.current_dir')

session_time_ms=$(echo "$input" | jq -r '.session_duration_ms')
session_time=$(ms_to_hhmmss "$session_time_ms")
session_id=$(echo "$input" | jq -r '.session_id' | cut -d '-' -f 1)

raw_transcript_path=$(echo "$input" | jq -r '.transcript_path')
raw_cost=$(echo "$input" | jq -r '.cost.total_cost_usd')
raw_lines_added=$(echo "$input" | jq -r '.cost.total_lines_added')
raw_lines_removed=$(echo "$input" | jq -r '.cost.total_lines_removed')

fmt_session_duration="${B_WHI}  ${session_time}${SEP}${NC}"
fmt_session_id="${B_CYA}  ${session_id}${SEP}${NC}"
fmt_cost="${B_GRE}$(printf '%.0f' "$raw_cost")${SEP}${NC}"
fmt_changes="${B_GRE} ${raw_lines_added}${B_RED}  ${raw_lines_removed}${SEP}${NC}"
fmt_transcript_path="${B_CYA} ${raw_transcript_path}${NC}"

# Display directory path with tilde for home
if [[ "$cwd" == "$HOME"* ]]; then
  display_dir="~${cwd#$HOME}"
else
  display_dir="$cwd"
fi
display_dir=$(shorten_path_custom "$cwd")

display_dir="${B_CYA}  ${display_dir}${SEP}${NC}"

# Git info
git_info=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" -c core.useBuiltinFSMonitor=false branch --show-current 2>/dev/null)
  if [[ -n "$branch" ]]; then
    status=""

    upstream=$(git -C "$cwd" rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null)

    # Ahead/behind indicator
    if [[ -n "$upstream" ]]; then
      stashed=0
      modified=0
      stashed=$(git rev-list --walk-reflogs --count refs/stash 2>/dev/null)
      ahead=$(git -C "$cwd" rev-list --count HEAD..@{u} 2>/dev/null || echo 0)
      behind=$(git -C "$cwd" rev-list --count @{u}..HEAD 2>/dev/null || echo 0)
      modified=$(git diff --name-only | wc -l | tr -d ' ' 2>/dev/null)
      [[ $ahead -gt 0 ]] && status="${status} ${B_RED}⇣${ahead}${NC}"
      [[ $behind -gt 0 ]] && status="${status} ${B_GRE}⇡${behind}${NC}"
      [[ $stashed -gt 0 ]] && status="${status} ${B_MAG}*${stashed}${NC}"
      [[ $modified -gt 0 ]] && status="${status} ${B_YEL}!${modified}${NC}"

      # Staged and untracked using porcelain v1
      staged=0
      untracked=0
      while IFS= read -r line; do
          case "$line" in
              "?? "*)
                  ((untracked++))
                  ;;
              *)
                  # First two chars are XY; staged when X != ' '
                  xy="${line%% *}"
                  [[ -n "$xy" ]] || continue
                  x="${xy:0:1}"
                  if [[ "$x" != " " ]]; then
                      ((staged++))
                  fi
                  ;;
          esac
      done < <(git -C "$cwd" status --porcelain --untracked-files=normal 2>/dev/null)

      # Apply mapping: ? = staged, ! = untracked
      if [[ $staged -gt 0 ]]; then
          status+="${B_CYA} +${staged}${NC}"
      fi
      if [[ $untracked -gt 0 ]]; then
          status+="${B_BLU} ?${untracked}${NC}"
      fi
    fi

    git_info="${B_BLU} $(printf '\uF126') ${branch}${status}${NC}"
  fi
fi

version="v$(claude --version | cut -d ' ' -f 1 2>/dev/null)"

kubectx="$(kubectl ctx -c 2>/dev/null)"
kube_info=""
[[ -n "$kubectx" ]] && kube_info="${MAG}󰒋 ${kubectx}${NC}"

aws_profile="${AWS_PROFILE:-}"
aws_region="${AWS_REGION:-}"
aws_info=""
[[ -z "$aws_profile" ]] || aws_info=" ${aws_profile}"
[[ -z "$aws_region" ]] || aws_info="${aws_info} ${aws_region}"
[[ -n "$aws_info" ]] && aws_info="${YEL}  ${aws_info}${NC}"

os_icon="$(printf '\uF179')"
current_time="${B_WHI}  $(date +%H:%M:%S)${NC}"

printf "%b %b \n%b %b %b %b %b \n%b" \
  "${display_dir}" \
  "${git_info}" \
  "${fmt_session_duration}" \
  "${fmt_cost}" \
  "${fmt_session_id}" \
  "${fmt_changes}" \
  "${model}" \
  "${kube_info}"

