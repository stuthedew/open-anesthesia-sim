---
id: PL-V53R
title: agent_identity_check reads only simulation_view.py and keys on _apply_agent_color_scheme by name, so moving one class out of that module silences it rather than failing
status: untriaged
added: 2026-09-14
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
