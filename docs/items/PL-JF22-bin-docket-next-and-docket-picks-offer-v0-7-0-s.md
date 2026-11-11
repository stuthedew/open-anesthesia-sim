---
id: PL-JF22
title: bin/docket next and docket picks offer v0.7.0's Required-scope items while Gate 3's second group is still open, though ROADMAP.md § The cadence beat 3 clears the gate before implementation begins (the likely route by which PL-6590's slip happened)
status: untriaged
added: 2026-11-11
---

**Problem.** bin/docket next and docket picks offer v0.7.0's Required-scope items while Gate 3's second group is still open, though ROADMAP.md § The cadence beat 3 clears the gate before implementation begins (the likely route by which PL-6590's slip happened).

**Evidence, 2026-11-11.** `bin/docket next product` ranks `PL-RJN9` second.
`PL-RJN9` is v0.7.0 Required-scope entry 13, so it is milestone implementation,
and Gate 3 still has 36 entries open. `docket picks` prints a "Build, from the
milestone's Required scope" block during the clear beat. That block only
appends "the roadmap clears the gate first" (`render.py`, the `build_waits`
branch). `PL-KFTM`, a Required-scope item, was built and closed on 2026-11-01
while the gate was open. No record shows which command its session picked it
from, so the route is likely rather than shown.

**Why it matters.** `PL-6590` (does the debt gate have to clear before a
milestone's features are built?) recommends keeping the rule so it applies
again from Gate 4. While the tools offer Required-scope work by band during the
clear beat, `next` ranks a build item by its band among the gate's entries,
so a P1 build item comes ahead of every P2 and P3 gate entry. The rule will be
skipped again the same way.

**Done when.** Whichever answer `PL-6590` gets, the tools say the same thing as
`ROADMAP.md`. If the rule is kept, `next` stops offering a Required-scope item
while the beat is `clear`, or names it as off-gate work the rule holds back. If
the rule becomes "side by side", nothing here changes except the picks note.

**Depends on** `PL-6590`'s answer. Found while reviewing that item's
recommendation, 2026-11-11.
