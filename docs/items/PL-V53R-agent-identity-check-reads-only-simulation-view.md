---
id: PL-V53R
title: agent_identity_check reads only simulation_view.py and keys on _apply_agent_color_scheme by name, so moving one class out of that module silences it rather than failing
priority: P1
effort: M
status: done
classes: defect, safety, infra
feature: qt-port
touches: tools/agent_identity_check.py, tests/unit/test_agent_identity_check.py, docs/ARCHITECTURE.md, Makefile
added: 2026-09-14
closed: 2026-09-14
verify: uv run pytest tests/unit/test_agent_identity_check.py && grep -q 'def test_the_writer_is_found_in_whichever_app_module_holds_it' tests/unit/test_agent_identity_check.py
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

**Corrected on triage, 2026-09-14.** The paragraph above overstates one case.
Moving the class that holds `_apply_agent_color_scheme` out of
`simulation_view.py` does *not* exit 0: `problems()` returns the empty-set
error the moment `identity_controls` finds no writer, which is `PL-JRS3`'s
probe C failing with the correct message. The silent case is the *other* class
moving. A control constructed with an agent colour in a module the tool does
not read is outside rule 2, and a `disabled` write on an identity control in
such a module is outside rule 1, and neither absence prints anything. `PL-B9PY`
kept both classes in one file to stay inside the tool's view; the port will
not, so the tool has to read whatever module the view is split across.

**Done when, restated.** The tool reads every module under
`src/anesthesia_sim/app/`. The writer is found in whichever module holds it,
exactly once - none is the existing error, two is a second writer of agent
colour, which the single-writer design exists to prevent. Rule 1 reads the
`disabled`/`visible` pairing inside the writer's own class, so a same-named
control in another class is not mistaken for the identity control; rule 2
reads every class in every module, so a control built from an agent colour
anywhere in the interface must be one the writer writes. The reading side of
`PL-0PJG` lands in the same change.

**What landed, 2026-09-14.** `read_modules` parses every `.py` under
`src/anesthesia_sim/app/`, and `find_writers` looks for `_apply_agent_color_scheme`
as a method of any class in any of them: none is the existing empty-set error,
two is a second-writer error naming both, and the success line names the one
found as `module:Class.method`. Rule 1 reads the `disabled`/`visible` pairing
inside the writer's own class, because `self.X` names that class's attribute
and a same-named attribute elsewhere is a different control; rule 2 reads
every class in every module, because the writer can only write its own class's
attributes. On the shipped tree the class scoping surfaced nothing new - the
run reports 6 identity controls, 3 disabled-state writes read across 11
modules, 1 of them on an identity control - and the four new tests cover the
writer in another module, rule 2 reaching another module, a second writer, and
a same-named control in another class staying quiet.

**Triaged twice on 2026-09-14.** A second pass (`PL-6FJ5`, `PL-66X4`) verified
the finding independently and triaged it at `P2` under `dev-tooling`; the
fields above are the project owner's (`P1`, `safety`, `qt-port`, 2026-09-14),
and the work closed on that basis. The second pass's verification and brief
follow unchanged, because a merge that keeps one of two answers is what
`PL-N1JK` recorded, and its "Done when" is compared against what landed
where the two differ.

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
