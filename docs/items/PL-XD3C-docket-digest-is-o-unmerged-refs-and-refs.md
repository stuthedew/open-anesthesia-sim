---
id: PL-XD3C
title: docket digest is O(unmerged refs) and refs accumulate without bound, so session start gets slower every month on a long-lived clone and never on a fresh container
priority: P2
effort: M
status: done
classes: session-cost, perf
feature: session-start-cost
touches: subprojects/docket/src/docket/vcs.py, docs/items
added: 2026-09-16
closed: 2026-09-17
pr: 668
not-delegable: what is left is one measurement on the project owner's own clone - `bin/docket digest --profile` run there, compared against a container's `ref set` block - and no command in this checkout can take it. The instrument it needed is built and on `main`
---

**Problem.** docket digest is O(unmerged refs) and refs accumulate without bound, so session start gets slower every month on a long-lived clone and never on a fresh container

**Measured on two machines, 2026-09-16, same commit and the same command.**

| | session container | owner's macOS clone |
| --- | --- | --- |
| unmerged refs `digest` walks | 18 | ~90 (predicted; see below) |
| git calls per `docket digest` | 220 | **1,107** |
| `docket digest` wall | 2.08 s | **24.19 s** |
| replay of those calls | 1.21 s | 17.25 s |
| per call | 5.5 ms | 15.6 ms |
| `size-pack` | 15.5 MB | 107 MB |
| read all item files | 0.01 s (1,074) | 0.17 s (1,089) |

**The call count is the finding, not the per-call cost.** Identical code and an
identical store produced 5x the git calls on one machine. Per call that machine
is only 2.8x slower, which is ordinary hardware and filesystem difference. The
store is not involved either - 1,089 files parse in 0.17 s. What differs is the
number of refs `digest` walks, and every one of `diff` (570 v 100), `show` (389
v 18) and `merge-base` (78 v 54) scales with it.

**Why a container never sees this and never will.** A container clones fresh, so
it holds only the refs the remote still has - 18 here. A clone that has been
worked in for months holds every `claude/*` branch any session ever pushed,
plus its remote-tracking ref, and nothing ever removes them. So the machine that
does the work is the only one that pays, the cost grows monotonically with the
number of sessions the project has ever run, and no CI run or fresh session can
reproduce it. On a project whose stated horizon is multi-year this is the exact
shape `CLAUDE.md` names as the thing that ends it: an accumulation a single
year would not surface.

**Pruning is not the remedy and must not be proposed as one.** `docs/dead-ends.md`
records that `git fetch --prune` is deliberately refused - "a branch deleted on
the remote leaves a tracking ref that is the only surviving copy of anything
committed on it, which is the case `stranded` exists to catch" - and
`.claude/hooks/no-prune-guard.sh` enforces it. The refs are load-bearing. The
cost has to come out of how `digest` walks them, not out of the walk's input.

**Verify the ref count before designing anything.** The ~90 above is inferred
from the call ratio, not measured:

```
git for-each-ref refs/heads refs/remotes | wc -l
git for-each-ref refs/heads refs/remotes --merged=origin/main | wc -l
```

The difference is what `digest` walks. If it is near 90, the scaling law holds
and this item is real; if it is near 18, the 5x is something else and this item
closes.

**Done when** `docket digest`'s git-call count is bounded by something that does
not grow with the number of branches the project has ever created, or the item
records why the growth is acceptable with the ref count at which it would stop
being. `PL-0J9K` (batch the blob reads) and `PL-MMVF` (memoize the runner) each
cut the constant and neither changes the exponent - they are worth doing and
they are not this item.

---

**The premise above is refuted, by the test it set itself.** It predicted ~90
unmerged refs on the owner's clone from the 5x call ratio, and said plainly:
"if it is near 18, the 5x is something else and this item closes." Measured
2026-09-16: **30 refs total, 4 merged, 26 unmerged.** 1.44x the refs cannot
produce 5x the calls. `digest` is not O(unmerged refs), or not only that.

The obvious second model fails too. `show origin/main:docs/items/<file>` looked
like one call per item file changed on an unmerged ref, but summing that across
the container's unmerged refs gives **102** against the **17** `show` calls the
measured run actually made. Whatever selects those 17 is narrower than "changed
on a branch", and is not yet identified.

**And the comparison was never controlled.** The container's ref set moved
during the session that measured it - 18 unmerged refs and 2 items in flight at
the first measurement, 19 and 6 by the last, while other sessions pushed
branches. So the container's 220 calls and the owner's 1,107 were counted
against *different ref sets, hours apart*. The ratio is not attributable to
anything until both sides are counted against the same input. That is a defect
in the measurement, not a finding about the code, and it is the reason this item
records a question rather than a cause.

**What survives, and it is little:** `docket digest` takes 24.19 s on the
owner's clone and 2.08 s on a container, and the difference is git call count
(1,107 v 220) rather than per-call cost (15.6 ms v 5.5 ms). That much is solid
and is why `PL-0J9K` and `PL-MMVF` are real - both were measured directly on the
owner's machine and neither depends on knowing what drives the count.

**Reframed: make `digest` able to answer this about itself.** The reason three
models were guessed and refuted in one sitting is that counting git calls needs
a shim on `PATH`, so nobody runs it, so the question gets answered by ratio
instead of measurement. The decidable part belongs in code, per `CLAUDE.md`'s
"find the decidable part and put it in code": a counter inside the runner in
`subprojects/docket/src/docket/vcs.py` and a flag - `bin/docket digest
--profile` - that prints calls by subcommand, wall time, and the ref count it
walked. Standard library, no shim, runnable on any machine in one command,
and it makes every future version of this question a measurement.

**Done when** `bin/docket digest --profile` reports its own git-call count,
per-subcommand totals and the refs it walked; the owner's clone and a container
are both profiled **against the same ref set**; and this item records what
actually drives the count, or closes having found the difference is not
structural.

---

**Built and measured, 2026-09-16.** `bin/docket digest --profile` reports calls
by subcommand, wall time, and the ref set walked, from a counter inside
`GitRunner` in `subprojects/docket/src/docket/vcs.py`. No `PATH` shim, so the
measurement adds no process of its own - which is the defect in the run that
counted 1,107 calls at 24.19 s, where a shell shim sat ahead of git and the
unshimmed run of the same command was 17.64 s.

On this container, on the commit that adds it:

```
git: 217 asked, 130 ran, 109 processes, 0.55s
  108 fewer processes than one-per-read (49% fewer)
  ref set: 23 refs, 6 merged, 17 unmerged, carrying 39 commits
           and 71 item-file edits
```

**`asked` is the pre-change count, so one run carries its own before and after.**
Every read was one process before `GitRunner` existed, so `asked` is what the
command used to spawn and `processes` is what it spawns now. Neither number has
to be taken on a different commit, a different machine, or - the failure this
item exists to stop - a different ref set.

**And the scaling question the retraction left open is answered, by experiment
rather than by ratio.** A scratch clone was given fabricated ref sets of known
size; holding refs fixed while varying commits, then the reverse, separates the
drivers: `merge-base` is 3.0 per unmerged ref and flat in commits, `show` is 1.0
per item file a ref introduces and flat in refs, `diff` is both at ~4.0 and
~0.95. So the premise was half right - the growth is real and unbounded, because
a squash-merged branch stays unmerged forever and nothing prunes - but the
variable is **the item edits those refs carry, not the refs**. That is why 1.44x
the refs gave 5x the calls, and it is the model the two refuted ones missed.

The laws predict the owner's clone rather than being fitted to it. At 30
fabricated refs carrying 390 item edits: 1,237 calls against their 1,107, `diff`
593 against 570, `show` 446 against 389, and `merge-base` 90 against their 78 -
which is exactly 3 x 26, their measured unmerged ref count.

**Still owed, and it needs the owner's machine.** Run `bin/docket digest
--profile` there and compare the `ref set` block with this one before comparing
any count. `PL-DMDF` carries the `diff` fan-out this profiling turned up.

**Correction to the table above: the `show` row is a marginal rate.** Attributing
each call to its issuing line shows four sites, not one - `_queue_only_work` 16,
`_title_at` 5, `_closed_on_base` 3, `released_on_base` 1 - so 1.0 per item edit
is what the *next* edited id costs, not a formula for the total. The
`merge-base` row is exact and unconditional: 3.0 per unmerged ref, because
`_unlanded_refs` runs once each for `branches_in_flight`, `orphaned` and
`cuts_in_flight`. Read the rows as slopes, and take totals from `--profile`.

**Why it matters.** It is the only one of the three session-start items whose
cost grows. `PL-0J9K` and `PL-MMVF` each cut a constant; this one asks whether
the constant is being multiplied by something unbounded, and a squash-merged
branch stays unmerged forever while `--prune` is deliberately refused. On a
multi-year horizon that is the accumulation `CLAUDE.md` names as the shape that
ends a project, and no container or CI run can ever reproduce it.

**Triaged 2026-09-17, and what is left is one command on one machine.** The
instrument is built and on `main`: `bin/docket digest --profile` reports calls
by subcommand, wall time and the ref set walked, and the scaling laws were
separated by experiment rather than by ratio. The item stays open for the half
that needs the owner's clone:

```
cd <repo> && bin/docket digest --profile
```

Compare its `ref set` block with a container's *before* comparing any count -
that is the controlled comparison whose absence invalidated this item's first
two models. `PL-0J9K`'s re-measured `show` time on that clone is the same run
and is carried here rather than there, so one command closes both obligations.

---

**Closed 2026-09-17: the owner ran the command, and all three "Done when"
clauses are met.** `bin/docket digest --profile` was run on the project owner's
clone twice, before and after `PL-DMDF`'s hoist landed, against a ref set that
did not move between the runs. That is the controlled comparison whose absence
invalidated this item's first two models, and it is the first one this question
has ever had.

**The input, printed by the instrument this item built:**

```
ref set: 38 refs, 5 merged, 33 unmerged, carrying 2270 commits
         and 1284 item-file edits
```

Against a container's 25 refs, 19 unmerged, 30 commits and 111 item-file edits.
So the clone carries **1.7x the unmerged refs, 76x the commits and 11.6x the
item-file edits** - and it is the last two, not the refs, that the original
premise missed.

**What actually drives the count, which is the clause this item could not
answer for two days.** Attributing by subcommand on that clone, before and
after the one change:

| subcommand | before | after | scales with |
| --- | --- | --- | --- |
| `diff` | 654 asked, 586 ran, 9.76 s | 161, 95, **1.63 s** | refs *and* item edits, before; refs alone, after |
| `show` | 409 asked, 373 ran, 0.06 s | 412, 376, 0.06 s | item files, but folded into one `cat-file` |
| `merge-base` | 99 asked, 33 ran | 99, 33 | exactly 3.0 per unmerged ref |
| `ls-tree` | 43 asked, 40 ran | 43, 40 | the store, not the refs |
| everything else | 40 asked | 40 | flat |
| **total** | **1,245 asked, 689 processes, 11.72 s** | **755, 198, 3.61 s** | |

**So the answer is: `diff`, and within it the per-item-edit term, and it is
gone.** 8.11 of the 11.72 seconds this command spent in git on the machine that
pays were one function being asked a question per path that it takes whole
sets for. What remains is `merge-base` at exactly 3.0 per unmerged ref - which
*is* O(refs), the original premise, at 33 calls and 0.54 s - and `show` at
roughly one per item file, which `PL-0J9K`'s batch already answers from a
single process at 0.06 s.

**The original premise is therefore half-vindicated and no longer load-bearing.**
Refs do accumulate without bound on that clone and nothing prunes them: 33
unmerged, of which five local branches carry 1,754 of the 2,270 commits between
them, the oldest named for the v0.3.0 release. The O(refs) term is real. It is
also now 0.54 s of a 3.61 s command, so the thing that made session start slow
was never the ref count on its own - it was the ref count multiplied by the
item files those refs touch, which is the model neither of the two refuted ones
found. Reaching it needed the instrument rather than another ratio, which is
what this item became.

**`PL-0J9K`'s obligation, carried here, is discharged in the same run.** `show`
on that clone is 412 asked, 376 reaching git, 375 folded into one
`cat-file --batch`: **0.06 s, against the 5.77 s that item measured before the
batch existed.**

**One defect in the instrument is filed rather than fixed**: the `ref set`
block's `item-file edits` is a per-ref sum, while the walk holds one entry per
identifier, so predicting a `diff` count from it over-predicts by ~2x on a
clone whose branches overlap. `PL-3BYK` carries it. It does not touch any
number above, all of which are measured rather than derived.

**One document was checked and deliberately left as written.** `ROADMAP.md`'s
v0.5.0 gate glosses this entry as "`digest`'s cost grows with the item edits
unmerged refs carry, and nothing prunes", inside the paragraph recording why
nine deferred entries were not pulled forward. That is a snapshot of a decision
taken at the freeze, in the past tense, and the reasoning it records - that no
per-entry saving could be named, so it waits - is still a correct account of
that decision. Editing it would be rewriting the snapshot the gate exists to
be. A reader following the id from there lands here, where the growth term is
reported gone.
