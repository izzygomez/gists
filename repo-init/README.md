# Setting up new personal GitHub repos

A collection of standardized files & documentation for jumpstarting new personal GitHub repositories.

When creating a new repo, there's a set of configurations, settings, & files that I find myself repeatedly setting up. This directory serves as a central reference & source of truth for those patterns, making it easy to bootstrap new projects with sensible defaults.

In addition to the files in this directory listed in the Contents section below, it is recommended to also create the following files (consider making templates for them):

- `README.md`
- `LICENSE.md`
- `.gitignore`
- `.pre-commit-config.yaml`

## Contents

| File                                                                                   | Description                                                                                                                                     |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| [`sensible-settings-guide.md`](sensible-settings-guide.md)                             | Step-by-step guide for configuring GitHub repo settings, branch rulesets, & pre-commit.ci integration                                           |
| [`rulesets/default-branch-protections.json`](rulesets/default-branch-protections.json) | Branch ruleset: require PRs (squash only), status checks, no force-pushes/deletions on the default branch                                       |
| [`rulesets/require-my-review.json`](rulesets/require-my-review.json)                   | Branch ruleset: require CODEOWNERS review before merge (with a bypass for myself when merging my own PRs)                                       |
| [`CODEOWNERS`](CODEOWNERS) → `.github/CODEOWNERS`                                      | Template CODEOWNERS file to auto-request reviews on PRs opened by others (needed for `require-my-review`; also useful for bot PR notifications) |
