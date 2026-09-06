---
id: PL-N2X4
title: Hold tools/contrast_check.py's line citations to the file, or drop them
status: done
added: 2026-09-04
closed: 2026-09-06
verify: uv run pytest tests/unit/test_contrast_check.py && grep -q 'def test_a_line_number_citation_is_refused' tests/unit/test_contrast_check.py
priority: P2
effort: S
classes: defect, infra
feature: dev-tooling
touches: tools/contrast_check.py
---

**Problem.** `tools/contrast_check.py`'s `REQUIREMENTS` entries each cite the
lines of `app/simulation_view.py` where the pair appears - nine citations
across the ten entries, e.g. `(simulation_view.py:248-257, :519, :650, :690,
:743, :1127)`. Nothing checks them, and they were already wrong before
`PL-DHV7` touched the file: `:1127` names a line past the end of a 1072-line
module. That item's edits moved most of the rest.

**Why it matters.** The citation is the only thing telling a reader *where* a
declared pair is actually drawn, which is the judgment the tool deliberately
does not make (`.claude/rules/ui-color.md`, judgment 1: "read the source and
confirm which background it is drawn on, rather than assuming `PANEL`"). A
citation nobody can follow makes that judgment unauditable while looking
audited - the same failure mode `tools/doc_check.py`'s dangling-citation check
exists to prevent for documentation.

**Decision needed.** Make the line citations checkable, or replace them with
control names? The item argues the second is smaller and probably right; either
closes it, and they produce different work.

**Two ways out, and the choice is the work.** Either make the citations
decidable - a line-number citation is checkable the same way a path is, by
confirming the named line still mentions the color - or drop the line numbers
and cite the *control* by name (`_status_text`, `_agent_amounts_text`), which
does not rot when a module is reordered. The second is smaller and probably
right: a reader greps for the control, and `app/simulation_view.py` moves
often enough that a line-checking tool would fire on ordinary edits without
changing a decision, which `CLAUDE.md` treats as a defect in a check.

**Done when.** Every `REQUIREMENTS` entry names where its pair is drawn in a
form that a reader can follow and that a later edit to `app/simulation_view.py`
cannot silently invalidate.

**Resolved 2026-09-06, with `PL-GJDW`, in one change.** The decision this item
posed went the way it expected: the line numbers are dropped and each entry
cites the *symbol* the colour is set on. What it left open - "or make the line
citations checkable" - is answered against, for the reason written here: a
line-checking tool would fire on ordinary reordering of `app/simulation_view.py`
without changing a decision, which `CLAUDE.md` treats as a defect in a check.

The half this item did not propose is what makes the answer hold. Citing by
name is a convention, and a convention is exactly what failed the first time,
silently. So `check_citations` in `tools/contrast_check.py` now refuses any
`*.py:<line>` in a description outright and resolves every backticked symbol
against `app/theme.py` and `app/simulation_view.py`, both as `make check`
errors. A rename now reddens the gate instead of rotting; whether the named
symbol is really where the colour matters stays a reader's judgment, which is
the same line `tools/doc_check.py` draws for documentation.
