---
id: PL-41YP
title: Assert every required displayed output reaches the rendered view
priority: P2
effort: M
status: done
classes: test
feature: model-claims-held-by-tests
milestone: v0.6.22
touches: tests/
added: 2026-08-25
closed: 2026-11-22
pr: 2248
tests: tests/integration/simulation_view/test_simulation_view_readouts.py::test_every_minimum_displayed_output_reads_its_value_from_its_widget
---

> **Groomed 2026-09-22 (`PL-Y4YG`): still owed, and its premise has moved.**
> `PL-036` closed on 2026-09-22 binding § "Minimum displayed outputs" to a
> named test per bullet rather than to a `SimulationSnapshot` field (ratified
> over the field, because a field "proves the value still travels, never that
> a widget still draws it" - the comment above `BOUND_FAMILIES` in
> `tools/doc_check.py`). So **Problem**'s first sentence describes a design
> that was not adopted. The gap survives it: of the 33 tests the section
> names, 27 assert the toolkit-free frame or the model and 6 build a Qt
> widget, so the chain is now doc → named test → formatted value, and which
> bullets have no test reaching a drawn widget is the first thing to count.
> The harness **Notes** implied was missing exists: `tests/integration/`
> builds the real view offscreen (`PL-YCWZ`).
>
> Build it now. It is one test file with nothing downstream; switching its
> list to `PL-NWTM`'s declaration is a small change once that exists, and
> `PL-NWTM`'s own after-a-split-and-a-close test should extend this one rather
> than write a second. Naming the new test in each bullet lets the existing
> binding carry the widget link with no new check.

**Problem.** PL-036 makes `docs/INTERFACE.md` § "Minimum displayed outputs" name
the `SimulationSnapshot` field behind each bullet and checks those fields
exist. That proves the field exists, not that the interface displays it.

**Why it matters.** A snapshot field can exist with no widget behind it —
`circuit_time_constant_s` was exactly that for several releases. The doc →
field → widget chain has a second link, and a required output silently losing
its display is a presentation failure of the kind `CLAUDE.md` treats as
safety, not tidiness.

**Where.** `tests/`, against `app/simulation_view.py`.

**Notes.** This cannot live in `tools/doc_check.py`: reaching the widget needs
the application package, which that tool deliberately never imports so it can
run in a bare checkout. A test is the right home.

**Done when.** A test asserts each required displayed output reaches the
rendered view, and fails when one loses its widget.

**Confirmed 2026-09-19 by `PL-4FBP`'s ratified convention** (a live assertion names what it asserts, a dated one carries its date).
Unchanged: the test carrying the field-to-widget link is still what this item
is for. It reads `PL-NWTM`'s declaration once that exists, so the ordering
between the two is unaffected by the convention.

**Noted 2026-10-18 by `PL-NWTM`.** The unconditional part of § "Minimum
displayed outputs" now has a declaration in code,
`src/anesthesia_sim/app/unconditional_set.py`, and
`RunView.unconditional_widgets` maps each of its values to the widget that
draws it. Build this item's assertion over that declaration rather than over a
list of its own, as `PL-NWTM`'s Done when asks.

**Checked 2026-11-21**, by `PL-5FMC` (the check of `docs/INTERFACE.md` against the code), at `2452b9b4e`. Every output that § "Minimum displayed outputs" requires has a test that reaches a widget, though no single test covers them all. `test_every_layout_operation_leaves_the_unconditional_set_on_screen` already asserts that each widget of the unconditional set is visible after every layout operation. What is still missing is one test that walks the section's own list and reads each value's text from its widget.

**Checked 2026-11-22** against `d4e8200`: partly done, as the check of 2026-11-21 found. Every output that § "Minimum displayed outputs" requires has some test that reaches a widget, and `test_every_layout_operation_leaves_the_unconditional_set_on_screen` (`tests/integration/test_layout_safety.py`) holds the unconditional set on screen after every layout operation. What is left is one test that walks the section's list, through `RunView.unconditional_widgets` and `app/unconditional_set.py`, and reads each value's text from its widget. No test named `test_every_minimum_displayed_output...widget` exists yet.

**Closed 2026-11-22.** `test_every_minimum_displayed_output_reads_its_value_from_its_widget`, in `tests/integration/simulation_view/test_simulation_view_readouts.py`, walks `unconditional_set(INHALED_AGENT)`, finds each value's widget through `RunView.unconditional_widgets`, and checks that the widget is shown and reads this run's value. The run is isoflurane with a dial change, halted at the supported run length, so the halt reason and the control record are on screen. The expected concentrations come from a fresh `AgentUptakeSystem` given the same settings, and the expected 1 MAC from the agent's data file. Wiring the 1 MAC value to the delivered line's widget made it fail with `one_mac reads 'Delivered 1.50% (1.28 ×MAC)'`. Files checked: `docs/INTERFACE.md` § "Minimum displayed outputs" (its note for developers now names the test), `app/unconditional_set.py`'s docstring (still true).

**Blind review, 2026-11-22.** Both passes found that the test read only each compartment's percent and not its multiple of 1 MAC, and that it accepted a control record with the wrong time or starting value. It now reads the multiple of 1 MAC beside each percent, compares the record's line exactly, and reads only labels that are shown.
