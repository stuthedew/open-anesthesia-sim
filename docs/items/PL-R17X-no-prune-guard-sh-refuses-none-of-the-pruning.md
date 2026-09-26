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

**Read before the fix, 2026-09-26, from git 2.43's usage lines** (`git fetch
-h`, `git pull -h`, `git remote -h`), by the thread that claimed it and
stopped for length before starting:

- `fetch` prunes with `-p`, `-P` (`--prune-tags`), `--prune` and
  `--prune-tags`. Its short options taking a value are `-j <n>` and
  `-o <server-option>`; the rest (`v q a f m t k u n 4 6`) take none.
- `pull` prunes with `-p` and `--prune`, and lists no prune-tags form. Its
  short options taking a value are `-r[=...]`, `-s <strategy>`, `-X <option>`,
  `-S[=<key-id>]`, `-j[=<n>]` and `-o <server-option>`.
- `remote update` prunes with `-p` as well as `--prune`.
- A bundle such as `-tp` prunes where `p` (or `P`, for `fetch`) comes before
  the first letter that takes a value, since that letter takes the rest of the
  word.
- `-c <name>=<value>` and `--config-env=<name>=<envvar>` are global options,
  before the subcommand. A prune setting there prunes unless its value reads
  false (empty, `false`, `no`, `off`, `0`). Finding where the global options
  end means stepping over the ones that take a separate value (`-C`, `-c`,
  `--config-env`, `--git-dir`, `--work-tree`, `--namespace`), and `-p` and
  `-P` there mean `--paginate` and `--no-pager`, not pruning.
- `PRUNE_SETTING` misses `fetch.pruneTags` and `remote.<name>.pruneTags`,
  both documented, because `\b` does not match between `prune` and `Tags`.
  That reaches the existing `config` shape too. git reads a setting's section
  and key without regard to case, so the match should as well.
- Out of reach, to be stated beside the other limits rather than handled:
  aliases, settings passed through `GIT_CONFIG_PARAMETERS` or
  `GIT_CONFIG_COUNT`, and abbreviated long options such as `--prune-t`.
- The hook refuses these spellings in any Bash command, so running real git on
  a scratch repository to confirm one has to go through a script file. The
  tests pipe payloads and run no git.
- The hook's Python sits inside single quotes in bash, so an apostrophe
  anywhere in it breaks every Bash call; check the file with `bash -n` after
  each edit.
