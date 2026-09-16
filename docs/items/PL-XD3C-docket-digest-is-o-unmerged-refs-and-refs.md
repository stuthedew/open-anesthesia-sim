---
id: PL-XD3C
title: docket digest is O(unmerged refs) and refs accumulate without bound, so session start gets slower every month on a long-lived clone and never on a fresh container
status: untriaged
added: 2026-09-16
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
