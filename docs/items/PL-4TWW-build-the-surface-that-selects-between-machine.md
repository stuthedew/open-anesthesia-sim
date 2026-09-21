---
id: PL-4TWW
title: Build the surface that selects between machine profiles, which planned-milestone item 40 deliberately omits and item 1 does not schedule
priority: P3
effort: M
status: blocked
classes: ux, anticipated
feature: machine-profile-framework
touches: src/anesthesia_sim/app
blocked-by: PL-TH35, PL-R1WQ, PL-TBMK
added: 2026-09-21
payoff: makes the machine a thing a learner can choose, which is what turns PL-WZVZ's attribution requirement from a table nobody reaches into the explanation beside the choice
---

**Problem.** Build the surface that selects between machine profiles, which planned-milestone item 40 deliberately omits and item 1 does not schedule

**Why it matters.** `PL-WZVZ`'s `Done when.` opens with "selecting between
machines shows the parameters that differ", and nothing in the project builds a
selection surface. Planned-milestone item 40 is explicit that it ships a second
profile loadable and **selectable in code**, "with no chooser and no displayed
value changing", and planned-milestone item 1 keeps the interlock baseline. So
the chooser is wanted, named in another item's done condition, and scheduled
nowhere.

**Filed so the condition is in a field rather than in prose** (`PL-0H5D`).
`PL-WZVZ` recorded only its display-surface blockers, so closing those in v0.6.0
would have reported it promotable while this was still missing.

**What blocks it, and note the first two are the same two `PL-WZVZ` carries.**
This is itself a new display surface, so planned-milestone item 34's standing
rule reaches it: `PL-TH35` (the View contract) and `PL-R1WQ` (the view
registry). And `PL-TBMK`, because a chooser over one profile is a control with
one option — the surface is only meaningful once there is a second machine.

**The attribution requirement travels with it.** Whatever this surface is, it is
where `PL-WZVZ`'s rule lands: a machine is never presented as a trade name
alone, and the parameters that differ, their units and their sources are shown
beside the choice. Build them together rather than building the chooser and
filing the explanation.

**`anticipated`** because no machine is selectable today, so no trade name is
displayed and nothing is being misattributed.

**Done when.** A learner can choose between the machine profiles the build
carries; the choice names the parameters that differ rather than only the
machines; and the surface states once that these are the parameters the model
uses, not the whole difference between the machines.
