---
id: PL-JHHC
title: A decision whose answer adds a commit to a pull request held for the owner's read is orphaned when the owner answers and merges in one sitting: PL-0GJC's answer was written while #1328 merged without it on 2026-10-04, and needed a follow-up pull request; nothing marks such a pull request as waiting on a commit, so the merge button reads as ready
priority: P3
effort: S
status: blocked
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, .claude/rules/instruction-writing.md
blocked-by: PL-R417
added: 2026-10-04
payoff: a pull request that a pending answer will add a commit to stops reading as ready to merge, so the answer lands with its work instead of in a follow-up pull request
---

**Problem.** A decision whose answer adds a commit to a pull request held for the owner's read is orphaned when the owner answers and merges in one sitting: PL-0GJC's answer was written while #1328 merged without it on 2026-10-04, and needed a follow-up pull request; nothing marks such a pull request as waiting on a commit, so the merge button reads as ready

**Reproduced 2026-10-04** on `main` at `8f24fe78`: `git log
--format='%h %ci %s' origin/main | grep -E '\(#1328\)|\(#1335\)'` shows
`1eb957d6`, PL-0GJC's build (#1328), merged at 01:17 UTC and `4899bfc0`, its
close carrying the compartment answer (#1335), at 02:02 UTC. The item's `pr:`
names 1335: the answer reached `main` only through the follow-up.

**Why it matters.** A pull request held for the owner's read shows a merge
button that reads as ready, and the hold says only that a read is owed. When a
decision put to the owner in the same sitting will add a commit to that branch,
answering and merging in one sitting lands the merge first and leaves the
answer's commit on a merged branch. Nothing was lost here, because the session
saw the merge and opened #1335, but it cost a second pull request, a second CI
run and a second read; and an answer committed to a merged branch unnoticed
never reaches `main`, which is why `CLAUDE.md` forbids committing to one. Rule
14's ordering, from `PL-794W`, puts the decision line first in the closing
block. It cannot reach a merge made from the pull request page.

**Shape, not decided here.** Two mechanisms would mark the pull request as
waiting. The session asking such a decision converts its pull request to a
draft until the answer is recorded: a sentence of rule, reusing the draft state
`bin/docket arm` already gives a claimed item. Or `bin/docket arm` answers
`hold` while an item the branch carries sits at `needs-decision`: code in
`arming.py`, itself on the owner's read list, which fires without anybody
remembering it. Either is new machinery.

**Held by the generator pause** (triage, 2026-10-04). Both shapes are new
workflow mechanisms, which `CLAUDE.md` § "What this project is" holds while any
open item carries `generator: live`. On `main` at `8f24fe78`, `bin/docket
generators` marks `PL-R417` still generating, its last slice open in #1353.
Before promoting, check that `bin/docket generators` marks no head "still
generating"; building it sooner is the owner's call, made by asking
(`PL-6Q9L`).

**Done when.** A pull request that a pending decision will add a commit to
cannot read as ready to merge until the answer is recorded, by whichever shape
is chosen once the pause lifts, and the choice is recorded here.

**Generator check.** Not a generator yet, with one predecessor. The fact
misread is whether an open pull request still owes a commit, a pending
decision's answer, before it is complete. `PL-794W` (closed 2026-09-01,
outside the 30-day re-entry window) met that fact at the closing block and
fixed it by ordering; this is the same fact at the merge button, which no
ordering in prose reaches. No head's `misread:` states it, and one more
instance makes three. Not `PL-WNCT`'s fact, whether pushed work has a pull
request to carry it: the answering session saw the merge and opened #1335.
