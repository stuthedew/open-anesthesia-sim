---
id: PL-880Z
title: Five ref-lifecycle briefs carry citations that have moved, and PL-XLQ5's title names a mechanism _landing_split cannot have - which ROADMAP.md repeats verbatim as a frozen gate entry
priority: P2
effort: S
status: ready
classes: defect, docs
feature: parallel-sessions
touches: docs/items, ROADMAP.md
added: 2026-09-12
verify: python3 tools/doc_check.py check && ! grep -qF 'superseded intermediate blob' ROADMAP.md
---

**Problem.** Five ref-lifecycle briefs carry citations that have moved, and PL-XLQ5's title names a mechanism _landing_split cannot have - which ROADMAP.md:1576 repeats verbatim as a frozen gate entry

**Confirmed at triage, 2026-09-12.** The frozen-gate half is exact:
`ROADMAP.md:1576`, under "Cleared before v0.5.0 begins, the workflow lane - 50
entries", reads

```text
- PL-XLQ5 (M) The orphaned report counts a branch's superseded intermediate blob
  as work the squash left behind
```

which is `PL-XLQ5`'s title copied verbatim, so the mechanism the title names
wrongly is now asserted in two documents and the gate entry is the one a reader
meets while deciding whether v0.5.0 can begin.

**Why it matters.** A citation that has moved costs a search. A *mechanism* named
wrongly costs the diagnosis: a session that starts `PL-XLQ5` from either
document goes looking in `_landing_split` for behavior it does not have, and the
gate entry gives that wrong description the standing of a frozen decision. The
same failure the ref-lifecycle cluster keeps producing - `PL-38PN`, `PL-JXVD`,
`PL-TTMF`, `PL-8T3Z` are all the same shape - is here one level up, in the
document that decides when a milestone opens.

**Sequencing, and it is not optional.** `PL-XLQ5` is in flight on
`origin/claude/ready-vcs-batch-closure-xrvfya` as of 2026-09-12. Its file is
being edited by that session, so correcting the title has to wait for that
branch to land or be abandoned; the `ROADMAP.md` half is independent and can go
first. Check `bin/docket show PL-XLQ5` before touching the item file.

**Done when.** The five ref-lifecycle briefs cite lines that resolve at the time
of writing; `PL-XLQ5`'s title names a mechanism `_landing_split` actually has;
and `ROADMAP.md`'s gate entry says the same thing the corrected title does,
rather than preserving the old sentence as a frozen record of a wrong diagnosis.
