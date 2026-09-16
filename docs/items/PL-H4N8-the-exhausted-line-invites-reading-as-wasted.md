---
id: PL-H4N8
title: The exhausted line invites reading as 'wasted', but this model has no metabolism so nearly all stored agent becomes exhausted by end of case - the figure that means cost is delivered
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
