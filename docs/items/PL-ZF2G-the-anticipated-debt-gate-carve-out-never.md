---
id: PL-ZF2G
title: The anticipated debt-gate carve-out never expires, so an anticipated safety item stays invisible to the gate after its hazard goes live
priority: P2
effort: S
status: done
classes: docs, defect
feature: debt-gate
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-16
closed: 2026-09-16
pr: 644
verify: uv run pytest tests/unit/test_doc_check.py && grep -qF 'The carve-out expires with the wait it is granted for' ROADMAP.md && grep -q 'def test_an_anticipated_safety_item_is_reported_once_it_is_no_longer_blocked' tests/unit/test_doc_check.py
---

**Problem.** The anticipated debt-gate carve-out never expires, so an anticipated safety item stays invisible to the gate after its hazard goes live

**Problem, stated against what just shipped.** `PL-83LS` made an `anticipated`
`safety` or `science` finding not debt until the hazard it describes exists
(project owner, 2026-09-16, ratified), and `tools/doc_check.py`'s
`check_gate_reentries` now excludes an `anticipated`-classed item from the
advisory. The exclusion turns on the class alone, so it does not stop when the
hazard starts: once planned-milestone item 34's area system ships, the ten
findings it was written for describe live hazards and are still invisible to
the check.

**Why it may not matter, which is why this is a question rather than a defect.**
All ten are named in v0.6.0's `Required scope` or v0.7.0's, so `scope_ids`
places them and the advisory would be quiet regardless once that gate is the
current one. The hole is for an `anticipated` item that is *not* placed - one
filed after the milestone that creates its hazard has been scoped, or one whose
milestone section never names it.

**The narrowing that was considered and not built.** `subprojects/docket/src/docket/checks.py`
already requires `status == "blocked"` alongside `anticipated` to grant the
safety-band exemption, for the same reason: "A blocked item where something is
already wrong is the opposite case". The same conjunct here would make the
carve-out expire exactly when the blocker closes, which is when the hazard goes
live. It was not built because it is not what the ratified decision or
`PL-83LS`'s brief describes, and because it changes nothing on today's tree -
all ten are `blocked`.

**Why it is the project owner's.** It amends a rule they ratified two hours
earlier. `CLAUDE.md` makes a ratified decision reopenable on ordinary evidence,
and this is ordinary evidence: a cost the case did not carry.

**Found 2026-09-16** while implementing `PL-83LS`.

**Where.** `tools/doc_check.py` `check_gate_reentries`; `ROADMAP.md` § "The gate
is a snapshot, not a moving target"; `tests/unit/test_doc_check.py`.

**Recommendation.** Add the `status == "blocked"` conjunct, matching
`checks.py`. It is decidable, it costs nothing today, and it turns a rule that
has to be remembered into one that expires by itself.

**Resolution** (project owner, 2026-09-16, ratified - chosen over leaving the
exclusion on the class alone, which never expires). The `status == "blocked"`
conjunct is in, matching `subprojects/docket/src/docket/checks.py`:
`check_gate_reentries` now exempts an item only where `anticipated` and
`blocked` hold together, so the exemption is held by an item that has written
down what it is waiting for and lapses when that wait ends.

**Counted before tightening, per `.claude/rules/expert-review.md`.** The
question was how many open items the conjunct newly exposes, and the answer is
**none**: 17 open items carry `anticipated` and all 17 are `blocked`. So it
cannot light the advisory on anything with no reachable clean state, which is
the failure `PL-83LS` was filed to remove.

**It is not hypothetical, though, which is the fact the brief did not have.**
`PL-W7H9` (`safety, anticipated`) is blocked on `PL-8PSW`, which is `done`, and
`bin/docket check` has been saying so - "every blocker has closed; it is ready
to promote", for seven items on 2026-09-16. Promoting it is now what returns it
to the gate. The hole was one grooming pass from being live rather than a
milestone away.

**What that same measurement costs, recorded rather than claimed away.** The
carve-out expires on the *promotion*, not on the blocker closing: nothing
rewrites `status` by itself, so the advisory above is the mechanism, and the
window is one grooming pass instead of the indefinite one it replaces. The
recommendation's "expires by itself" was half right, and the docstring and
`ROADMAP.md` now say the accurate version.

**Resolving the blockers inside `check_gate_reentries` was considered and
refused.** It would close the window outright, at the price of a second copy of
`checks.py`'s resolution logic - item edges, milestone edges, `ships_with` - in
the tool whose job is to read the store rather than reason about it, and of two
readings of `anticipated` in one repository. The project has also already decided this exact case by hand
and written it down: `PL-V6M0` is `safety, anticipated` and was never blocked,
and `ROADMAP.md` § "Why `anticipated` does not defer it" seats it at `P1`
because "`checks.py` grants the class its exemption from the band only at
`status: blocked`, and nothing blocks this one ... an unavailable exemption is
not a reason to seat safety-critical work lower". The same paragraph has it
re-entering the gate "whatever its presence answer". So the conjunct is not a
new rule imported from the checker - it is the gate check catching up with a
disposition this roadmap already took, which on the class alone it would have
contradicted.

**Tests pin both halves of the conjunct.**
`test_an_anticipated_safety_item_is_reported_once_it_is_no_longer_blocked` is
what fails without the change - 0 advisories where 1 is expected, confirmed by
reverting the line - and
`test_a_blocked_safety_item_without_the_class_is_still_reported` holds the other
side, so a future narrowing cannot move the exemption onto the status alone.
