---
id: PL-X0ND
title: quality run 2000 on main commit 25abc218 was cancelled 8s in, so that commit has no verdict, which is exactly what PL-QD9K's cancel-in-progress exemption for refs/heads/main is supposed to prevent
status: untriaged
added: 2026-09-15
---

**Problem.** quality run 2000 on main commit 25abc218 was cancelled 8s in, so that commit has no verdict, which is exactly what PL-QD9K's cancel-in-progress exemption for refs/heads/main is supposed to prevent

**Observed 2026-09-15.** The project owner merged `#595`, `#597` and `#598`
within thirteen seconds. The three `push` runs on `main`:

| run | head | started | outcome |
| --- | --- | --- | --- |
| 1999 | `84b23720` (`#595`) | 22:59:44 | in progress |
| 2000 | `25abc218` (`#597`) | 22:59:50 | **cancelled 22:59:58** |
| 2001 | `17403970` (`#598`) | 22:59:57 | pending |

So `25abc218` - the commit closing `PL-16ZC`, `PL-7G5M`, `PL-4D1M` and
`PL-JFXG` - carries no verdict at all.

**Why this should not have been possible.** `.github/workflows/quality.yml`
sets `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`, and its
comment states the reason in full: "cancelling there would mean a merge landing
while an earlier merge was still being verified silently drops that commit's
only check. Every commit on `main` keeps its own run. `PL-QD9K`." On a `push`
to `main`, `github.ref` is `refs/heads/main`, so the expression is `false` and
no run should be cancelled.

**What is not established, and must be before anything is changed.** The
cancellation source was not read. Two readings fit the timing and they want
opposite fixes:

- *Concurrency cancelled it* - the guard is not doing what its comment claims,
  and the expression or its evaluation context is wrong.
- *A person cancelled it* in the Actions UI, in which case nothing is broken
  and this item is dropped.

The pattern argues slightly against the first: run 1999 was **older** than 2000
and was not cancelled, where a concurrency group would have taken the oldest
first. That is suggestive rather than decisive - three runs in one group inside
thirteen seconds is a race, and the order runs register in is not the order they
started.

**How to settle it in one look**, which this session could not do from the API:
the run page for `35033624911` names what cancelled it. A concurrency
cancellation reads "Canceled by the concurrency group"; a manual one names the
user.

**Why it is worth settling rather than shrugging at.** A red `main` that no
pull request shows is already this repository's known blind spot - `PL-B5VM`,
`PL-Y1W6` and `PL-7VSK` are three independent captures of one instance of it
from the same hour. A `main` commit with *no* verdict is the same blind spot
with the signal removed entirely: nothing reports it, and `bin/docket`'s red-main
line reads the latest conclusion rather than asking whether every commit has
one. The tip being green afterwards hides it, because the next commit's run
proves the tip rather than the commit that was skipped.
