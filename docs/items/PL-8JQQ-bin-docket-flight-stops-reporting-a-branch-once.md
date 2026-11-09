---
id: PL-8JQQ
title: bin/docket flight stops reporting a branch once an earlier pull request from it squash-merged, so commits pushed to it afterwards are invisible: PL-3K9B's whole implementation, pushed with the id leading its subject, does not appear
priority: P2
effort: M
status: done
classes: defect
feature: stranded-report-fidelity
milestone: v0.5.0
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
closed: 2026-09-21
pr: 813
payoff: restores the one guard against two sessions on one item for the branch shape every harness-named branch here ends up in
verify: grep -q 'def test_a_branch_pushed_to_after_its_pull_request_squash_merged_is_still_in_flight' subprojects/docket/tests/test_vcs.py
---

**Problem.** bin/docket flight stops reporting a branch once an earlier pull request from it squash-merged, so commits pushed to it afterwards are invisible: PL-3K9B's whole implementation, pushed with the id leading its subject, does not appear

**Why it matters.** `bin/docket flight` is the one guard against two sessions
implementing the same item, and `.claude/skills/docket/modes/start.md` makes it
the first step of starting a named item — "the one step with no other guard".
When it goes quiet on live work it does not fail loudly; it reports a clean
list, and the reader concludes nobody is there. That is `CLAUDE.md`'s "gives a
wrong answer silently" test, on the command every other in-flight read is built
from.

**Measured 2026-09-20, and it cost exactly what it is meant to prevent.** This
session spent three replies recommending that `PL-3K9B` be started in a fresh
session while `session_01WxCqBLpTESQRwKS2Q4zSug` was implementing it on
`claude/lucid-dijkstra-i1qy6x` — the same branch this session was pushing to.
The project owner caught it; the tooling did not. The sequence:

- `#801` (this session's design round for `PL-3K9B`) squash-merged onto `main`.
- The other session pushed `6b2008c8` to the same branch: subject
  `PL-3K9B: a mark the run's clock is at or behind reads passed, not still
  running`, 8 files, 637 insertions across `src/`, `tests/` and `docs/`.
- `git fetch origin` then `bin/docket flight` reported two items in flight,
  neither of them `PL-3K9B`. The local branch was then fast-forwarded to
  `6b2008c8` and `flight` re-run: still silent.

Before `#801` merged, the same command *did* report `PL-3K9B` on that branch.
The only thing that changed between the two readings is that the branch's
earlier commits landed on `main`.

**Two leads already ruled out, so the next session need not walk them.**

- **Not a stale ref.** `git fetch origin` ran immediately before, and the
  answer did not change after fast-forwarding the local branch to the new
  commit. This is a different failure from the one `PL-QSGX` records about
  `flight` not fetching.
- **Not the landed-branch exclusion.** `_work_already_on_base` is
  `bool(landed) and not outstanding`, and the branch had an outstanding commit
  (`6b2008c8`), so that test returns `False` and cannot be what dropped it.

**What is left to look at.** The strong reading is documented as coming from
commit subjects on refs the default branch has not taken, and `_annotates_only`
withholds a commit whose whole diff is in the queue — which `6b2008c8` is not.
So either the ref was named as unread by one of the two history guards
`branches_in_flight` documents, or the squash left the ref in a state the split
reads differently than it reads a never-merged branch. Read it against a branch
that has been squash-merged and then pushed to again, which is the shape every
long-lived harness branch on this project takes.

**Done when.** A branch that continues after an earlier pull request from it
squash-merged is still reported by `bin/docket flight` for an item a later
commit on it names; and a test pins that shape, since it is the one every
harness-named branch here eventually takes.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground". No paragraph there named it apart from this entry line, so it rested on the section's opening ground, which is quoted in `PL-36R4`'s brief.

> - PL-8JQQ (M) bin/docket flight went silent on a live implementation while the branch carried already-squash-merged commits beside the new one, so the one guard against two sessions implementing the same item reported a clean list; `defect` and dated after this gate's freeze, so it enters on the refilling-queue ground rather than under the safety/science exception
