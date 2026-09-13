---
id: PL-JXVD
title: PL-38PN's own line-number corrections are stale, so working it as written writes a second generation of wrong citations; PL-QV5Y has the same defect
priority: P3
effort: S
status: ready
classes: defect, docs
feature: documentation-standard
touches: docs/items/PL-38PN-stale-source-line-citations-in-pl-vm40-and-pl.md, docs/items/PL-QV5Y-makefile-s-ci-timing-comments-quote-a-1230-test.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && ! grep -qF ':1149' docs/items/PL-38PN-stale-source-line-citations-in-pl-vm40-and-pl.md
---

**Problem.** PL-38PN's own line-number corrections are stale, so working it as written writes a second generation of wrong citations; PL-QV5Y has the same defect

**Confirmed at triage, 2026-09-12.** Every corrected number in `PL-38PN` has
itself moved, and `PL-QV5Y`'s citations have all moved:

| Brief says | Actually at |
| --- | --- |
| `PL-38PN`: `_run_simulation_timer` at `simulation_view.py:1149` | `:3260` |
| `PL-38PN`: `AlveolarCompartment` at `alveolar.py:32` | `:38` |
| `PL-38PN`: `apply_blood_uptake` at `alveolar.py:68` | `:68` (still right) |
| `PL-QV5Y`: Makefile "lines 29-30" | `:61` |
| `PL-QV5Y`: Makefile "line 35" | `:67` |
| `PL-QV5Y`: Makefile "lines 145-146" | `:184` |
| `PL-QV5Y`: Makefile "line 22" | `:54` |

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
