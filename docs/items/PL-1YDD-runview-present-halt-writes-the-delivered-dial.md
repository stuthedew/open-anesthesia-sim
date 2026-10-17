---
id: PL-1YDD
title: RunView.present_halt writes the delivered dial's name from settings().agent_display_name while the subtitle, chip, substance heading, selector and colour scheme stay the last frame's, so a halt on the first frame after a successful set_agent would show two agents; no control reaches it today, since _start_new_case halts on a refused snapshot before set_agent (found reviewing PL-85LJ)
priority: P2
effort: S
status: ready
classes: defect, ux
feature: every-control-restates-the-halt
touches: src/anesthesia_sim/app/run_view.py, src/anesthesia_sim/app/dashboard_frame.py, tests/integration/test_simulation_view.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-10-17 triage pass
added: 2026-10-12
payoff: A run halted right after an agent change names one agent everywhere on screen, rather than the new agent on the dial and the old one in the header, chip and heading.
verify: grep -q 'def test_a_halt_after_an_agent_change_names_one_agent' tests/integration/test_simulation_view.py
---

**Problem.** RunView.present_halt writes the delivered dial's name from settings().agent_display_name while the subtitle, chip, substance heading, selector and colour scheme stay the last frame's, so a halt on the first frame after a successful set_agent would show two agents; no control reaches it today, since _start_new_case halts on a refused snapshot before set_agent (found reviewing PL-85LJ)

**Reproduced 2026-10-17** (triage), by forcing the frame to fail after a
successful agent change: a fresh run (no recorded run, so the pick starts a
new case without a question), `simulation_view.assemble_chart_frame`
monkeypatched to raise, then desflurane picked in the selector. After the
halt the controller's agent is desflurane and the delivered dial reads
"Delivered desflurane", while the subtitle reads "... Sevoflurane patient
model", the running-agent chip "Sevoflurane" and the substance heading
"Modelled concentrations: Sevoflurane"; the selector reads desflurane. Two
agents named on one halted run. Script:
`scratchpad/ui-a/test_repro_ui_a.py::test_1ydd`.

**Why it matters.** Agent identity is the one fact every other value on the
run is read against, and a halted screen naming two agents leaves a reader
unable to tell which agent the dials, the stale readouts and the chart
belong to. **Not reachable today, which is what sets the band:** the only
frame failures after `set_agent` are latent faults - a snapshot that refuses
a value (`PL-7DJK`, which no supported setting reaches) or an
`assemble_chart_frame` raise - and `_start_new_case` already halts on a
refused snapshot before `set_agent` runs. So `defect`/`ux` at `P2`, like its
siblings in `every-control-restates-the-halt`, rather than `safety`/`P1`.

**Done when.** `RunView.present_halt` writes every agent-identity widget it
does not leave to a frame - the subtitle, the chip, the substance heading,
the selector and `_apply_agent_color_scheme` - from the same
`SimulationController.settings()` it already writes the dials from (the
controller's own agent, built from no compartment value), so a halted run
names one agent; `substance_heading` takes what both a snapshot and
`RunSettings` carry rather than a snapshot. A test,
`test_a_halt_after_an_agent_change_names_one_agent` in
`tests/integration/test_simulation_view.py`, picks a new agent on a fresh
run with the frame forced to fail and asserts the dial name, subtitle, chip,
substance heading and selector all name the controller's agent.
