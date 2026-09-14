---
id: PL-V53R
title: agent_identity_check reads only simulation_view.py and keys on _apply_agent_color_scheme by name, so moving one class out of that module silences it rather than failing
priority: P2
effort: M
status: ready
classes: defect
feature: dev-tooling
touches: tools/agent_identity_check.py, tests/unit/test_agent_identity_check.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_agent_identity_check.py && grep -q 'def test_identity_writing_outside_the_view_is_found' tests/unit/test_agent_identity_check.py
---


**Problem.** agent_identity_check reads only simulation_view.py and keys on _apply_agent_color_scheme by name, so moving one class out of that module silences it rather than failing

**Why it matters.** This is the "silence is indistinguishable from a pass"
failure `ROADMAP.md` already records for the same tool under `PL-JRS3`, reached
by a different door. `IDENTITY_WRITER = "_apply_agent_color_scheme"` is matched
by name inside `VIEW = src/anesthesia_sim/app/simulation_view.py` alone, and
the identity set is *defined* as whatever that method writes. Move the class
holding the agent controls into a module of its own and the tool finds no
writer, reports on an empty identity set, and exits 0 - having measured
nothing, in the same words it uses when it has measured everything.

`tools/contrast_check.py` has the same hard-coding and is already filed as
`PL-BXB2`; this is the companion finding for the other tool, whose failure mode
is worse because it keys on a symbol as well as on a path.

**What it already cost.** `PL-B9PY` (decompose `SimulationView` so two runs can
be rendered at once) kept both new classes in `simulation_view.py` rather than
giving the per-run class a module of its own, specifically so that these two
tools would go on reading them. That is the right call for one refactor and the
wrong thing to be deciding module boundaries on: `PL-25KS` (port the dashboard
to PySide6) builds the view decomposed from the start, so the port creates
exactly the modules neither tool can see.

**Where.** `tools/agent_identity_check.py` - `VIEW`, `IDENTITY_WRITER`, and
`identity_controls`. `tests/unit/test_agent_identity_check.py` is where a case
for the empty-identity-set answer would go.

**Done when.** A view split across more than one module under `src/anesthesia_sim/app/`
is measured rather than silently skipped, and an identity set that comes back
empty is an error rather than a pass.

**Verified 2026-09-14.** `tools/agent_identity_check.py:102` fixes
`VIEW = Path("src/anesthesia_sim/app/simulation_view.py")` and `:107` fixes
`IDENTITY_WRITER = "_apply_agent_color_scheme"`. The module's own docstring
concedes the gap at `:44-51` and `:67` - rule 1 is "every `self.X` that
`_apply_agent_color_scheme` writes", and a writer outside that method "is
invisible to both rules. None exists today".

**Why it matters.** The check's reach is defined by a file path and a method
name rather than by the property it is protecting, so the ordinary act of
moving a class out of a 4 321-line module silences it. It does not fail; it
reports a pass over a smaller world. That is the same defect as `PL-0PJG` seen
from the other side, and it is due before rather than after the Qt port:
`v0.4.25` rewrites `app/simulation_view.py` wholesale, so a check anchored to
that path will either break loudly or - if a file of that name survives with
different contents - go quiet while appearing to work.

**Done when.** The check decides its own surface from the tree rather than from
a hard-coded path and method name: any module under `src/anesthesia_sim/app/`
that writes an agent identity colour is measured, a writer outside
`_apply_agent_color_scheme` is found rather than ignored, and
`tests/unit/test_agent_identity_check.py` covers a control that carries identity
from a module other than `simulation_view.py`.
