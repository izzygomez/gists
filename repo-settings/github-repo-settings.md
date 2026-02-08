# Sensible Github repo settings

Most large Github projects use repo settings to enforce certain code & contribution standards. The following are some sensible settings that I've found worth using for my personal projects to have good default branch rules, & to make use of [`pre-commit`](https://pre-commit.com/) & [pre-commit.ci](https://pre-commit.ci/) effectively. The overarching philosophy is to automate formatting & deployment checks as much as possible, & to avoid committing directly to `main`.

* Give [pre-commit.ci](https://results.pre-commit.ci/) access to the repository
* In `Repo > Settings`
  * `General > Pull Requests`
    * Only enable **Allow squash merging**, with the default commit message set to **Pull request title and description**
    * Enable **Always suggest updating pull request branches**
    * Enable **Allow auto-merge**
    * Enable **Automatically delete head branches**
  * `Rules > Rulesets > New ruleset`
    * The remaining bullet points describe the desired ruleset options. For convenience, you can instead use **Import a ruleset** and upload [this file](https://gist.github.com/izzygomez/d6ad67417b61d7238013f138436f1028). `"source"` will be filled in automatically when the file is uploaded.
    * Create a ruleset named **main**
    * Set **Enforcement Status** to **Active**
    * Under **Target branches**, select **Include default branch** (i.e., `main`)
    * Under **Rules > Branch rules**
      * Enable **Restrict deletions**
      * Note on **Require signed commits**:
        * I would prefer for this to be enabled, but for now I disabled it because some "auto fix" PRs from tools ([example](https://github.com/izzygomez/izzygomez.github.io/pull/10)) may be unsigned, which would block merges. My own commits _should_ be verified automatically [per this config](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/gitconfig#L16).
      * Enable **Require a pull request before merging**
        * Most sub-options here are not necessary for personal projects, since I'm the only contributor, though they are sensible elsewhere.
        * Under **Allowed merge methods**, select only **Squash**
      * Enable **Require status checks to pass**
        * Enable **Require branches to be up to date before merging**
        * Add **pre-commit.ci - pr** as a required check. This check only appears after it has run at least once, so a dummy PR may be needed.
      * Enable **Block force pushes**
    * Click **Save changes**
* I find it useful to include documentation in a repo's `README` & config files on how `pre-commit` is used. See [here](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/README.md?plain=1#L75-L77) & [here](https://github.com/izzygomez/dotfiles/blob/d8c05294d541964b80bbb4818339cf27098e194b/.pre-commit-config.yaml#L1-L13) for some examples.