---
id: PL-77DZ
title: Four ROADMAP.md citations and two open briefs anchor inert_splitter at src/anesthesia_sim/app/qt_widgets.py:784, but the function is at line 1651 now, and .claude/rules/citation-drift.md says a line number is not a citation anchor
priority: P3
effort: S
status: ready
classes: housekeeping
touches: ROADMAP.md, docs/items/PL-9LNF-three-app-surfaces-own-state-a-layout-could.md, docs/items/PL-W9P6-build-the-one-adapter-module-that-drives-the-qt.md
added: 2026-09-26
payoff: a reader following any live citation of the inert splitter lands on the function itself, and the citation stops drifting because it names a symbol rather than a line
verify: ! grep -qE 'qt_widgets\.py:[0-9]+' ROADMAP.md docs/items/PL-9LNF-three-app-surfaces-own-state-a-layout-could.md docs/items/PL-W9P6-build-the-one-adapter-module-that-drives-the-qt.md
---

**Problem.** Four ROADMAP.md citations and two open briefs anchor inert_splitter at src/anesthesia_sim/app/qt_widgets.py:784, but the function is at line 1651 now, and .claude/rules/citation-drift.md says a line number is not a citation anchor

**Found 2026-09-26.** `grep -n 'def inert_splitter' src/anesthesia_sim/app/qt_widgets.py`
prints line 1651; line 784 is now inside `set_readouts`.
The live citations are ROADMAP.md's four - v0.5.0's declined-to-Gate-2
section, v0.6.0's Goal, v0.6.0's gate paragraph on `PL-Y04W`, and § "The gate
is a snapshot, not a moving target" - and the open briefs of `PL-W9P6` (the Qt
adapter build item) and `PL-9LNF` (three app/ surfaces owning state a layout
could relocate). The closed briefs of `PL-83LS`, `PL-BNYF`, `PL-LPHT` and
`PL-NMTF` cite it too and are records under `.claude/rules/citation-drift.md`,
so they stay as written.

**The fix is the symbol, not a new number.** Re-pointing at 1651 mints the next
drift, which is the loop `.claude/rules/citation-drift.md` refuses. Where a
sentence already names `inert_splitter`, drop the `:784`; where it does not,
name the function in `src/anesthesia_sim/app/qt_widgets.py`.

**Generator check.** An instance of `PL-G424`'s fact - a line number is not a
citation anchor - filed after that head closed on 2026-09-19. Its rule banned
the anchor going forward and measured the standing documents at 0 stale of 5
that day, so these four were left in place while still correct; they have gone
stale since, which is the mechanism the rule describes rather than a new one.
