# Gists

Miscellaneous scripts, notes, & one-off utilities.

## Why & how this repo was created

I migrated my gists from [gist.github.com/izzygomez](https://gist.github.com/izzygomez) into this repo to get full repo features, such as a directory structure, grepability across files, & easier syncing of gist changes across machines. Since each gist.github.com gist is already a full git repo, I wrote `import_gists.py` to preserve commit history during the migration. It:

1. Clones each gist
2. Rewrites gist commit messages ([using `git-filter-repo`](https://github.com/newren/git-filter-repo)) to be more descriptive; otherwise, the commit messages were empty
3. Merges into this repo

Usage:

```bash
mkdir gists && cd gists
git init
python import_gists.py gists_to_import.txt
```

The `gists_to_import.txt` file is a list of `<filename> <gist_id>` pairs, where:

- `<gist_id>` is the ID in the gist URL
- `<filename>` is the gist filename & what it will be called in the repo

Requires `git-filter-repo` (`brew install git-filter-repo`). Only single-file gists are supported.

## TODOs

- write a blog post on website about how this repo was created
- consolidate all `.pre-commit-config.yaml` files across my repos into `repo-settings/`
- consolidate all colors in scripts to a single file that is imported
