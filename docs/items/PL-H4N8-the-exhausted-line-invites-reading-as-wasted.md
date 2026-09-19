---
id: PL-H4N8
title: ROADMAP planned-milestone item 28 specifies agent cost 'from the exhausted-agent amount', but cost is what left the bottle, which is the delivered amount - exhausted understates it mid-run by exactly what is still stored
priority: P1
effort: S
status: done
classes: science, docs
feature: liquid-agent-consumption
touches: ROADMAP.md
added: 2026-09-16
closed: 2026-09-19
verify: grep -qF 'from the delivered-agent amount' ROADMAP.md
---

**Problem.** The exhausted line invites reading as 'wasted', but this model has no metabolism so nearly all stored agent becomes exhausted by end of case - the figure that means cost is delivered

**The arithmetic that makes the reading wrong.** The accounting identity is
`initial + delivered = exhausted + currently stored`, so with `initial` zero,
delivered is the total and exhausted and stored are its two fates at that
instant. Reading exhausted as "wasted" and stored as "used" makes them look
like a fixed split of the bill. They are not: `docs/MODEL.md` § "Assumptions"
records "there is no metabolism" and "there is no chemical degradation", so
every millilitre currently stored in the patient and the circuit leaves
through the exhaust during emergence. Run the case to completion and exhausted
converges on delivered.

**What that means for a consumption display.** The figure that means money and
bottle is **delivered** — it is the vapour the vaporizer added, so it is
exactly what left the 250 mL bottle. The exhausted/stored split is a statement
about *where the agent is right now*, which is a genuine and teachable thing
(it is the uptake curve in mass form) but is not the economics. The low-flow
lesson is a comparison between two runs' *delivered* totals at the same
alveolar concentration, not a split within one run.

**So the labels have to carry which question they answer.** A panel that puts
a "wasted" label on the exhausted line teaches something false about where the
cost goes. Decided together with `PL-B396`, which chooses the display.

**This is now a correction to a planned feature, not only to a label**
(found 2026-09-16, when the project owner ruled the accounting panel
developer-facing). `ROADMAP.md` § "Planned milestones" item 28 reads, in
full:

> 28. Add agent cost, from the exhausted-agent amount the model already
>     tracks. The economic argument for low fresh gas flow is a standard
>     teaching point and currently the one lesson in this class of simulator
>     that the application has the numbers for and does not draw.

The intent is right and the basis is wrong. Cost is what left the bottle,
which is `delivered_agent_l` — the vapour the vaporizer added,
$\dot V_F F_D \Delta t$. `exhausted_agent_l` is what has left the *circuit*
so far, and by the accounting identity it understates delivered by exactly
`currently_stored_agent_l`.

**Why it reads plausibly, and where it breaks.** `docs/MODEL.md`
§ "Assumptions" records no metabolism and no chemical degradation, so
everything stored leaves through the exhaust eventually and the two converge
at the end of a run taken to full washout. They are not equal at any earlier
instant, and the gap is largest exactly during wash-in — the phase the
low-flow lesson is about. A cost readout built on exhausted would therefore
read low for most of a case and lowest when the teaching point is sharpest.

**What done requires.** Item 28's sentence is corrected to name delivered;
the difference between the two is measured at 15, 30 and 60 minutes for a
reference-adult sevoflurane case so the item records what the wrong basis
would have cost; and any cost or consumption surface reads delivered.

**The reference implementation agrees, read 2026-09-16.** The Gas Man
Workbook's Appendix states the program's own cost formula at printed p. 174:
`Cost = DELIVERED Flow x Cost/mL vapor`, where `DELIVERED Flow = DEL x Feff`
and `Feff = FGF (1+Del)`. Gas Man bills delivered, not exhausted. Item 28's
sentence therefore disagrees with both the accounting identity and the
simulator this project takes as its lineage.

**Why it matters.** `ROADMAP.md` planned-milestone item 28 is the specification a
later session will build the cost readout from, and it names the wrong quantity.
A cost built on `exhausted_agent_l` reads low for most of a case and lowest
during wash-in - the phase the low-flow lesson is about - because by the
accounting identity it understates delivered by exactly what is still stored.
That is a plausible-looking number that is wrong in a teaching display, which is
the failure `CLAUDE.md`'s safety-critical standard puts above tidiness. It is
also cheap to fix now and expensive later: once the readout exists, the wrong
basis is in code, in a test and on a screen.

**Done when** item 28's sentence names the delivered-agent amount rather than the
exhausted one; the gap between the two is measured at 15, 30 and 60 minutes for a
reference-adult sevoflurane case and recorded here, so the item carries what the
wrong basis would have cost; and the exhausted/stored split, if it is displayed
at all, is labelled as where the agent is now rather than as what it cost.

## The measurement, 2026-09-19

**Method.** `AgentUptakeSystem.default()` - the reference adult from
`data/patients/reference_adult.json` and the reference circle system from
`data/machines/reference_circle_system.json`, running sevoflurane at its own
1 MAC (2.0%) with the dial held there for the whole run - advanced in 0.1 s
steps, the model's `MAXIMUM_SIMULATION_STEP_S`. `agent_simulation_validation`
was read at each sample and asserted to pass, so every figure below sits on a
closed accounting identity rather than on a drifting one. `initial_agent_l` is
0.0 throughout, which is what lets delivered be read as the whole bill.
Three fresh gas flows, because the low-flow lesson is a comparison *between*
runs and a single run cannot show what the wrong basis does to it.

**Delivered, exhausted and stored, in millilitres of vapour.**

| FGF | | 15 min | 30 min | 60 min |
| --- | --- | --- | --- | --- |
| 1.0 L/min | delivered | 300.00 | 600.00 | 1200.00 |
| | exhausted | 108.98 | 277.03 | 651.56 |
| | stored | 191.02 | 322.97 | 548.44 |
| | **exhausted reads low by** | **63.7%** | **53.8%** | **45.7%** |
| 4.0 L/min | delivered | 1200.00 | 2400.00 | 4800.00 |
| (default) | exhausted | 856.40 | 1885.39 | 3990.61 |
| | stored | 343.60 | 514.61 | 809.39 |
| | **exhausted reads low by** | **28.6%** | **21.4%** | **16.9%** |
| 8.0 L/min | delivered | 2400.00 | 4800.00 | 9600.00 |
| | exhausted | 2010.63 | 4233.55 | 8723.78 |
| | stored | 389.37 | 566.45 | 876.22 |
| | **exhausted reads low by** | **16.2%** | **11.8%** | **9.1%** |

Delivered is exactly $\dot V_F F_D t$ at every sample - 4.0 L/min x 0.02 x
15 min = 1200 mL - which is the arithmetic check that the quantity being
called the bill is the one the vaporizer added, and is why the delivered
column is round.

**The finding the single-run gap understates.** Two things make this worse
than a uniform under-read:

1. **It is largest early.** 28.6% low at 15 minutes at the default flow
   against 16.9% at an hour. Wash-in is the phase the low-flow lesson is
   about, so the error peaks where the teaching point is sharpest.
2. **It is largest at low flow**, which distorts the comparison rather than
   shifting both arms of it. At a fixed dial, delivered is proportional to
   flow, so 1 against 8 L/min is exactly **8:1** at every time shown - the
   honest saving. On the exhausted basis the same pair reads **18.4:1** at 15
   minutes, **15.3:1** at 30 and **13.4:1** at 60. A cost readout built on
   exhausted would therefore have overstated the low-flow saving by up to
   **2.3x**, in the direction of flattering its own lesson, which is the worst
   direction available for a teaching display: a learner who later does the
   arithmetic by hand finds the simulator oversold it.

**The caveat, stated because the item's own brief invites the stronger
reading.** These runs hold the *dial* fixed, not the alveolar concentration,
so the three arms do not reach the same depth of anaesthesia - at 15 minutes
FA is 0.80% at 1 L/min, 1.37% at 4 and 1.51% at 8. The 8:1 figure is therefore
the fixed-dial ratio, which is the arithmetic a learner checks by hand, and is
not the equal-alveolar-concentration comparison a real low-flow protocol
makes (where the dial goes *up* as the flow comes down). Producing that second
comparison is design work belonging to item 28 itself, not to this correction;
what it would change is the size of the saving, never which quantity measures
it.

**The third clause of "Done when" needed no code change, checked 2026-09-19.**
There is no cost or consumption surface yet. The one place the split is
displayed is the agent-accounting panel, `accounting()` in
`app/dashboard_frame.py`, whose five lines read "Delivered", "Exhausted",
"Stored", "Unaccounted" and "Absolute error" - each naming where the agent is
or how well it is accounted for, none naming waste or cost. That is already
what the clause requires, so the requirement now lands on item 28's own
implementation, where `ROADMAP.md` records it.

**Reproducing it.** No script was committed: the measurement is thirty lines
against `AgentUptakeSystem.default()` with `set_fresh_gas_flow()` and
`agent_simulation_validation` read at the three samples, and
`CLAUDE.md`'s deterministic-tooling gate asks whether a tool will genuinely
run again. This one answers a question that is now answered. A cost readout
built under item 28 owes a reference test of its own, and that is the right
place for the arithmetic to become permanent.
