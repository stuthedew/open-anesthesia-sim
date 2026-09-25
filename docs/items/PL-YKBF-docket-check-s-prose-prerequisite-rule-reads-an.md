---
id: PL-YKBF
title: docket check's prose-prerequisite rule reads an item id after a negated 'not blocked by' as a prerequisite and refuses the brief with an error - this item's own first draft was refused by it
priority: P3
effort: S
status: ready
classes: defect
feature: exact-gates
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-25 triage pass
added: 2026-09-25
payoff: a brief saying it is not held up by an item stops drawing advice to block it on that item
verify: grep -q 'def test_a_negated_blocked_by_is_not_read_as_a_prerequisite' subprojects/docket/tests/test_checks.py
---

**Problem.** docket check's prose-prerequisite rule reads an item id after a negated 'not blocked by' as a prerequisite and refuses the brief with an error - this item's own first draft was refused by it

Reproduced by the fuzz harness, and again by filing this item: its first draft quoted the sentence "This is not blocked by" followed by a real id, and `bin/docket check` refused the store with an error ("names ... as a prerequisite in prose and does not list it in `blocked-by`"), so the example had to be reworded to satisfy the check it reports - PL-KJ63's pattern. The rule reads any cue word within 40 characters of an id.

Re-confirmed 2026-09-25 against 46954a81, at a lower severity than the title states: in a scratch store, a `ready` brief reading "This is not blocked by" and then an open item's id draws the grooming advisory `names ... as a prerequisite in prose and does not list it in blocked-by`, with 0 errors and exit 0. `_check_prose_dependencies` writes to `report.advisories`, and has since `PL-8YXJ` (#935), before this item was filed; `test_an_undeclared_prerequisite_never_fails_the_build` pins that, and `docket set` only prints the passage. So nothing is refused. What is wrong is the advice: on a negated sentence it tells the session to declare the edge and set `status: blocked`, which would hide the item from `docket next` behind work its brief says it is free of.

**Generator check.** The fact misread is whether a sentence claims a prerequisite, recognised by cue words - `PL-GPJ7`'s `misread:` at family altitude, but read by an advisory, which is where the head's remedy already puts wording-based recognition. The head's fix leaves this rule exactly as it is, so the head does not explain this item: it is a one-off precision defect in an advisory, and a candidate to leave `PL-GPJ7`'s `root-cause-of:`.

**Why it matters.** An advisory that fires on the opposite claim trains sessions to skim advisories.

**Done when.** A negation cue before the id suppresses it; a test holds the reproduction.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
