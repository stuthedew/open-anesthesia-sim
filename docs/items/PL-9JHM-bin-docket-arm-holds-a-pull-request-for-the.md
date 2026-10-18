---
id: PL-9JHM
title: bin/docket arm holds a pull request for the owner's read with no ask in it, so sessions still send a bare 'read #N' and holds with nothing to review reach the owner
priority: P2
effort: M
status: ready
classes: defect
feature: review-hold
touches: subprojects/docket/src/docket/arming.py, subprojects/docket/tests/test_cli.py, docs/maintainer.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; the owner asked for it on 2026-10-18
added: 2026-10-18
payoff: a pull request reaches the owner only with a recorded question or risk to review, printed as the ask's opening line, and anything else merges on green
verify: grep -q 'OWNER_ASK = "Owner-ask"' subprojects/docket/src/docket/arming.py && grep -q 'def test_arm_holds_for_the_owner_only_with_a_recorded_ask' subprojects/docket/tests/test_cli.py
reenters: PL-9KHK, PL-DKBG
---

**Problem.** When `bin/docket arm` holds a pull request for the owner's
read, it prints prose telling the session what to ask (`READ_ASK` in
`subprojects/docket/src/docket/arming.py`). Nothing checks that the session
does it. On 2026-10-18 the view chooser thread sent Stuart a bare "read the
pull request" with no question in it. That has now happened at least three
times despite two prose fixes: `PL-9KHK` (three sessions closed on a bare
"read #N") and `PL-DKBG` (`#1516`'s ask invented two points to judge).

**Why it matters.** Each ask with nothing in it spends the owner's attention
and trains a click-through, which would let the one change that does need him
merge as unread as the rest. Two prose fixes have not stopped it, so the shape
of the ask has to be something `arm` checks.

**The owner's rule** (project owner, 2026-10-18, on the project timeline):
"View chooser thread just told me a generic read pull request without a
question again", "I feel like we keep doing this every time and it doesn't
help", "Will that force it to make up questions that shouldn't be asked?", and
"Right, but it's not supposed to ask for a merge if nothing to review". So a
pull request with nothing to review must not reach him at all, not even as a
plain "Merge it", and a question must never be invented to justify a hold.

**The fix.** A hold for the owner's read must carry the ask as a recorded
fact, an `Owner-ask:` commit trailer that `arm` parses and prints as the ask's
opening line. It takes one of two forms:

- a decision: the question, at least two options that each say what they
  change for the owner or a learner, and a recommendation naming one of them;
- a risk review, for a high-risk change with no choice in it (`PL-DKBG`'s
  second case): what could go wrong and for whom, what was checked to rule it
  out, and the one thing the owner should look at.

Without a valid record on a commit made since the branch's newest change
outside the store, `arm` prints no ask and tells the session what to do. If it
cannot fill either form honestly, nothing needs the owner, and the session
records `Owner-read: not needed - <why>` so the change merges on green. The
printed form and `docs/maintainer.md` say that a question with an obvious answer
is wrong, citing `#1516`.

**Open for the owner: the gate's own hold.** Any change to `arming.py`, and
any edit to a test pinning its answers, holds for the owner whatever it
changes (`PL-VKHD`, the owner's answer of 2026-10-12, ratified, over arming a
change to it on green; `PL-WW0Q` for the pinned tests). That conflicts with
the rule above for a refactor of the gate. It was put to the owner on a card
on 2026-10-18. The options were: tests guard it (a gate change holds only when
it edits or deletes an existing pinned test), keep holding (with a risk-review
ask), or merge on green. **Recommendation: tests guard it.** To loosen an
existing answer, a change has to edit the test that pins it, so that kind of
loosening still reaches the owner.

**Done when.** `arm` holds for the owner's read only with a valid `Owner-ask:`
record and prints it as the ask's opening line; without one it says that
nothing reaches the owner until the session records an ask or judges the
change `not needed`. `arming.py`'s docstring and `docs/maintainer.md` § "What comes to
you before it merges" state the rule, and `CLAUDE.md` stays as it is, because
`arm` prints the rule at the moment a session needs it, and the owner's answer on the gate's own hold is
built and recorded here.

**Generator check.** Not recorded as a generator. Leaving the ask's shape to
prose explains `PL-9KHK`, `PL-DKBG` and the 2026-10-18 bare ask, but only two
of the three are items. This item fixes that mechanism directly.
