#!/bin/sh

# Any changes to this file should be reflected at:
# https://gist.github.com/izzygomez/c4efca57c2237277e3f725b612608b6b
#
# Quick script to split a file in `git` into two files while preserving blame
# history, which is useful for e.g. code blame view on Github.com.
#
# Inspired by answers [1] & [2] from Stack Overflow.
#
# Usage:
#   - From clean working directory in your `main` branch, create a new splitting
#     branch: `git checkout -b split-NEW-FILE-from-ORIGINAL-FILE`
#   - Run this script: `git-split.sh ORIGINAL-FILE NEW-FILE`
#   - Verify `git log` shows all "[Tool commit]" commits created in this script.
#   - Edit ORIGINAL-FILE & NEW-FILE to only contain contents they should now
#     contain*.
#   - Commit new changes: `git add . && git commit -m "Split ORIGINAL-FILE &
#     NEW-FILE definitions"`
#   - Push changes to remote directory: `git push`
#   - Verify history & blame looks correct on remote repo (e.g. on Github.com).
#
#
# * For example, if ORIGINAL-FILE was a file that contained definitions for two
#   classes A & B, & the refactor is to split these classes into separate files,
#   then ORIGINAL-FILE should delete class B's definition & NEW-FILE should
#   delete class A's definition. Put differently, the state of files & file
#   contents should have the following transformation:
#
#   { ORIGINAL-FILE: {A, B} } ==> { ORIGINAL-FILE: {A}, NEW-FILE: {B} }
#
#
# [1] https://stackoverflow.com/a/53849651
# [2] https://stackoverflow.com/a/53849613

if [[ $# -ne 2 ]]; then
    echo "Usage: git-split.sh original-file new-file"
    exit 0
fi

GIST_LINK="https://gist.github.com/izzygomez/c4efca57c2237277e3f725b612608b6b"
MADE_BY_TOOL_MSG="This commit was made by a tool. See: $GIST_LINK"

git mv "$1" "$2"
git commit -n -m "[Tool Commit] Split history \`$1\` to \`$2\` - rename original-file to new-file" -m "$MADE_BY_TOOL_MSG"
REV=$(git rev-parse HEAD)
git reset --hard HEAD^
git mv "$1" temp
git commit -n -m "[Tool Commit] Split history \`$1\` to \`$2\` - rename original-file to temp" -m "$MADE_BY_TOOL_MSG"
git merge $REV
git commit -a -n -m "[Tool Commit] Split history \`$1\` to \`$2\` - resolve conflict and keep both files" -m "$MADE_BY_TOOL_MSG"
git mv temp "$1"
git commit -n -m "[Tool Commit] Split history \`$1\` to \`$2\` - restore name of original-file" -m "$MADE_BY_TOOL_MSG"
