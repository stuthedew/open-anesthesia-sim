---
id: PL-KZR1
title: RunView's build_* methods are split between handing back what the run built once (build_notice, build_off_scale_notice, build_sidebar_panels) and laying its live widgets into a new container on each call (build_transport_row, build_readout_section, build_parameter_controls), so a second call to one of those three takes its widgets off screen or deletes them, and nothing in the names says which
priority: P2
effort: S
status: done
classes: refactor
feature: sidebar-panel-rebuild
touches: src/anesthesia_sim/app/run_view.py, tests/integration/test_simulation_view.py, tools/literal_home_check.py, docs/items/PL-TH35-define-the-common-view-contract-every-app-view.md
blocked-by: PL-N67T
added: 2026-09-21
closed: 2026-10-04
pr: 1356
payoff: a second call to any of RunView's build_ methods leaves the run's widgets on screen, so no caller has to know which of them is safe to call twice
verify: grep -q 'def test_a_second_build_call_leaves_each_run_widget_on_screen' tests/integration/test_simulation_view.py && grep -q 'def _lay_out_transport_row' src/anesthesia_sim/app/run_view.py && grep -q 'def _lay_out_readout_section' src/anesthesia_sim/app/run_view.py && grep -q 'def _lay_out_parameter_controls' src/anesthesia_sim/app/run_view.py
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

**Started 2026-10-04; stopped for length before the fix.** The test is
committed ahead of the fix, which is decided and written down here for
the session that picks it up.

- *The test.* `test_a_second_build_call_leaves_each_run_widget_on_screen`
  fails on the unfixed code with "a second call hid the transport row".
  Each case names a widget that has to be shown before the call: the Start
  button, the substance heading and the fresh gas flow slider. The lone
  run's name and the agent chip are hidden in that state, so the test holds
  them to the page alone.
- *The fix.* Lay the three containers out once, in the constructor, beside
  `self._sidebar_panels = self._lay_out_sidebar_panels()`.
  `_lay_out_transport_row`, `_lay_out_readout_section` and
  `_lay_out_parameter_controls` take the three methods' bodies, and the
  methods return what they stored. `RunView`'s docstring already says the
  build methods return widgets for `SimulationView` to place; it states the
  rule there once: the same widget on every call.
- *The `build_` prefix stays.* `PL-TH35` (the common View contract) decides
  what a view hands an area, so these names are rewritten there, and a
  rename now would be done twice. It would also reach `simulation_view.py`,
  `tools/contrast_check.py` and `ROADMAP.md`. `PL-TH35`'s file carries the
  case against the prefix, for that decision.
- *Two more files, both in `touches`.* `tools/literal_home_check.py`'s
  baseline keys four literals by the method holding them
  (`RunView.build_transport_row` "8", `RunView.build_readout_section` "12"
  and "4", `RunView.build_parameter_controls` "12"). They move to the
  `_lay_out_` names. `PL-TH35` takes the note.
- *Then.* Revert each of the three fixes in turn and see the test fail on
  it. Run `make check` and `bin/docket verify --self PL-KZR1`, close the
  item out, and open the pull request. It holds for the owner's read
  (`src/`, `tests/`).
- *`verify:` rewritten.* The grep for the test's name alone passed once the
  test was committed, before any fix. `bin/docket check` refused that, so
  `verify:` now also greps for the three `_lay_out_` methods the fix adds.

**Done 2026-10-04, as planned above.** Each of the three fixes, reverted
alone, fails the test on its own case: "a second call hid the transport
row", "the readout section", "the setting controls". `RunView`'s docstring
states the rule once, so `build_sidebar_panels` no longer repeats it. The
`literal_home_check.py` baseline still holds 42 literals. Four of them are
now keyed under the `_lay_out_` methods that contain them.
