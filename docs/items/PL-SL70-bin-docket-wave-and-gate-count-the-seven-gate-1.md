---
id: PL-SL70
title: bin/docket wave and gate count the seven Gate 1 entries sequenced behind v0.5.1 as open debt, so every session opens on a beat asking for a target the plan forbids
status: untriaged
added: 2026-09-13
---

**Problem.** bin/docket wave and gate count the seven Gate 1 entries sequenced behind v0.5.1 as open debt, so every session opens on a beat asking for a target the plan forbids

Measured 2026-09-13 against `origin/main` at `5cbcea3`. `bin/docket wave`
reports Gate 1 as "97 cleared, 62 open" and prints the beat `clear the gate -
62 entries of 159 still open`; `bin/docket gate` lists the same entries under
`Open debt`. Seven of the 62 cannot reach `done` or `dropped` before v0.5.0
begins, because they are sequenced behind v0.5.1 — a release the timeline puts
*after* v0.5.0:

- `PL-3355`, `PL-TG60` — `blocked-by: PL-25KS` (port the dashboard to PySide6)
- `PL-Q4VH`, `PL-THXF` — `blocked-by: PL-G59B` (port the chart to pyqtgraph)
- `PL-W8DQ` — `blocked-by: PL-L9RD` (re-express `theme.py` for Qt)
- `PL-GS3R` — `blocked-by: v0.5.1` directly; `P1`, `safety`
- `PL-NGF7` — the one deferral Gate 1's own section records

Two more, `PL-8PS6` and `PL-WZVZ`, are blocked behind `PL-FG9D` (the base
anesthesia-machine abstraction), which `ROADMAP.md` places nowhere. Those are
clearable in principle — the chain is `PL-4DCG` → `PL-FG9D` → the two — but
only by pulling an unscoped design round into the gate.

**Why it matters.** `wave`'s beat is what the session-start digest prints, so
this is the first line every session reads, and it asks for something the plan
forbids. A session that takes it literally either works an item whose own file
says not to, or spends a pass discovering the sequencing by opening nine files.

**It is the half of `PL-D143` that did not land.** `PL-D143` (closed
2026-09-13, `#512`) named this contradiction for five of the seven and chose
its option 1 — `status: blocked` — on the stated ground that it "stops `next`
offering them and stops `gate` counting them as resolvable debt". The first
half is true. The second is not: `bin/docket gate` and `bin/docket wave` both
count a `blocked` item as open gate debt, so the count the beat is computed
from is unchanged. `PL-D143`'s `verify:` command tested only that the five
files carry a `blocked-by`, which is why the gap survived its close.

**Where.** `subprojects/docket/src/docket/` — whatever computes the gate split
`wave` prints and the `Open debt` list `gate` prints.

**Decision needed.** Whether the count excludes them or merely marks them. Two
shapes, and the second is the recommendation:

1. **Exclude** an entry whose `blocked-by` resolves to a version later than the
   milestone the gate guards. Cleanest count, but it silently shrinks a frozen
   list, which is the thing `ROADMAP.md` § "Recording it" exists to prevent.
2. **Report the split** — `62 open, 53 clearable, 9 sequenced past this
   milestone` — and compute the beat from the clearable figure. The frozen list
   stays whole and visible, and the beat becomes reachable. `PL-9S30` is the
   documentation half of the same finding.
