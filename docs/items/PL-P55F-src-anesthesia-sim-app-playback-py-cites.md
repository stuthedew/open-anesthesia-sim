---
id: PL-P55F
title: src/anesthesia_sim/app/playback.py cites SimulationView._run_simulation_timer, a method the 2026-09-15 PySide6 port deleted, so live source prose names a mechanism the tree has not had for six days
priority: P3
effort: S
status: ready
classes: docs
feature: gate-staleness-sweep
touches: src/anesthesia_sim/app/playback.py
added: 2026-09-21
payoff: A reader of playback.py can grep the mechanism it names and find it, so the paragraph on when a control change takes effect is confirmable rather than taken on trust.
verify: grep -q 'RunView.step_tick' src/anesthesia_sim/app/playback.py
---

**Problem.** src/anesthesia_sim/app/playback.py cites SimulationView._run_simulation_timer, a method the 2026-09-15 PySide6 port deleted, so live source prose names a mechanism the tree has not had for six days

**Where.** `src/anesthesia_sim/app/playback.py:54`, in the module docstring's
paragraph "A control change timed to the step is available at every rate:
pause, change, resume."

**What replaced it.** `RunView.step_tick`, at
`src/anesthesia_sim/app/run_view.py:988`, which returns before taking any step
while `self.controller.is_running` is false. So the *claim* the paragraph makes
is still true - a setting changed while paused acts from the step the run
resumes on - and only the symbol naming the mechanism is dead. Verified
2026-09-21: no `def _run_simulation_timer` exists anywhere under `src/`, while
`SimulationView` itself survives the port at
`src/anesthesia_sim/app/simulation_view.py:215`. That pairing is what makes the
name look live to a reader who greps the class rather than the method.

**Why it matters.** This is live source prose rather than a queue brief, and it
is the paragraph a reader consults to learn *when a control change takes
effect* - which this project treats as timeline exactness rather than tidiness.
A reader who greps the named method finds nothing and cannot confirm the claim;
one who assumes the name is current goes looking for pause behaviour in a class
that no longer implements it. `CLAUDE.md`'s sweep-the-docs rule names this
case: a reader who trusts a wrong statement about which mechanism is running
can reach a wrong conclusion from a correct number.

**Done when.** `src/anesthesia_sim/app/playback.py` names the mechanism that
actually holds the run - `RunView.step_tick` - in place of
`SimulationView._run_simulation_timer`, and the surrounding sentence still
states the same behaviour, which `step_tick`'s early return preserves.
