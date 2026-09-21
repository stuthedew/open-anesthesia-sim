---
id: PL-KZR1
title: RunView's build_* methods are split between returning a stored widget (build_notice, build_off_scale_notice) and constructing a new one on each call (build_sidebar_panels, build_readout_section), with nothing in the names saying which
priority: P3
effort: S
status: blocked
classes: refactor
feature: sidebar-panel-rebuild
touches: src/anesthesia_sim/app/run_view.py
blocked-by: PL-N67T
added: 2026-09-21
payoff: a caller can tell from a build_ method name whether calling it twice is safe
---

**Problem.** RunView's build_* methods are split between returning a stored widget (build_notice, build_off_scale_notice) and constructing a new one on each call (build_sidebar_panels, build_readout_section), with nothing in the names saying which

**Why it matters.** `PL-N67T` and `PL-JS0X` are both this ambiguity being paid
for. A caller reading `build_sidebar_panels` beside `build_notice` has nothing
in either name to say that one hands back the widget already on screen and the
other builds a replacement and reparents the live labels into it. The reasonable
reading - that a `build_*` method is a getter, which is how `SimulationView`
treats them - is the one that dismantles the display.

**Blocked on `PL-N67T`** rather than merely related to it. The convention cannot
be written until that item settles whether a second call returns the placed
panels or refuses. Either answer then names the rule for all eight methods;
neither can be applied to them ahead of it.
