---
id: PL-0J9K
title: Replace docket's per-blob git show fan-out with one git cat-file --batch: 389 processes and 5.77s of a 24s session start on the owner's machine
status: untriaged
added: 2026-09-16
---

**Problem.** Replace docket's per-blob git show fan-out with one git cat-file --batch: 389 processes and 5.77s of a 24s session start on the owner's machine

**Problem.** `subprojects/docket/src/docket/vcs.py` reads a committed blob by
spawning `git show <rev>:<path>`, one process per blob, at seven call sites -
lines 926, 1075, 2165, 2552, 2802, 3069 and 3191 - most of them inside a loop
over item files. Measured 2026-09-16 on the same commit and store:

| | session container | owner's macOS clone |
| --- | --- | --- |
| `show` calls per `docket digest` | 18 | **389** |
| time in `show` | 0.05 s | **5.77 s** |
| share of the whole `digest` | 2% | **24%** |

**The fix is the standard one and changes no semantics.** `git cat-file --batch`
takes `<rev>:<path>` lines on stdin and returns every blob from a single
process. 389 spawns become 1. The bytes are identical - it is the same object
lookup - so no caller's behaviour changes and no output moves.

**Two things to get right.** A missing path makes `cat-file --batch` print
`<spec> missing` on stdout rather than failing, where `git show` exits non-zero;
whatever `vcs.py` does today with a blob that is absent at that rev has to keep
happening, and that is the behaviour the test should pin. And the batch process
has to be scoped to one command and closed, for the reason `PL-MMVF` gives about
a cache outliving a fetch.

**Why this one first.** It is the largest single block after `diff`, it is a
mechanical substitution against a documented git interface, and unlike `PL-XD3C`
it needs no design round. Sequenced after `PL-XD3C`'s ref count is verified,
because if the ref count turns out not to be the driver then these 389 calls
were never going to be 389.

**Done when** `docket digest` spawns one `cat-file` process where it now spawns
one `show` per blob, the digest's output is byte-identical on both machines, the
missing-blob path is covered by a test, and the item records the re-measured
`show` time on the owner's clone.

---

**Done, 2026-09-16.** `GitRunner` in `subprojects/docket/src/docket/vcs.py`
answers `show <rev>:<path>` from one `git cat-file --batch` per checkout,
started on first use and closed from `main`'s `finally` so a command that
raised still ends it. No call site changed: the runner is a `Runner` like
`_run_git`, so all seven sites and their absent-blob handling are untouched.

**The missing-path hazard, and what testing it actually showed.** `git show`
exits 128 and `_run_git` turns that into the empty string; `cat-file --batch`
prints `<spec> missing` on stdout. That line is read and returns the same empty
string. But mutation testing found that *deleting* the branch leaves every
caller's answer correct - an unreadable header drops the batch and `git show`
answers instead - so correctness alone cannot tell the two apart. What it
actually costs is the batch, for every later blob in the command, and an absent
blob is ordinary here rather than rare. The test pins the process count for that
reason, which is the only place the difference shows.

Two shapes decline rather than guess: anything that is not a blob, because
`git show` formats a tree where `cat-file` returns its raw bytes, and a spec
carrying the newline the protocol delimits on.

**Re-measured.** On this container `show` is 25 asked, 22 reaching git, 21 of
them folded into the batch - 0.02 s. The container was never where this item's
value lay: `show` is 1.0 call per item file an unmerged ref introduces, so it is
15-25 calls here and 389 on the owner's clone. The premise survives; only its
container share was misleading.

**Still owed:** the re-measured `show` time on the owner's clone, from
`bin/docket digest --profile` run there.

**Correction, same day: "1.0 per item edit" is a marginal rate, not the driver.**
An independent pass refuted it and the refutation holds. Attributing every `show`
to the line that issued it, on this container:

| call site | calls |
| --- | --- |
| `_queue_only_work` | 16 |
| `_title_at`, via `stranded` | 5 |
| `_closed_on_base` | 3 |
| `released_on_base` | 1 |

So `show` is a sum over four differently-driven collections, and only the largest
loops over `walk.edited`. The 1.0 slope measured by fabricating ref sets is
sound for what it measured - each synthetic commit touched exactly one item file,
so each added one `_queue_only_work` call - but it predicts the *marginal* call
and not the total, and the three other terms have their own inputs. Anyone
predicting a count from it will be wrong the way this item's own history was
wrong, which is why the correction is here rather than left implied.

Nothing shipped changes: the batch folds every `show` whatever line issued it,
and the four sites were already covered.
