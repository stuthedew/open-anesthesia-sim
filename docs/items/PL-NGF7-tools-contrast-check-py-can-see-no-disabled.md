---
id: PL-NGF7
title: tools/contrast_check.py can see no disabled-state colour, because none of them is a constant in theme.py
priority: P2
effort: M
status: needs-decision
classes: infra, test
feature: presentation-safety
touches: tools/contrast_check.py, src/anesthesia_sim/app/theme.py, src/anesthesia_sim/app/simulation_view.py, tests/unit/test_contrast_check.py
added: 2026-09-06
---

**Problem.** `tools/contrast_check.py` extracts colour constants from
`src/anesthesia_sim/app/theme.py` with `ast`, deliberately, so it runs in a
bare checkout. Every colour a control takes when Flet/Material disables it
comes from the Material theme rather than from `theme.py`, so it is not merely
undeclared in `REQUIREMENTS` — it is unreachable to the tool that would measure
it. `make check` is therefore green on the whole disabled half of the
interface, and will stay green however that half renders.

**Why it matters.** The tool's docstring is honest about its own scope: it
decides "whether a declared requirement meets its declared ratio", and lists
"which pairs actually appear on screen together" among what it must never
decide. So this is a coverage gap in what a person declared, not an arithmetic
defect. But the practical reading of a green contrast check is that the
interface's colour pairs are covered, and one whole rendering state is not —
the state the app spends most of its time in, since a run disables controls.
`PL-61WW` (agent name loses contrast against the agent colour during a run) is
the instance that surfaced it; that one control is fixable without closing this.

**Where.**

- `tools/contrast_check.py` — the `ast` extraction, and `REQUIREMENTS`.
- `src/anesthesia_sim/app/theme.py` — where a disabled foreground would have to
  become an explicit constant for any of it to be measurable.
- `src/anesthesia_sim/app/simulation_view.py` — the `disabled=` assignments;
  `2123` (agent dropdown) and `2233` (Start) are the two known.

**Done when.** Either every control disabled during normal operation takes an
explicit foreground from `theme.py` with a declared requirement measuring it,
or the tool states in its docstring that disabled states are out of scope and
says what covers them instead. The second is a legitimate answer — but it has
to be a decision somebody took, not the current situation, which is that
nothing covers them and nothing says so.

**Decision needed.** Does every control disabled during normal operation take
an explicit foreground from `theme.py` with a declared requirement measuring
it, or does `tools/contrast_check.py` state in its docstring that disabled
states are out of scope and name what covers them instead? The second is a
legitimate answer and the item is explicit that it has to be a decision
somebody took: today nothing covers them and nothing says so.

**Classed `infra, test` rather than `defect`, and it can be overruled.** The
tool's docstring already disclaims deciding which pairs appear on screen
together, so nothing it asserts is false - what is missing is coverage a reader
of a green check assumes. `PL-61WW` is the instance and is fixable without
closing this.
