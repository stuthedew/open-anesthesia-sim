---
id: PL-H4N8
title: ROADMAP planned-milestone item 28 specifies agent cost 'from the exhausted-agent amount', but cost is what left the bottle, which is the delivered amount - exhausted understates it mid-run by exactly what is still stored
status: untriaged
feature: liquid-agent-consumption
added: 2026-09-16
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
