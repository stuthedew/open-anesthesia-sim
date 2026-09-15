---
id: PL-QRD1
title: A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW
status: untriaged
added: 2026-09-15
---

**Problem.** A dashboard showing two runs lets either selector switch its own agent, which the shared MAC axis then refuses only after the controller has switched: lock the selectors while two runs are shown, with PL-8PSW

**Found by the Qt-correctness review of `PL-25KS`, 2026-09-15.** `RunView`
keeps its own agent selector, and `SimulationView` admits two runs. Switching
one run's agent goes through `SimulationController.set_agent`, which succeeds
on a trunk, and the refusal comes a moment later from `assemble_chart_frame`
(two agents cannot share one MAC axis) - after the controller has already
switched. `_halt_every_run` then fails both runs. The port made the halt
itself visible (`present_halt` writes each run's status word and banner with
no frame), but the switch should be refused before it reaches the controller:
while two runs are shown the selectors are locked, in the same disabled-and-
hidden form the running-agent chip uses, because a comparison is of one
agent by construction. Only reachable today by constructing a two-trunk
dashboard, which no shipped entry point does; `PL-8PSW` (overlay two branches)
is where two runs first reach a reader, and a branch's `set_agent` already
refuses, so this is that item's to settle - lock, or rely on the branch
refusal and say so.
