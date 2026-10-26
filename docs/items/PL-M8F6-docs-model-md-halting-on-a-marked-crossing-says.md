---
id: PL-M8F6
title: docs/MODEL.md § "Halting on a marked crossing" says the concentration displayed beside a halt is the height the learner marked, but the run halts on the first step at or past the height, so a circuit target of 0.10 ×MAC halts showing 0.11 ×MAC on 13 of 59 targets tried, and a learner reads a correct halt as a detection fault
priority: P1
effort: S
status: done
classes: docs, science
feature: replay-findings
touches: docs/MODEL.md, tests/integration/test_controller.py
added: 2026-10-25
closed: 2026-10-26
pr: 1855
payoff: a learner who sees 0.31 beside a 0.30 ×MAC halt is told by the specification that this is expected, not a detection fault
verify: ! grep -qF 'So the concentration displayed beside a halt is the height the learner' docs/MODEL.md && grep -qF 'within one simulation step' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Halting on a marked crossing" says "the concentration displayed beside a halt is the height the learner marked." The halt actually lands on the step that crossed the height. The reading there can be past the height by up to one 0.1 s step's change. The sentence should say the halt is within one simulation step of the mark, and say how large one step's change can be on a fast compartment.

**Why it matters.** `docs/MODEL.md` is the authority for what a displayed value means. A learner who sets a 0.30 ×MAC circuit target and sees 0.31 beside the halt is told by the specification that the two should match. They would conclude the detection is faulty, or distrust a correct value. The alveolar compartment moves slowly enough that it showed no difference in the same test.

**Done when.** `docs/MODEL.md` § "Halting on a marked crossing" says the halt lands within one simulation step of the marked height, and how large one step's change can be on a fast compartment. It no longer says the concentration displayed beside a halt is the height the learner marked.

**Found by.** `PL-TBQS` reviewer replay on #775, finding 775 r04 F3, and the third `PL-ZWXD` addendum entry, checked against main on 2026-10-25. Reproduced with `scratchpad/r/scripts/d_775_overshoot.py`: with 8% sevoflurane at 10 L/min, targets from 0.05 to 2.95 ×MAC in 0.05 steps, 13 of 59 circuit halts showed one display count high (0.05 as 0.06, 0.10 as 0.11, 0.45 as 0.46, 0.50 as 0.51), and 0 of 59 alveolar halts did.

## Done 2026-10-26

`docs/MODEL.md` § "Halting on a marked crossing" now says that the value
beside a halt is the reading on the first step at or past the marked height,
within one simulation step of it. It gives the size of that step on the
fastest compartment and says that a halt one count past the mark is correct.

The figures were measured again on this branch, not copied from the finding.
A script ran a sevoflurane case at 8% and 10 L/min against each circuit and
alveolar target from 0.05 to 2.95 ×MAC in steps of 0.05, stepping at 0.1 s
until the halt. It recorded the reading at the halt, the reading one step
before, and the text `format_mac_multiple` gives. On the circuit, 13 of 59
halts showed one count past the mark, the largest one-step change was
0.0109 ×MAC and the largest overshoot 0.0091 ×MAC. On the alveolar
compartment, 0 of 59 did, with a largest step of 0.0026 ×MAC. The new test
`test_a_circuit_target_halts_within_one_step_of_its_mark_and_can_show_one_count_past`
pins the specification's example: a 0.10 ×MAC circuit target halts showing
0.11 ×MAC, past the mark by less than the step that crossed it.
