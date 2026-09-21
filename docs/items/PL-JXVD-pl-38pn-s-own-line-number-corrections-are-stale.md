---
id: PL-JXVD
title: PL-38PN's own line-number corrections are stale, so working it as written writes a second generation of wrong citations; PL-QV5Y has the same defect
priority: P3
effort: S
status: dropped
classes: defect, docs
feature: documentation-standard
touches: docs/items/PL-38PN-stale-source-line-citations-in-pl-vm40-and-pl.md, docs/items/PL-QV5Y-makefile-s-ci-timing-comments-quote-a-1230-test.md
added: 2026-09-12
closed: 2026-09-21
reason: `.claude/rules/citation-drift.md`'s line-anchor ban. The whole deliverable is a second generation of line-number repair in two item briefs, and § "Why re-pointing is refused specifically" names this item and `PL-38PN` as the mechanism it bans: "That is the mechanism, and it is why the rule bans the anchor rather than asking for more careful repair." Its own **Actually at** column was already dead by 2026-09-19. `PL-38PN` is now `dropped`, so that half is a closed brief as well; `PL-QV5Y`'s four Makefile citations go with the `Makefile` comments `PL-QV5Y` itself rewrites, so nothing is left for a separate pass. Re-judged in `PL-PT7M`'s pass, 2026-09-21
---

**Problem.** PL-38PN's own line-number corrections are stale, so working it as written writes a second generation of wrong citations; PL-QV5Y has the same defect

**Confirmed at triage, 2026-09-12.** Every corrected number in `PL-38PN` has
itself moved, and `PL-QV5Y`'s citations have all moved:

| Brief says | Actually at |
| --- | --- |
| `PL-38PN`: `_run_simulation_timer` in `app/simulation_view.py` | gone; the symbol no longer exists |
| `PL-38PN`: `AlveolarCompartment` at `alveolar.py:32` | `:38` |
| `PL-38PN`: `apply_blood_uptake` at `alveolar.py:68` | `:68` (still right) |
| `PL-QV5Y`: Makefile "lines 29-30" | `:61` |
| `PL-QV5Y`: Makefile "line 35" | `:67` |
| `PL-QV5Y`: Makefile "lines 145-146" | `:184` |
| `PL-QV5Y`: Makefile "line 22" | `:54` |

**Overtaken twice, 2026-09-19, and that is now the item's point rather than a
correction to make.** The `Actually at` column is itself stale: the Qt port took
`app/simulation_view.py` from 3,850 lines to 580, so `:3260` resolves to
nothing and `_run_simulation_timer` no longer exists under that name. Two
generations of hand-repair, both dead, is the loop `PL-G424` was filed to stop -
and `PL-G424`'s decision (2026-09-19) governs the disposition: a line number is
not a citation anchor, so these are re-anchored to symbols rather than
re-pointed at fresh line numbers. `tools/doc_check.py`'s `check_line_citations`
now fails `make check` on a citation past its file's end in a live document, so
the third generation is caught by a script rather than by a reader.

`PL-38PN`'s own `verify:` - `! grep -q 'line 943'` - passes as soon as the
original stale number goes, whether or not what replaces it is right.

**Why it matters.** `PL-38PN` is the item whose entire purpose is fixing stale
line citations, and its corrections went stale before it was started. Worked as
written it would copy `:1149` into `PL-VM40` - a `P1` item in the milestone being
implemented - and the project would have paid twice to install a wrong number.
That is the generator `PL-38PN`'s own brief gestures at when it asks whether
citations should be made mechanically checkable: a bare `:NN` decays, and
correcting one by hand produces the next one.

This is a merge candidate rather than a separate piece of work. `PL-38PN` is
`P3`, open, and has not been started; folding this into it - correct all four
citations once, in the shape `file.py:NN (symbol_name)` its brief proposes - is
one edit rather than two. `PL-6ZQY`'s consolidation pass is where that call
belongs.

**Done when.** Both briefs cite lines that resolve at the time of writing, each
citation names the symbol it points at so the next drift is mechanically
detectable, and `PL-38PN`'s `verify:` tests the corrected citation rather than
the absence of the original one.
