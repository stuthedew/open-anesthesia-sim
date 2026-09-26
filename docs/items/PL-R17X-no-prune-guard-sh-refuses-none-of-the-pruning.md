---
id: PL-R17X
title: no-prune-guard.sh refuses none of the pruning spellings git documents beyond its four patterns: git pull --prune or -p, git remote update -p, git fetch -P, a bundled short flag such as git fetch -tp, and a prune setting passed on the command line as git -c fetch.prune=true fetch, each of which prunes unrefused
status: untriaged
added: 2026-09-26
---

**Problem.** no-prune-guard.sh refuses none of the pruning spellings git documents beyond its four patterns: git pull --prune or -p, git remote update -p, git fetch -P, a bundled short flag such as git fetch -tp, and a prune setting passed on the command line as git -c fetch.prune=true fetch, each of which prunes unrefused

**Found 2026-09-26 while working `PL-WGFY`**, by piping each command as a hook
payload into `bash .claude/hooks/no-prune-guard.sh` on its branch. All seven
are allowed:

    git pull --prune
    git pull -p
    git remote update -p
    git fetch -P
    git fetch -tp
    git -c fetch.prune=true fetch origin
    git -c remote.origin.prune=true pull

git 2.43's own usage lines say each prunes: `git pull -h` and `git fetch -h`
list `-p, --[no-]prune` ("prune remote-tracking branches no longer on
remote"), `git fetch -h` lists `-P, --[no-]prune-tags`, and `git remote -h`
lists `update [-p | --prune]`. The guard's four patterns name `fetch`, `remote
prune`, `remote update --prune` and `config`, with `-p` only as a word of its
own and `--prune-tags` but not its short form. These misses predate `PL-WGFY`,
which kept the four shapes as they were.

**Generator check.** One-off: the guard's list of spellings is incomplete,
which is not a fact another reader misreads.
