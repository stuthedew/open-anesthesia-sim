---
id: PL-JHHC
title: A decision whose answer adds a commit to a pull request held for the owner's read is orphaned when the owner answers and merges in one sitting: PL-0GJC's answer was written while #1328 merged without it on 2026-10-04, and needed a follow-up pull request; nothing marks such a pull request as waiting on a commit, so the merge button reads as ready
priority: P3
effort: S
status: ready
classes: infra
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, .claude/rules/instruction-writing.md
blocked-by: PL-R417
added: 2026-10-04
payoff: a pull request that a pending answer will add a commit to stops reading as ready to merge, so the answer lands with its work instead of in a follow-up pull request
verify: grep -qE '^\*\*Shape chosen, [0-9]{4}-' docs/items/PL-JHHC-*.md
not-delegable: the shape - a draft-conversion rule or an arm hold on needs-decision - is the building session's judgment, and no admitted command reads either mechanism, so the command reads only the recorded choice
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
is chosen once the pause lifts, and the choice is recorded here, in a paragraph
opening `**Shape chosen,` and its date.

**Generator check.** Not a generator yet, with one predecessor. The fact
misread is whether an open pull request still owes a commit, a pending
decision's answer, before it is complete. `PL-794W` (closed 2026-09-01,
outside the 30-day re-entry window) met that fact at the closing block and
fixed it by ordering; this is the same fact at the merge button, which no
ordering in prose reaches. No head's `misread:` states it, and one more
instance makes three. Not `PL-WNCT`'s fact, whether pushed work has a pull
request to carry it: the answering session saw the merge and opened #1335.

[superseded 2026-10-12: moved to `ready` by `PL-2349`, below] **The pause ends with `PL-R417`, closed 2026-10-11 in `#1392`.** `PL-R417` was the last head `bin/docket generators` marked still generating, and with it closed the command marks none, so the pause this waited on ends when `#1392` merges. Nothing else holds it. It stays `blocked` only because `ready` needs a `verify:` command, which `bin/docket set` refuses `ready` without, and that command waits on which of the two shapes is built, the building session's choice, recorded here as Done-when asks. `bin/docket check` names it ready to promote meanwhile.

**Promoted 2026-10-12** by `PL-2349`, whose check now refuses a `blocked` item whose every blocker has closed. `bin/docket generators` on `main` at `3ff9f0f6` marks no head "still generating" and no open item carries `generator: live`, so the pause is over and nothing else this brief names holds it. The fault stands: `grep -c 'needs-decision' subprojects/docket/src/docket/arming.py` prints 0, and no rule converts such a pull request to a draft. The shape stays the building session's choice, so `verify:` reads the recorded choice rather than either mechanism - it passes once a paragraph opening `**Shape chosen,` and a date records which was built and why - and `not-delegable:` keeps it from a worker that `docket verify` would trust on that paragraph alone. Seen failing (exit 1) on 2026-10-12.
