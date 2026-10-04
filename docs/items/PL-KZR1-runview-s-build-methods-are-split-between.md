---
id: PL-KZR1
title: RunView's build_* methods are split between handing back what the run built once (build_notice, build_off_scale_notice, build_sidebar_panels) and laying its live widgets into a new container on each call (build_transport_row, build_readout_section, build_parameter_controls), so a second call to one of those three takes its widgets off screen or deletes them, and nothing in the names says which
priority: P2
effort: S
status: ready
classes: refactor
feature: sidebar-panel-rebuild
touches: src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py
blocked-by: PL-N67T
added: 2026-09-21
payoff: a second call to any of RunView's build_ methods leaves the run's widgets on screen, so no caller has to know which of them is safe to call twice
verify: grep -q 'def test_a_second_build_call_leaves_each_run_widget_on_screen' tests/integration/test_simulation_view.py
---

**Problem.** RunView's build_* methods are split between handing back what the run built once (build_notice, build_off_scale_notice, build_sidebar_panels) and laying its live widgets into a new container on each call (build_transport_row, build_readout_section, build_parameter_controls), so a second call to one of those three takes its widgets off screen or deletes them, and nothing in the names says which

Retitled 2026-10-04, when `PL-N67T` moved `build_sidebar_panels` to the first
group; it was filed naming it and `build_readout_section` as the two that
construct.

**Why it matters.** `PL-N67T` and `PL-JS0X` are both this ambiguity being paid
for. A caller reading `build_sidebar_panels` beside `build_notice` has nothing
in either name to say that one hands back the widget already on screen and the
other builds a replacement and reparents the live labels into it. The reasonable
reading - that a `build_*` method is a getter, which is how `SimulationView`
treats them - is the one that dismantles the display.

[superseded 2026-10-04] **Blocked on `PL-N67T`** rather than merely related to it. The convention cannot
be written until that item settles whether a second call returns the placed
panels or refuses. Either answer then names the rule for all eight methods;
neither can be applied to them ahead of it.

**Unblocked 2026-10-04: `PL-N67T` settled the fork as handing back.**
`build_sidebar_panels` now returns the two panels the run laid out at
construction, the same two on every call. A layout being rearranged into areas
will ask for them again to move them, and refusing would block that
(`.claude/rules/ui-areas.md`). That names the rule for all eight methods: a
`build_*` method hands back what the run built once.

**Three still break it, measured the same day** against a shown
`SimulationView` over one run. `build_transport_row`, `build_readout_section`
and `build_parameter_controls` lay the run's live widgets into a new container
on every call. Kept, a second call's result takes them off screen: the Start
button, the substance heading and the fresh gas flow slider each read as
hidden. Dropped, it deletes them. The new container is Python-owned, so garbage
collection takes the widgets it adopted with it, and the next write to one
raises `RuntimeError`. `SimulationView._place_run` calls each once, so nothing a
learner sees is affected today.

This is `PL-N67T`'s defect three times over, not naming alone, so this item
ranks with that one at `P2`. The test under `verify:` is the shape of
`test_a_second_build_sidebar_panels_leaves_the_run_labels_on_screen`, extended
to each of the three.

**Done when.** All eight hand back what the run built once. A second call to
each of the three leaves its widgets on screen and in the view, which
`test_a_second_build_call_leaves_each_run_widget_on_screen` asserts, before
the call and after it. Whether the `build_` prefix stays, now that none of the
eight builds on a call, is this item's own call: a rename goes through every
`SimulationView` call site.
