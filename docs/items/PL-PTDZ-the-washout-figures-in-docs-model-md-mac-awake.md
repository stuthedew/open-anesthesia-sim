---
id: PL-PTDZ
title: The washout figures in docs/MODEL.md § "MAC-awake as a chart reference" (2.86, 6.55 and 7.31 min crossings, 1.69% alveolar, 0.84 MAC after 3 hours) depend on the blood:gas and tissue coefficients, volumes, ventilation, cardiac output and the protocol, but no test pins them, so a parameter change leaves six figures in the specification stale with no check firing
priority: P1
effort: S
status: done
classes: defect, science
feature: mac-awake-reference-text
touches: docs/MODEL.md, tests/reference/test_mac_awake_washout_figures.py
added: 2026-10-26
closed: 2026-10-31
pr: 1900
payoff: a change to a coefficient or a default flow that moves the MAC-awake washout figures fails a test, instead of leaving docs/MODEL.md teaching a wake-up time the model no longer produces
verify: uv run pytest -q tests/reference/test_mac_awake_washout_figures.py
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

**Built 2026-10-31.** `tests/reference/test_mac_awake_washout_figures.py`
runs the section's protocol once, through `AgentUptakeSystem.for_agent` at
0.1 s steps, and checks nine printed numbers. They are the six figures this
item names, the band centre of 0.68%, the restated 6.55 min, and 0.612% at
Mapleson's MAC. The test reads each expected figure from `docs/MODEL.md`
itself, by matching its sentence, and compares the model's value to the
decimal places printed. So a model change that moves a figure fails the test,
and so does an edit to the document that changes a figure without the model.
A literal copy in the test would have caught only the first. A reworded
sentence fails with a message that says to update the pattern. The band
centre comes from the agent's data file, as the chart draws it. Mapleson's
1.80% is read from the section, where it is restated beside its citation. The
run takes about 5 s.

**One figure was wrong, and is corrected.** Before the fix the test failed on
one figure: "prints the vessel-rich crossing of the band at Mapleson's MAC as
7.31, and the model now gives 7.303996285072531" (`uv run pytest -q
tests/reference/test_mac_awake_washout_figures.py`, 2026-10-31). The crossing,
interpolated between the two steps around it, is at 7.304 min, which prints
as 7.30. The 2026-10-26 measurement evidently took the first step below the
threshold, at 438.3 s, or 7.305 min, which rounds up. The section now says
7.30 and states that a crossing time is interpolated. The other five figures
agree under either reading. The 0.006 min difference changes no conclusion in
the section.
