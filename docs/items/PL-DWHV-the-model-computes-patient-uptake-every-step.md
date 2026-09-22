---
id: PL-DWHV
title: The model computes patient uptake every step (UptakeStepResult.patient_agent_change_l) and displays it nowhere, though Gas Man makes Uptake and Delivered its headline pair - the difference between them is the low-flow lesson
priority: P3
effort: M
status: ready
classes: feature, ux
feature: liquid-agent-consumption
touches: ROADMAP.md
added: 2026-09-16
verify: grep -qF 'uptake beside delivered' ROADMAP.md && python3 tools/doc_check.py check
---

**Problem.** The model computes patient uptake every step (UptakeStepResult.patient_agent_change_l) and displays it nowhere, though Gas Man makes Uptake and Delivered its headline pair - the difference between them is the low-flow lesson

**What the model already has.** `AgentUptakeSystem._advance_step()` forms
`patient_agent_change_l` every step — the change in stored patient agent,
which by the tissue and venous balances is the integral of the pulmonary
uptake rate — and returns it on `UptakeStepResult`. It is exact rather than
accumulated, for the reason `core/governing_equations.py` gives. Nothing in
`app/` displays it.

**Why it is the missing half.** The Gas Man Workbook's Appendix (printed
pp. 180 and 196) shows that program's economic display as the pair *Uptake*
and *Delivered*, each available in litres or in dollars. Delivered is what was
bought; uptake is what the patient actually took; the gap between them is
waste, and it is the gap that fresh gas flow moves. Today's accounting panel
shows delivered, exhausted and stored instead — a decomposition of where the
agent *is*, which is a different and less teachable question than what it
cost.

**Not the same as `PL-H4N8`.** That item corrects which quantity means cost.
This one is that the second half of the comparison is computed and thrown
away. Both feed `ROADMAP.md` planned-milestone item 28.

**Why it matters.** The comparison a low-flow lesson rests on is delivered
against uptake - what was bought against what the patient took, the gap being
waste and the gap being what fresh gas flow moves. This model already computes
the second half exactly rather than by accumulation, and discards it. Building
the readout without it would leave the application drawing the decomposition it
has (delivered, exhausted, stored - where the agent is) instead of the comparison
the lesson needs, which is a different and less teachable question.

**Done when** `ROADMAP.md` planned-milestone item 28 names uptake beside
delivered as the pair the readout draws, and records that
`UptakeStepResult.patient_agent_change_l` already carries it; and the readout
built under that milestone displays both. Only the first half is actionable
now - the readout is item 28's work and out of the current milestone - and it is
what this item's `verify:` command pins.
