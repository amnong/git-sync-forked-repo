# git-sync-forked-repo

```
usage: git-sync-forked-repo.py [-h] target_repo_url source_repo_url

Sync branches from source repository into target repository using rebase

positional arguments:
  target_repo_url  Forked repository where new commits should be written to
  source_repo_url  Original repository where new commits should be taken from

optional arguments:
  -h, --help       show this help message and exit
```

New branches will be created, exisitng branches will be rebased.
