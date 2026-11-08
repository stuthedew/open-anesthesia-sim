---
id: PL-4L49
title: tools/contrast_check.py measures only declared pairs, so a control that declares no colour reads as covered when nothing measures it
priority: P2
effort: M
status: done
classes: defect, infra
feature: platform-palette
milestone: v0.5.4
touches: tests/integration/test_simulation_view.py, tools/contrast_check.py, tests/unit/test_contrast_check.py, docs/MODEL.md, docs/ARCHITECTURE.md, .claude/rules/ui-color.md
added: 2026-09-17
closed: 2026-09-22
pr: 897
verify: uv run pytest tests/integration/test_simulation_view.py tests/unit/test_contrast_check.py -q && grep -q 'def test_every_control_that_paints_its_own_content_declares_a_foreground' tests/integration/test_simulation_view.py
---

**Problem.** `tools/contrast_check.py` measures only declared pairs, so a
control that declares no colour reads as covered when nothing measures it.

The report line is `contrast: 24 of 24 declared requirements meet WCAG 2.2 AA,
17 modules read under src/anesthesia_sim/app/, 0 known shortfalls, 0 errors`.
It counts requirements, and a requirement exists only where somebody wrote a
colour down. A control that writes none contributes nothing to the numerator
*or* the denominator, so the line reads identically whether the interface is
fully covered or has three invisible controls on it - which is exactly the
state `PL-DHBX` was found in, by the project owner, on his own screen.

The tool's docstring is careful about the holes it knows of: "a color that is
neither a module-level constant nor a literal - one computed, or taken from a
toolkit's own palette by name - is not a value this tool can see". That
sentence describes this. What it does not do is *report* it, and an
unmeasurable colour that is also unmentioned is indistinguishable from one that
does not exist.

**Why it matters.** This is a check whose output looks authoritative and is
silently partial - `CLAUDE.md`'s first compounding-friction test, a check
passing while the guarantee it stands for is void. It is also the reason
`PL-DHBX` reached a release: nothing in `make check` could have caught three
controls drawing their labels from the host palette, and nothing said so.

**The decidable part, and where it should live.** Whether a widget declares a
foreground is answerable by walking the built widget tree: a widget declares
one if its own stylesheet, or a non-object-name-scoped ancestor's, sets
`color:`. That is decidable; *which* widgets ought to declare one is not -
scrollbars, splitter handles and sliders draw no text and are deliberately the
platform's. So the shape is an allow-list of the platform-owned chrome, and a
failure for anything text-bearing outside it.

It belongs in `tests/integration/test_simulation_view.py` rather than in a new
tool under `tools/`: the whole dashboard is already constructed headless there,
and the question needs a *built* tree - the `ast` extraction `contrast_check`
runs cannot see which widget a stylesheet reached. Note the substring trap
found while diagnosing `PL-DHBX`: matching `color:` also matches
`background-color:`, which made a first pass report almost nothing undeclared.

The matching audit found these drawing text or a visible surface with no
declared foreground, after `PL-DHBX` landed: `QScrollBar` (6),
`QSplitterHandle` (5), `QSlider` (4), `PlotWidget` (2). None draws a label
today; each should be named in the allow-list with the reason, so that the
next one to appear fails instead of joining them silently.

**Done when** a test holds every text-bearing control in the built dashboard to
declaring its own foreground, the platform-owned exceptions are named
individually with their reason, and `contrast_check`'s report line says how
many controls it could not measure rather than only how many it could.

**Moved from `ROADMAP.md` on 2026-11-08 (`PL-4BCF`).** `ROADMAP.md`'s § "Completed: v0.5.0 - the case you can branch" carried this under § "Declined to Gate 2 on the refilling-queue ground", Gate 1's record of how it disposed of debt it did not hold. In it, "this gate", "the gate" and "the list" are Gate 1, v0.5.0's frozen list; "this milestone" is v0.5.0; "the freeze" is Gate 1's freeze on 2026-09-06; "this section" and "this subsection" are that heading's section; "the first twenty-nine" are the 2026-09-08 group that opened the section, and "the first thirty" are those with `PL-HX5C`; "today" is the day the paragraph was written; and "above" and "below" point within `ROADMAP.md` as it then stood. The section now lists this item under "The refilling-queue ground".

> `PL-4L49` records that `tools/contrast_check.py` measures only *declared* pairs, so a control that declares no colour is treated as covered. It passes the presence test. The check has had that limitation since long before this freeze, and the limitation is why `PL-DHBX` could ship. `PL-4L49` is declined on the refilling-queue arithmetic above, not on its lane. It is classed `defect` and `infra`, not `safety` or `science`. The one instance it would have caught is closed. And the gate is already the largest this project has held, and it is not draining. `PL-BXB2` is the nearest precedent that was admitted, and it differs from `PL-4L49` in the way that matters. In `PL-BXB2`, a colour that nothing measured could be an ISO 5360 agent colour, which is why that item was `safety`. An *undeclared* control cannot be an agent colour, because every control that carries agent identity is written by `_apply_agent_color_scheme` and guarded by `tools/agent_identity_check.py`.
