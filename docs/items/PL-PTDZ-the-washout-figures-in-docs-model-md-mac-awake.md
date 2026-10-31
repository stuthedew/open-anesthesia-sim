---
id: PL-PTDZ
title: The washout figures in docs/MODEL.md § "MAC-awake as a chart reference" (2.86, 6.55 and 7.31 min crossings, 1.69% alveolar, 0.84 MAC after 3 hours) depend on the blood:gas and tissue coefficients, volumes, ventilation, cardiac output and the protocol, but no test pins them, so a parameter change leaves six figures in the specification stale with no check firing
priority: P1
effort: S
status: ready
classes: defect, science
feature: mac-awake-reference-text
touches: docs/MODEL.md, tests/reference
added: 2026-10-26
payoff: a change to a coefficient or a default flow that moves the MAC-awake washout figures fails a test, instead of leaving docs/MODEL.md teaching a wake-up time the model no longer produces
verify: grep -rq 'def test_the_mac_awake_washout_figures' tests/reference
reenters: PL-4FBP
---

**Problem.** The washout figures in docs/MODEL.md § "MAC-awake as a chart reference" (2.86, 6.55 and 7.31 min crossings, 1.69% alveolar, 0.84 MAC after 3 hours) depend on the blood:gas and tissue coefficients, volumes, ventilation, cardiac output and the protocol, but no test pins them, so a parameter change leaves six figures in the specification stale with no check firing

**Reproduced 2026-10-31.** `grep -rn '2\.86\|6\.55\|7\.31' tests/` finds the
figures in no test. The one hit, `2.865236619137837` in
`tests/unit/test_exponential_approach.py`, is an unrelated searched state.

**Why it matters.** These figures teach how much later responsiveness returns
than the alveolar trace suggests, and how far a band drawn too high moves the
crossing. A learner reads them as what the model does. A change to a partition
coefficient, a volume or a default flow would change all six and leave the
specification stating a wash-out the model no longer produces, with no check
firing.

**Done when.** A test under `tests/reference/` runs the protocol the section
describes (sevoflurane, 3 hours at 2.0% and 4 L/min, then the dial off and
10 L/min) and holds each of the six figures to the precision the section
prints. A parameter change that moves one then fails the test.

**Generator check.** `PL-4FBP`'s fact: the link between a document sentence and
the tree fact it restates, here where the fact is the model's computed output
rather than a file. `PL-4FBP` closed on 2026-09-19, so this is an instance filed
after its head closed, recorded as `reenters: PL-4FBP`. `PL-R4Y2`'s pass of
2026-10-26 found four more of this shape (`PL-39KH`, `PL-MLPT`, `PL-M8F6`,
`PL-5RPD`) and left them unrecorded (`PL-R4Y2`'s triage, 2026-10-31).
