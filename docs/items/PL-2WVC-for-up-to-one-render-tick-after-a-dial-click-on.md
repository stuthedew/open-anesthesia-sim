---
id: PL-2WVC
title: For up to one render tick after a dial click on a running run, the readouts and the compartment schematic show a later step than the charts, on main as on the PL-RF2S branch
status: untriaged
feature: every-view-in-run-state-tests
added: 2026-11-11
---

**Problem.** For up to one render tick after a dial click on a running run, the readouts and the compartment schematic show a later step than the charts, on main as on the PL-RF2S branch

**Found on 2026-11-11 by a review of `PL-RF2S`'s second pull request, and not
fixed there.** A dial click on a running run applies the setting and asks for a
frame at once. Until the next render tick, the run's readouts and the
compartment schematic show the step after the click, and both charts still
show the frame before it. The reviewer saw the same on `main` at `35294da61`
and on the branch at `70dbdc525`. Its script was
`repro5_readouts_ahead_of_chart.py` in that session's scratchpad, which does
not outlive the session.

**Where it may belong.** `PL-RF2S`'s third pull request puts the chart frame
for each window into the one value that the whole screen is drawn from. The
readouts and the charts would then come from one state on every draw. Triage
decides whether this item closes with that pull request or is dropped as a
difference of one tick (0.2 s) that no learner can act on.
