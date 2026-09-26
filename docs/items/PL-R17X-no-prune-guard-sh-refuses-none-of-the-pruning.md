---
id: PL-R17X
title: no-prune-guard.sh refuses none of the pruning spellings git documents beyond its four patterns: git pull --prune or -p, git remote update -p, git fetch -P, a bundled short flag such as git fetch -tp, and a prune setting passed on the command line as git -c fetch.prune=true fetch, each of which prunes unrefused
priority: P2
effort: S
status: done
classes: defect
touches: .claude/hooks/no-prune-guard.sh, tests/unit/test_no_prune_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science
added: 2026-09-26
closed: 2026-09-26
pr: 1102
payoff: a session reaching for git pull -p, git remote update -p, a bundled -tp or a prune setting passed with -c meets the refusal and the recipe git fetch --prune already gets, so no spelling git documents deletes a stale ref that may hold the only copy of an item
verify: grep -q 'def test_every_pruning_spelling_is_refused' tests/unit/test_no_prune_guard.py
recurrences: 2026-09-26 PL-YFT4 withdrawn 2026-09-26 PL-YFT4
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

**Checked 2026-09-26 against git 2.43.0 on a scratch remote** - a bare
repository outside the tree, a fresh clone for each spelling, the branch
deleted on the remote before each run. These deleted the tracking ref:
`git pull --prune`, `-p` and `-np`; `git pull --pru`, an abbreviation;
`git remote update -p` and `git remote -v update -p`; `git fetch -tp`, `-np`
and `-pj4`; `git -c fetch.prune=true fetch origin`; `git -c fetch.prune
fetch`, where a name with no `=` reads as true; `git -c FETCH.PRUNE=Yes
fetch`; `git -c remote.origin.prune=true pull`; `git
--config-env=fetch.prune=V fetch` and its two-word form; and `git fetch -p`
after each of `-C .`, `--git-dir .git`, `--work-tree .`, `--namespace x` and
`--attr-source HEAD`, so each of those five takes the next word as its value.
These deleted nothing: `git fetch -P`, `--prune-tags` and `--prune-t`; a
`pruneTags` setting alone; `-c fetch.prune=` (empty), `=off`, `=0` and
`=NO`; `git fetch -j4p` and `git pull -rp`, each an error, since the letter
taking a value takes the rest of the word; `git pull -Sp`, a key id of `p`;
`git -p fetch` and `git -P fetch`, the pager options; `git -c
fetch.prune=true status`; and `git remote prune -n`. `-P`, `--prune-tags` and
a `pruneTags` setting deleted the tag as well once pruning was on (`git fetch
-pP`, `git -c fetch.prune=true fetch -P`), and not before.

So the title's `git fetch -P` prunes nothing on its own. It is refused all the
same, as `--prune-tags` already is: pruning can be on from a config file the
hook cannot read, and one spelling of an option refused while the other passes
is the gap this item is about. The same holds for the `pruneTags` settings.

**Why it matters.** The guard exists because a stale `origin/<branch>` can be
the only surviving copy of an item captured on a branch nobody merged
(`PL-HKF4`). A guard that refuses `git fetch --prune` and passes `git pull -p`
deletes that ref as surely as having no guard, and silently: the deny message
carrying `bin/docket stranded` and the one-ref recipe never reaches the session
that needed it, and a session that has seen the refusal once can reasonably
believe pruning is fenced off.

**Done when.** Every spelling above that deleted the tracking ref is refused,
the abbreviation aside, and so are `git fetch -P` and a `pruneTags` setting
passed with `-c` or written with `git config`; the false-valued settings,
`git fetch -j4p`, `git pull -rp` and `-Sp`, `git -p fetch` and `git -P fetch`
pass, and so do `git grep -c fetch.prune` and `git commit -c HEAD`, whose
`-c` is the command's own; the hook states what stays out of reach beside its
other limits; and `tests/unit/test_no_prune_guard.py` pins both lists.

**Joined the Fix generators project's list 2026-09-26** (project owner,
2026-09-26). Asked in the project timeline whether anything else was left for
generators, the coordinator named the seven items filed overnight, this one
among them, as staying out of scope unless he added them, and the owner
answered "Add them". Recorded here by the thread that took it.
