---
id: PL-MMVF
title: docket digest spawns 192 git subprocesses of which 82 are exact duplicates, so a machine that charges for exec pays 17.6s at every session start
status: untriaged
added: 2026-09-16
---

**Problem.** docket digest spawns 192 git subprocesses of which 82 are exact duplicates, so a machine that charges for exec pays 17.6s at every session start

**Measured 2026-09-16**, by putting a logging shim ahead of `git` on `PATH` and
running `bin/docket digest` once, at commit `9c9a3aa`, with 18 remote branches
and 1,073 item files:

| subcommand | calls | distinct argv | wasted |
| --- | --- | --- | --- |
| `diff` | 85 | 51 | 34 |
| `merge-base` | 48 | 16 | **32 (67%)** |
| `ls-tree` | 25 | 22 | 3 |
| `show` | 17 | 15 | 2 |
| `for-each-ref`, `rev-parse`, `rev-list`, `log` | 17 | 6 | 11 |
| **total** | **192** | **110** | **82 (43%)** |

The repeats are byte-identical argv in the same process against the same
refs - `merge-base origin/main <ref>` asked three times for the same `<ref>`,
`diff --raw --no-renames --no-abbrev <base> <ref> --` asked twice. Nothing
between them can have changed the answer: `vcs.py` already documents that this
module never fetches and that its refs "can be stale by exactly one fetch",
so within one `digest` the ref set is fixed by construction.

**Why it is worth fixing rather than accepting.** The store read is not the
cost - 1,073 files and 5.1 MB parse in 0.019 s - and neither is the network,
which `digest` never touches. The whole of `digest` is git process spawns, so
its cost is `192 x (per-spawn cost)` and the only two levers are the count and
the per-spawn price. The count is this item. The price is the machine's, and
the spread is enormous: 2.1 ms per trivial `git` subprocess in a session
container against **~92 ms on the project owner's macOS machine**, where the
same 192 spawns take **17.64 s of a 20.01 s session start** - 88% of it. Every
session pays this before its first turn, on the one command the session-start
hook exists to run.

**The fix, and its bound.** Memoize the runner in
`subprojects/docket/src/docket/vcs.py` on the argv tuple for the lifetime of
one process. That is 43% of the spawns on today's store and needs no change to
any caller or to what `digest` prints - the same bytes come back, because they
are the same command. It does **not** reach the other 110, so it is worth about
7.6 s of the owner's 17.6 s and about 0.7 s of a container's 1.55 s. Removing
the remaining redundancy - 51 distinct `diff` calls and 16 distinct
`merge-base` calls for 19 branches is still more than one question per branch -
is a second, larger change and belongs in its own item if this one shows it is
worth it.

**Beware the cache that outlives the question.** A memo keyed on argv is only
sound inside a single read-only command. `bin/docket branch` and the hook's
`--unshallow` both fetch, so a cache shared across a fetch would answer from
before it. Scope it to the process, and hold that with a test.

**Done when** `docket digest` makes at most 110 git subprocesses on a store
where it now makes 192, the digest's output is unchanged, a test pins the
cache to one process, and the item records the re-measured wall time on both
machines.
