---
id: PL-3DXV
title: Four qt-port items carry a verify: command another port item satisfies, so each passes while still open once its neighbour lands and reddens the whole-store verify replay on main
priority: P3
effort: S
status: ready
classes: defect, infra
feature: queue-hygiene
touches: docs/items
added: 2026-09-14
verify: test -z "$(grep -h '^verify:' docs/items/PL-3SQT-*.md docs/items/PL-7SVX-*.md docs/items/PL-L9RD-*.md | grep import_boundary_check)"
---

**Problem.** Four qt-port items carry a verify: command another port item satisfies, so each passes while still open once its neighbour lands and reddens the whole-store verify replay on main

**Measured 2026-09-15.** Four open `qt-port` items carry a `verify:`, and three
open with the same clause:

| item | command | today |
| --- | --- | --- |
| `PL-3SQT` | `import_boundary_check.py && ! grep -qE '"flet' pyproject.toml` | fails |
| `PL-7SVX` | `import_boundary_check.py && ! test -d spikes` | fails |
| `PL-L9RD` | `import_boundary_check.py && grep -q 'PySide6' app/theme.py` | fails |
| `PL-C92D` | `doc_check.py check && grep -qF ... docs/WORKING_NOTES.md` | fails |

**The shared clause is already a no-op.** `uv run python
tools/import_boundary_check.py` exits 0 on this tree - "12 declared, 38 modules
read, 0 errors" - so it proves nothing about any of the three, and each command
now rests entirely on its own second half. Those halves still fail correctly
today (`flet` is still in `pyproject.toml`, `spikes/` still exists,
`app/theme.py` names no `PySide6`), which is why nothing is red yet.

**The exposure is which item satisfies which half.** `PL-3SQT`'s half asks that
`flet` be gone from `pyproject.toml`, and `PL-7SVX` - "delete `spikes/` and the
last Flet import" - is as likely to be the item that removes it. `PL-L9RD`'s
half asks that `app/theme.py` name `PySide6`, which any item porting that module
satisfies. So the first of these to land flips a *neighbour's* command to
passing while that neighbour is still open, which is what `docket check
--verify` reports as an error on the whole-store replay `main` runs.

**Why it matters.** The replay's one job is to find work that merged without its
item being closed. A command an item does not itself satisfy makes that report
wrong in both directions at once: it accuses an item nobody has worked, and it
spends the signal that would have caught a genuine unclosed closure. It lands on
`main` rather than on a branch, where no session owns the red.

**Done when.** Each of the four names a command only its own work satisfies -
the no-op `import_boundary_check.py` clause dropped where it proves nothing -
and `bin/docket check --verify` reports no open item whose command already
passes.

**Re-pointed by `PL-6TP8`, 2026-09-19.** This is the contract's first
obligation on a command - it goes green only for what *this* item's work
creates - and the work is as briefed whichever way `PL-6TP8`'s shape half is
answered: each of the four names a clause only its own work satisfies, and the
no-op `import_boundary_check.py` clause goes.
