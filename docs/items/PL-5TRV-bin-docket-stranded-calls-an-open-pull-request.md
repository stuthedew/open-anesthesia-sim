---
id: PL-5TRV
title: bin/docket stranded calls an open pull request's branch merged-and-abandoned when another PR independently wrote the same docket record pr: lines, and its recovery would discard the branch
status: untriaged
added: 2026-09-06
---

**Problem.** `bin/docket stranded`'s second section — "carries work the default
branch does not hold, having already taken the rest of it" — fired on
`claude/triage-fwyuus` while that branch's pull request, #372, was **open and
unmerged**.

Observed 2026-09-06T01:2xZ, verbatim:

> 1 branch carries work the default branch does not hold, having already taken
> the rest of it:
>
> `claude/triage-fwyuus`  (8 files of its work already landed)

`origin/main` at the time was `40352b8` and still carried `PL-7PLY` at `status:
untriaged` — the branch's triage commit had landed nowhere. Nothing had merged.

**What actually matched.** The branch's first commit changed twelve files. Four
are its real work; the other eight are items whose *only* change in that commit
was a `pr:` line written by `bin/docket record`. `origin/main` already carried
those same eight `pr:` lines — because the sessions behind #366 and #369 ran
`docket record` too, and the command is deterministic, so both sides wrote
byte-identical lines. Eight of twelve files therefore agreed with `main`, and
the detector read that agreement as "its pull request merged and took this
much".

The interaction is specific and it is going to recur: `docket record` is
explicitly designed to be run by any session, to write a value dictated by the
tool rather than chosen, and to be let ride whatever commit is already being
made (`PL-QTSB`). Convergent identical writes are its *intended* behaviour. So
any branch that runs it will keep tripping this.

**Why it matters.** Two reasons, and the second is the sharp one.

The verdict is confidently wrong rather than uncertain, and nothing in the
output hedges it. It takes a cross-check the reader has no reason to run —
compare the branch's real work against `origin/main`, or read the pull request's
state — to see that it is wrong.

And the prescribed recovery is destructive. The `docket` skill's stranded
section answers this exact section with

```
git branch -dr origin/<branch>
git fetch origin main
git checkout -B <branch> origin/main
```

which, applied to a branch whose pull request is *open*, discards the branch the
pull request was opened against. A session that trusts the digest — and the
digest is the first thing every session reads — throws away live work while
believing it is recovering it. This session was told to do exactly that at
startup and did not, only because it had the pull request's state in context.

**Where.** `subprojects/docket/src/docket/` — whichever function backs
`stranded`'s second section; the session-start digest line that summarises it
("Left on a branch after its pull request merged"); and the `docket` skill's
stranded prose, which states the recovery.

**Approach, and where the decidable line falls.** The current test appears to be
file-level agreement with the default branch, which cannot distinguish "merged"
from "converged". Two decidable signals are available without an API call and
either would have prevented this:

- **Only count files whose branch-side change is not already present on the
  base.** The eight `pr:` files agreed *exactly*, so they are not work the
  branch is carrying; they are work `main` already has. Counting only genuine
  differences drops the ratio from 8/12 to 0/12 and the section does not fire.
- **Require the merge to be visible in history.** A branch whose pull request
  merged has an ancestor of its own on the default branch, or a squash subject
  naming its ids. Neither held here.

Whether a *third* signal — the pull request's actual state — belongs here is a
real question and probably no: `docket` runs from a bare checkout with no
network and must keep doing so (`PL-SK88`).

**Found.** This session, 2026-09-06, when the resume digest told it to restart
`claude/triage-fwyuus` on `main` while #372 was open with two commits on it.

**Done when.** `bin/docket stranded` does not report a branch as having had its
pull request merged on the strength of files whose content already agrees with
the base, and a regression test covers the shape: a branch carrying real work
plus several `pr:`-only edits that the base independently made.
