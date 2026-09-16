---
id: PL-ZF2G
title: The anticipated debt-gate carve-out never expires, so an anticipated safety item stays invisible to the gate after its hazard goes live
status: untriaged
feature: debt-gate
added: 2026-09-16
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
