---
id: PL-5TRV
title: bin/docket stranded calls an open pull request's branch merged-and-abandoned when another PR independently wrote the same docket record pr: lines, and its recovery would discard the branch
priority: P2
effort: M
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-06
closed: 2026-09-06
pr: 385
verify: uv run pytest subprojects/docket/tests/test_vcs.py && grep -q 'def test_a_branch_whose_changes_the_base_already_holds_is_not_partly_merged' subprojects/docket/tests/test_vcs.py
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

**Sequence it with `PL-39B7`** (make `stranded` distinguish a merged-and-deleted
branch from an abandoned one). Noted at triage, 2026-09-06: that item is the
same command's *first* section and declares the same three files, so the two are
one branch rather than two. Neither subsumes the other — `PL-39B7` is about a
stale comparison point and a deleted ref read as corroboration, this is about
the second section counting agreement as merge — but whichever runs second will
resolve against the first.

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

**#372 did merge later, and that does not soften this.** The merge landed at
02:06:27Z as `6e6032c`, after the observation above. The observation is pinned
by facts a reader can still check rather than by a clock: at the time
`stranded` fired, `origin/main` was `40352b8`, and `git show
40352b8:docs/items/PL-7PLY-*.md` shows `status: untriaged` — the branch's work
was nowhere on the base and no pull request of its had merged. So the detector
was wrong when it spoke, and only accidentally right an hour later. Had a
session obeyed it then, `git branch -dr` plus a restart on `main` would have
deleted the branch #372 was open against and thrown the whole triage pass away.

The merge did produce the *genuine* article immediately afterwards, which is
worth recording as the contrast: two commits pushed to the branch at 02:07:09Z,
after the squash-merge had already taken `84cdeef` and deleted the head branch.
That is the case this section is for, and the same output cannot distinguish it
from the false one.

**Done when.** `bin/docket stranded` does not report a branch as having had its
pull request merged on the strength of files whose content already agrees with
the base, and a regression test covers the shape: a branch carrying real work
plus several `pr:`-only edits that the base independently made.

**Closed 2026-09-06 on `PL-39B7`'s branch, as its triage note anticipated.**
The two are one function and one walk, and splitting them would have meant the
second resolving against the first for nothing.

Of the two decidable signals proposed above, **neither survived as written and
the second's idea did.** Counting only files whose branch-side change is absent
from the base is what `_landing_split` already does: the eight `pr:` blobs
*are* on the base, byte for byte, so no content comparison can subtract them —
convergence and a merge are indistinguishable at the blob, because there is
nothing to distinguish. And requiring an ancestor on the default branch is the
ancestry test a squash merge defeats, which would have silenced the check in
every true case (`PL-39B7`'s close-out spells that out).

What separates them is the **unit** rather than the content: a squash merge
takes whole commits, so a branch whose pull request merged has a commit every
path of which the base holds, while convergence scatters agreement inside
commits and leaves no whole one. `_commits_by_landing` now reads both halves of
that off the one walk `_commits_touching` already made — the commits nothing
took, and whether the base took any commit whole — and `orphaned` requires
both. The observed shape is pinned by
`test_a_branch_whose_changes_the_base_already_holds_is_not_partly_merged`.

Its cost is one narrow recall loss, documented in the docstring and in
`subprojects/docket/README.md`: a post-merge push to a branch whose every
pre-merge commit was re-merged against a base that had moved under it has no
whole commit on either side and goes unreported. The remaining false positive
is a branch one of whose commits is *only* `docket record` output, which the
skill already tells a session not to make.

The third signal — the pull request's own state — stayed out, for the reason
guessed above (`PL-SK88`). The skill prose instead tells the reader to confirm
the merge before running a recovery that deletes a branch, since narrowing the
verdict is not the same as removing the reader's part.
