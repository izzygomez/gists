# Sensible Github repo settings

Most large Github projects use repo settings to enforce certain code & contribution standards. The following are some sensible settings that I've found worth using for my personal projects to have good default branch rules, & to make use of [`pre-commit`](https://pre-commit.com/) & [pre-commit.ci](https://pre-commit.ci/) effectively. The overarching philosophy is to automate formatting & deployment checks as much as possible, & to avoid committing directly to `main`.

* Give [pre-commit.ci](https://results.pre-commit.ci/) access to repository
* In `Repo > Settings`
  * `General > Pull Requests`
    * Only enable "Allow squash merging" with "Default commit message" set to "Pull request title and description"
    * Enable "Always suggest updating pull request branches"
    * Enable "Allow auto-merge"
    * Enable "Automatically delete head branches"
  * `Branches > Branch Protection Rules > main`
    * Enable "Require a pull request before merging"
      * None of the sub-options here ("Require approvals", etc) are necessary for personal projects since I'm the only contributor, but they are sensible elsewhere. What we really care about is enforcing PRs instead of direct `main` pushes.
    * Enable "Require status checks to pass before merging"
      * Enable sub-option "Require branches to be up to date before merging"
      * Add "pre-commit.ci - pr" as a required check. Note that this check will only become available in the search bar if it has run at least once before, so one might need to create a dummy PR to trigger this if necessary.
    * Note on "Require signed commits"
      * I would prefer for this to be enabled, but for now I disabled this because it is possible for some "auto fix" PRs from tools ([see here for an example](https://github.com/izzygomez/izzygomez.github.io/pull/10)) to be unsigned, which would block mergeability. For what it's worth, my own commits _should_ be verified automatically [per this](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/gitconfig#L16).
    * Enable "Do not allow bypassing the above settings"
    * Enable "Allow force pushes" only for myself
    * Click "Save Changes"
* I find it useful to include documentation in a repo's `README` & config files on how `pre-commit` is used. See [here](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/README.md#L75-L77) & [here](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/.pre-commit-config.yaml#L1-L13) for some examples.