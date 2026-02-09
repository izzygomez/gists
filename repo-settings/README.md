# Github repo settings

A collection of standardized files & documentation for jumpstarting new GitHub repositories.

## Philosophy

When creating a new repo, there's a set of configurations, settings, & files that I find myself repeatedly setting up. This directory serves as a central reference & source of truth for those patterns, making it easy to bootstrap new projects with sensible defaults.

The goal is to:

- **Automate** formatting, linting, & deployment checks as much as possible
- **Standardize** contribution workflows across personal projects
- **Document** the reasoning behind these choices for future reference

## Contents

| File                                                       | Description                                                                                                |
| ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| [`sensible-settings-guide.md`](sensible-settings-guide.md) | Step-by-step guide for configuring GitHub repo settings, branch rulesets, & pre-commit.ci integration      |
| [`main.json`](main.json)                                   | Exportable GitHub branch ruleset that can be directly imported into a repo's `Settings > Rules > Rulesets` |
| [`CODEOWNERS`](CODEOWNERS)                                 | Template CODEOWNERS file to auto-request reviews on all PRs (useful for getting notified of bot PRs)       |
