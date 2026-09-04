---
id: PL-N2X4
title: Hold tools/contrast_check.py's line citations to the file, or drop them
status: untriaged
added: 2026-09-04
---

**Problem.** Hold tools/contrast_check.py's line citations to the file, or drop them

**Why it matters.**

**Where.**

**Done when.**

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
