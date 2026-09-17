---
id: PL-MMVF
title: docket digest spawns 192 git subprocesses of which 82 are exact duplicates, so a machine that charges for exec pays 17.6s at every session start
priority: P2
effort: M
status: done
classes: session-cost, perf
feature: session-start-cost
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_git_runner.py
added: 2026-09-16
closed: 2026-09-17
verify: uv run pytest subprojects/docket/tests/test_git_runner.py && grep -q 'def test_the_memo_does_not_answer_from_before_a_fetch' subprojects/docket/tests/test_git_runner.py
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

**Correction, same day: 43% of the calls is not 43% of the time.** The first
measurement above counted calls. Timing each one individually gives the value
of the memo directly, and it is smaller than the call count implies, because
the duplicated calls skew cheap:

| | calls | replay time |
| --- | --- | --- |
| all git calls in one `digest` | 220 | 1.21 s |
| of which exact repeats | 90 (41%) | **0.57 s (47%)** |

So on a container the memo is worth 0.57 s of `digest`'s 2.08 s - **27%**, not
43%. It happens to land better than the call count suggested rather than worse,
because the single most expensive repeat is `rev-list --objects origin/main`
asked three times at ~0.08 s each. The claim to hold this item to is the 27%,
and the same measurement has to be re-run on the slow machine before the item
is worked, because nothing guarantees the ratio survives a 6.4x slower git.

**And the per-spawn story in the section above is wrong.** It inferred ~92 ms
per spawn from `digest`'s wall time divided by the call count. Measured
directly on the owner's machine: `/bin/echo` 2.9 ms, `git rev-parse HEAD`
12.8 ms, no `xcrun` shim. 220 x 12.8 ms is about 2.8 s, which is a sixth of
that machine's 17.64 s, so process creation is a minor term and the rest is git
doing work - disk, not spawn. What is actually slow there is still open at the
time of writing; `PL-JH3T` carries it.

**Measured on the slow machine, 2026-09-16: 10%, not 27%.** The correction above
asked for exactly this re-measurement before the item is worked, and it came
back lower again. On the owner's clone `digest` makes 1,107 git calls of which
**151 are exact repeats costing 2.37 s** - 14% of the 17.25 s replay, and 10% of
the 24.19 s command. On a container it is 27%. The memo is worth less where it
would help most, because that machine's extra calls are overwhelmingly *distinct*
ones, not repeats.

So the honest figure to hold this item to is **10% on the machine that pays**,
and it is now the smallest of the three levers: `PL-0J9K` (batch the blob reads
into one `cat-file`) is 24% and mechanical, and `PL-XD3C` (the ref-count growth)
is the one that decides whether any of this stops mattering. Do this one last,
or fold it into whichever of those two is worked first - it is a few lines
inside the same runner either way.

---

**Done, 2026-09-16, and the duplication is structural rather than incidental.**
`GitRunner` memoizes on `(argv, root)`. Dumping the argv of a real `digest` run
settles what the three earlier estimates - 43% of calls, then 27% of time, then
10% - were circling: **every `merge-base` this module issues is asked exactly
three times.** 18 calls, 6 distinct, multiplicity 3 for every one of them.
`_unlanded_refs` runs once each for `branches_in_flight`, `orphaned` and
`cuts_in_flight`, and the same three-fold repeat covers the `diff --raw` shape.

So the memo is not a guess at a rate. On this container `merge-base` goes 51
asked to 17 ran and `diff` 96 to 60, and the whole command 217 asked to 130 -
87 calls the memo answered, 40%.

**It does not reach `show`, and that is the finding to carry forward.** 22 of 25
`show` calls are distinct, because each asks for a different blob. A memo cannot
help there, which is what makes `PL-0J9K`'s batch the only lever on that block
and the two items genuinely separate rather than overlapping.

**The fetch hazard is closed twice.** The memo covers only subcommands that
cannot change anything, whatever their arguments; anything else - `fetch` among
them - is run *and* empties it. A test drives that against a real remote that
really moves, rather than asserting the clearing rule against itself, because
`bin/docket branch` fetches in-process.

**Why it matters.** The duplication turned out to be structural rather than
incidental - every `merge-base` this module issues is asked exactly three times,
because `_unlanded_refs` runs once each for `branches_in_flight`, `orphaned` and
`cuts_in_flight` - so it was a fixed multiple paid at every session start rather
than a rate that might drift away on its own.

**Closed at triage, 2026-09-17.** `GitRunner` memoizes on `(argv, root)` on
`origin/main`, landed by `#635` and pinned by
`subprojects/docket/tests/test_git_runner.py`, including the fetch hazard the
brief names. The item was never taken out of `untriaged`.

The three estimates this brief carried and corrected - 43% of calls, 27% of
time, then 10% on the machine that pays - are left as written. They are the
reason `--profile` exists, and the last of them is why this was the smallest of
the three levers rather than the first.
