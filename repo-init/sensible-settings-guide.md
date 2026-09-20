# Guide to setting sensible Github repo settings

Most large Github projects use repo settings to enforce certain code & contribution standards. The following are some sensible settings that I've found worth using for my personal projects to have good default branch rules, & to make use of [`pre-commit`](https://pre-commit.com/) & [pre-commit.ci](https://pre-commit.ci/) effectively. The overarching philosophy is to automate formatting & deployment checks as much as possible, & to avoid committing directly to `main`.

- Give [pre-commit.ci](https://results.pre-commit.ci/) access to the repository
- Add [`.github/CODEOWNERS`](CODEOWNERS) so reviews are requested on all PRs (required for the `require-my-review` ruleset below)
- In `Repo > Settings`
  - `General > Pull Requests`
    - Only enable **Allow squash merging**, with the default commit message set to **Pull request title and description**
    - Enable **Always suggest updating pull request branches**
    - Enable **Allow auto-merge**
    - Enable **Automatically delete head branches**
  - `Rules > Rulesets`
    - Import both rulesets from the [`rulesets/`](rulesets/) directory via **Import a ruleset** (upload each JSON file).
    - Alternatively, create them manually as described below.
    - **`default-branch-protections`** ([`rulesets/default-branch-protections.json`](rulesets/default-branch-protections.json))
      - Set **Enforcement Status** to **Active**
      - Under **Target branches**, select **Include default branch** (i.e., `main`)
      - Under **Rules > Branch rules**
        - Enable **Restrict deletions**
        - Note on **Require signed commits**:
          - I would prefer for this to be enabled, but for now I disabled it because some "auto fix" PRs from tools ([example](https://github.com/izzygomez/izzygomez.github.io/pull/10)) may be unsigned, which would block merges. My own commits _should_ be verified automatically [per this config](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/gitconfig#L16).
        - Enable **Require a pull request before merging**
          - Most sub-options here are not necessary for personal projects, since I'm the only contributor, though they are sensible elsewhere.
          - Enable **Dismiss stale pull request approvals when new commits are pushed**
          - Enable **Require extra approval for unattributed changes** (so Copilot-or-similar commits can't slip through without another look)
          - Under **Allowed merge methods**, select only **Squash**
        - Enable **Require status checks to pass**
          - Enable **Require branches to be up to date before merging**
          - Add **pre-commit.ci - pr** as a required check. This check only appears after it has run at least once, so a dummy PR may be needed.
        - Enable **Block force pushes**
    - **`require-my-review`** ([`rulesets/require-my-review.json`](rulesets/require-my-review.json))
      - Purpose: make the GitHub UI show **Review required** before merging, so bot PRs aren't one-click mergeable. Pair with [`.github/CODEOWNERS`](CODEOWNERS).
      - Set **Enforcement Status** to **Active**
      - Under **Target branches**, select **Include default branch**
      - Under **Rules > Branch rules**, enable **Require a pull request before merging** with **Require review from Code Owners**
      - Under **Bypass list**, add yourself with **Allow this actor to bypass...** set to **Pull requests** — so you can still merge your own PRs via the **Merge without waiting for requirements to be met (bypass rules)** checkbox when you don't need a formal self-approval
      - If importing the JSON, confirm the `bypass_actors` entry matches your user (the export is keyed to my account id)
    - Click **Create/Save changes** for each ruleset
- I find it useful to include documentation in a repo's `README` & config files on how `pre-commit` is used. See [here](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/README.md?plain=1#L75-L77) & [here](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/.pre-commit-config.yaml#L1-L13) for some examples.
