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

[superseded 2026-11-22: the owner's answer below replaced this done-when] **Done when** `ROADMAP.md` planned-milestone item 28 names uptake beside
delivered as the pair the readout draws, and records that
`UptakeStepResult.patient_agent_change_l` already carries it; and the readout
built under that milestone displays both. Only the first half is actionable
now - the readout is item 28's work and out of the current milestone - and it is
what this item's `verify:` command pins.

**Checked 2026-11-22** against `d4e8200`: needs the project owner. The model still computes `patient_agent_change_l` in `src/anesthesia_sim/core/uptake_system.py`, and nothing in `src/anesthesia_sim/app/` shows it. But the done-when now contradicts the scoped milestone. `ROADMAP.md` § "Explicitly out of scope for v0.7.0", written when v0.7.0 was scoped in #1761, lists "Uptake as a headline figure" and says showing it is a display of its own, not part of the cost. The agent cost View that item 28 built (`src/anesthesia_sim/app/agent_cost.py`) shows delivered agent only. So the change this item asks for in item 28's text, and the readout under item 28 showing both, now turn on whether the owner wants uptake beside delivered as its own display.

**Answered 2026-11-22.** Uptake is shown beside delivered as a display of its own, after v0.7.0, and the agent cost View keeps showing what was delivered (project owner, 2026-11-22, ratified, "whatever is best practice", over adding uptake to item 28's cost readout). Two reasons favour a display of its own. The cost View answers what the agent cost, and uptake is not a cost. The low-flow lesson is the gap between the two amounts over time, which needs both drawn on one scale rather than a second number beside a price. This agrees with `ROADMAP.md` § "Explicitly out of scope for v0.7.0", which already says "Showing it is a display of its own, not part of the cost."

**Done when.** `ROADMAP.md`'s planned milestones carry one line for a display that shows uptake beside delivered as its own display rather than part of the agent cost. That line records that `UptakeStepResult.patient_agent_change_l` already carries uptake. Item 28's text is left as it is.
