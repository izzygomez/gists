#!/bin/bash

# =============================================================================
# check-repos.sh - Check & possibly sync multiple git repositories in parallel
# =============================================================================
#
# Usage:
#   ./check-repos.sh [directory]
#
# Arguments:
#   directory   Path to search for git repos (default: current directory)
#
# Examples:
#   ./check-repos.sh                     # Check all repos in current dir
#   ./check-repos.sh ~/code              # Check all repos under ~/code
#
# Behavior:
#   - Prompts whether to auto-pull repos that are behind (default: no)
#   - Only pulls if on main or master branch
#   - Repos on feature branches are reported but not pulled
#   - Fetches from all repos in parallel for speed
#
# Safety:
#   Auto-pull only runs if the repo:
#   - Is on main or master branch
#   - Has no uncommitted changes (staged or unstaged)
#   - Has no unpushed commits
#   - Has a valid upstream branch configured
#   - Can fast-forward (no merge required)
#
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m' # No Color

TOP_DIR="$(realpath "${1:-.}")"

# Prompt for auto-pull
echo -e "${BOLD}Checking repos in:${NC} $TOP_DIR"
echo
read -r -p "Auto-pull repos that are behind? [yN] " response
if [[ $response =~ ^[Yy]$ ]]; then
    AUTO_PULL=true
    echo -e "${GREEN}Auto-pull enabled${NC} (main/master branches only)"
else
    AUTO_PULL=false
    echo -e "${YELLOW}Auto-pull disabled${NC} (status check only)"
fi

# Create temp directory for parallel output
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

# Find all repos (same approach as sequential version)
REPO_DIRS=()
while read -r git_dir; do
    REPO_DIRS+=("$(dirname "$git_dir")")
done < <(find "$TOP_DIR" -maxdepth 2 -type d -name ".git" | sort)

TOTAL_REPOS=${#REPO_DIRS[@]}
MAX_JOBS=10
echo
echo -e "${DIM}Found $TOTAL_REPOS repos. Fetching in parallel (up to $MAX_JOBS concurrent)...${NC}"

# Process a single repo - called in parallel
process_repo() {
    local idx="$1"
    local repo_dir="$2"
    local auto_pull="$3"
    local tmp_dir="$4"

    local repo_name
    repo_name="$(basename "$repo_dir")"
    local out_file
    out_file="$tmp_dir/$(printf "%04d" "$idx")_${repo_name}.out"
    local state_file
    state_file="$tmp_dir/$(printf "%04d" "$idx")_${repo_name}.state"

    # Helper to check if safe to pull
    is_safe_to_pull() {
        local repo="$1"
        git -C "$repo" diff --quiet || return 1
        git -C "$repo" diff --cached --quiet || return 1
        git -C "$repo" rev-parse --abbrev-ref '@{u}' >/dev/null 2>&1 || return 1
        [ -z "$(git -C "$repo" log '@{u}..' 2>/dev/null)" ]
    }

    is_main_branch() {
        local branch="$1"
        [[ $branch == "main" || $branch == "master" ]]
    }

    check_dirty() {
        local has_unstaged=false has_staged=false has_untracked=false
        git -C "$repo_dir" diff --quiet 2>/dev/null || has_unstaged=true
        git -C "$repo_dir" diff --cached --quiet 2>/dev/null || has_staged=true
        [ -n "$(git -C "$repo_dir" ls-files --others --exclude-standard 2>/dev/null)" ] && has_untracked=true

        if $has_unstaged || $has_staged || $has_untracked; then
            local dirty_msg=""
            $has_staged && dirty_msg+="staged changes, "
            $has_unstaged && dirty_msg+="unstaged changes, "
            $has_untracked && dirty_msg+="untracked files, "
            dirty_msg="${dirty_msg%, }"
            echo -e "  ${YELLOW}Dirty:${NC} $dirty_msg"
            echo "$repo_name" >"$tmp_dir/$(printf "%04d" "$idx")_${repo_name}.dirty"
        fi
    }

    {
        # Validate repo
        if [ ! -d "$repo_dir" ]; then
            echo
            echo -e "${RED}Skipping invalid repo:${NC} $repo_dir (directory not found)"
            echo "INVALID:$repo_name" >"$state_file"
            exit 0
        fi

        if ! git -C "$repo_dir" rev-parse >/dev/null 2>&1; then
            echo
            echo -e "${RED}Skipping invalid repo:${NC} $repo_dir (not a valid git repository)"
            echo "INVALID:$repo_name" >"$state_file"
            exit 0
        fi

        echo
        echo -e "${BOLD}${CYAN}[$repo_name]${NC} $repo_dir"

        # Get current branch
        current_branch=$(git -C "$repo_dir" rev-parse --abbrev-ref HEAD)

        # Fetch (this is the slow part we're parallelizing)
        git -C "$repo_dir" fetch --all --quiet 2>/dev/null || true
        status="$(git -C "$repo_dir" status -sb 2>/dev/null)"

        # Check if on feature branch
        if ! is_main_branch "$current_branch"; then
            echo -e "  ${BLUE}Branch:${NC} $current_branch ${YELLOW}(feature branch)${NC}"
            echo "  $status"
            echo "FEATURE:$repo_name ($current_branch)" >"$state_file"
            check_dirty
            exit 0
        fi

        echo -e "  ${BLUE}Branch:${NC} $current_branch"

        if echo "$status" | grep -q '\[.*behind'; then
            echo -e "  ${RED}Status: Behind remote${NC}"
            echo "  $status"

            if [[ $auto_pull == "true" ]]; then
                if is_safe_to_pull "$repo_dir"; then
                    echo -e "  ${GREEN}Pulling latest changes...${NC}"
                    if git -C "$repo_dir" pull --ff-only origin "$current_branch" 2>&1; then
                        echo -e "  ${GREEN}Pulled successfully.${NC}"
                        echo "PULLED:$repo_name" >"$state_file"
                    else
                        echo -e "  ${RED}Pull failed.${NC}"
                        echo "DIRTY:$repo_name" >"$state_file"
                    fi
                else
                    echo -e "  ${YELLOW}Skipping pull:${NC} repo is not clean, has unpushed commits, or no upstream configured."
                    echo "DIRTY:$repo_name" >"$state_file"
                fi
            else
                echo "BEHIND:$repo_name" >"$state_file"
            fi
        elif echo "$status" | grep -q '\[.*ahead'; then
            echo -e "  ${YELLOW}Status: Ahead of remote${NC} (unpushed commits)"
            echo "  $status"
            echo "AHEAD:$repo_name" >"$state_file"
        else
            echo -e "  ${GREEN}Status: Up to date${NC}"
            echo "UP_TO_DATE:$repo_name" >"$state_file"
        fi

        check_dirty
    } >"$out_file" 2>&1
}

# Export function & variables for parallel execution
export -f process_repo
export RED GREEN YELLOW BLUE CYAN BOLD DIM NC

# Run all repos in parallel
job_count=0

for i in "${!REPO_DIRS[@]}"; do
    process_repo "$i" "${REPO_DIRS[$i]}" "$AUTO_PULL" "$TMP_DIR" &

    ((job_count++))
    if ((job_count >= MAX_JOBS)); then
        wait -n 2>/dev/null || true
        ((job_count--))
    fi
done

# Wait for remaining jobs
wait

# Print output in order
for out_file in "$TMP_DIR"/*.out; do
    [ -f "$out_file" ] && cat "$out_file"
done

# Aggregate summary from state files
declare -a SUMMARY_PULLED=()
declare -a SUMMARY_UP_TO_DATE=()
declare -a SUMMARY_FEATURE_BRANCH=()
declare -a SUMMARY_AHEAD=()
declare -a SUMMARY_BEHIND=()
declare -a SUMMARY_DIRTY=()
declare -a SUMMARY_INVALID=()
declare -a SUMMARY_HAS_CHANGES=()

for state_file in "$TMP_DIR"/*.state; do
    [ -f "$state_file" ] || continue
    state=$(cat "$state_file")
    category="${state%%:*}"
    value="${state#*:}"

    case "$category" in
    PULLED) SUMMARY_PULLED+=("$value") ;;
    UP_TO_DATE) SUMMARY_UP_TO_DATE+=("$value") ;;
    FEATURE) SUMMARY_FEATURE_BRANCH+=("$value") ;;
    AHEAD) SUMMARY_AHEAD+=("$value") ;;
    BEHIND) SUMMARY_BEHIND+=("$value") ;;
    DIRTY) SUMMARY_DIRTY+=("$value") ;;
    INVALID) SUMMARY_INVALID+=("$value") ;;
    esac
done

for dirty_file in "$TMP_DIR"/*.dirty; do
    [ -f "$dirty_file" ] || continue
    SUMMARY_HAS_CHANGES+=("$(cat "$dirty_file")")
done

# Print summary
echo
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}SUMMARY${NC}"
echo -e "${BOLD}═══════════════════════════════════════════════════════════════════════════════${NC}"

# Print a blank line between summary sections, but not before the first one
_section_count=0
section_gap() {
    [ "$_section_count" -gt 0 ] && echo || true
    _section_count=$((_section_count + 1))
}

# Helper: print each array element on its own line
print_each() { for item; do echo -e "$item"; done; }

if [ ${#SUMMARY_PULLED[@]} -gt 0 ]; then
    section_gap
    echo -e "${GREEN}✓ Pulled successfully (${#SUMMARY_PULLED[@]}):${NC}"
    echo -e "${DIM}${SUMMARY_PULLED[*]}${NC}"
fi

if [ ${#SUMMARY_UP_TO_DATE[@]} -gt 0 ]; then
    section_gap
    echo -e "${GREEN}✓ Already up to date (${#SUMMARY_UP_TO_DATE[@]}):${NC}"
    echo -e "${DIM}${SUMMARY_UP_TO_DATE[*]}${NC}"
fi

if [ ${#SUMMARY_FEATURE_BRANCH[@]} -gt 0 ]; then
    section_gap
    echo -e "${BLUE}◆ On feature branch (${#SUMMARY_FEATURE_BRANCH[@]}):${NC}"
    for fb in "${SUMMARY_FEATURE_BRANCH[@]}"; do
        local_name="${fb%% (*}"
        branch_info="${fb#"$local_name" }"
        echo -e "$local_name ${DIM}$branch_info${NC}"
    done
fi

if [ ${#SUMMARY_AHEAD[@]} -gt 0 ]; then
    section_gap
    echo -e "${YELLOW}▲ Ahead of remote (${#SUMMARY_AHEAD[@]}):${NC}"
    print_each "${SUMMARY_AHEAD[@]}"
fi

if [ ${#SUMMARY_BEHIND[@]} -gt 0 ]; then
    section_gap
    echo -e "${RED}▼ Behind remote (${#SUMMARY_BEHIND[@]}):${NC}"
    print_each "${SUMMARY_BEHIND[@]}"
fi

if [ ${#SUMMARY_DIRTY[@]} -gt 0 ]; then
    section_gap
    echo -e "${YELLOW}⚠ Dirty/skipped (${#SUMMARY_DIRTY[@]}):${NC}"
    print_each "${SUMMARY_DIRTY[@]}"
fi

if [ ${#SUMMARY_INVALID[@]} -gt 0 ]; then
    section_gap
    echo -e "${RED}✗ Invalid repos (${#SUMMARY_INVALID[@]}):${NC}"
    print_each "${SUMMARY_INVALID[@]}"
fi

if [ ${#SUMMARY_HAS_CHANGES[@]} -gt 0 ]; then
    section_gap
    echo -e "${YELLOW}● Dirty working tree (${#SUMMARY_HAS_CHANGES[@]}):${NC}"
    print_each "${SUMMARY_HAS_CHANGES[@]}"
fi

echo
echo -e "${DIM}Total: $TOTAL_REPOS repos scanned${NC}"
