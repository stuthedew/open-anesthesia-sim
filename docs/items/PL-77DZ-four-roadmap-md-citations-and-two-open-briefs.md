---
id: PL-77DZ
title: Four ROADMAP.md citations and two open briefs anchor inert_splitter at src/anesthesia_sim/app/qt_widgets.py:784, but the function is at line 1651 now, and .claude/rules/citation-drift.md says a line number is not a citation anchor
priority: P3
effort: S
status: done
classes: housekeeping
touches: ROADMAP.md, docs/items/PL-9LNF-three-app-surfaces-own-state-a-layout-could.md, docs/items/PL-W9P6-build-the-one-adapter-module-that-drives-the-qt.md, docs/items/PL-L8RN-nothing-enforces-the-one-adapter-qsplitter.md
added: 2026-09-26
closed: 2026-09-26
pr: 1132
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

**Done 2026-09-26: seven anchors, not six.** `PL-9LNF` held two. Every one was
written while line 784 was `def inert_splitter` (`e5ad821f`, `d4f7f187`), except
ROADMAP.md's fourth, added by `e6cdfd93` when that line was already inside
`_lay_out`, which named the function. The four sentences naming
`inert_splitter` lost the `:784`. The three that did not - ROADMAP.md's
declined-to-Gate-2 section and § "The gate is a snapshot, not a moving target",
and `PL-9LNF`'s basis paragraph - now cite
`src/anesthesia_sim/app/qt_widgets.py`'s `inert_splitter`, the rule's own form.
The quote `PL-9LNF` takes from its docstring still matches word for word.

**`PL-L8RN`'s brief rode along**, repaired in place under
`.claude/rules/citation-drift.md` rather than filed, which is why its file is in
`touches`. That open item (nothing enforces the one-adapter `QSplitter`
confinement) carried three more drifted line anchors: `qt_widgets.py:58` for the
`QSplitter` import, now line 63, and `docs/interface-provenance.md:737` twice for
the paragraph now at line 739. The import now cites the file, and the paragraph
is named by its quoted lead and, where the sentence already gave it, its
§ "Adopted" heading.
