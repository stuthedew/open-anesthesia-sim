---
id: PL-DWHV
title: The model computes patient uptake every step (UptakeStepResult.patient_agent_change_l) and displays it nowhere, though Gas Man makes Uptake and Delivered its headline pair - the difference between them is the low-flow lesson
status: untriaged
feature: liquid-agent-consumption
added: 2026-09-16
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
