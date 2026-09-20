---
id: PL-880Z
title: Five ref-lifecycle briefs carry citations that have moved, and PL-XLQ5's title names a mechanism _landing_split cannot have - which ROADMAP.md repeats verbatim as a frozen gate entry
priority: P2
effort: S
status: done
classes: defect, docs
feature: gate-list-integrity
touches: docs/items, ROADMAP.md
added: 2026-09-12
closed: 2026-09-20
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

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation): still real, with stale numbers corrected here rather than in the text above.** `ROADMAP.md` still repeats
`PL-XLQ5`'s title verbatim as a frozen gate entry, and the brief's own citation
of it has gone stale the same way it describes: the line is `ROADMAP.md:2229`,
not `:1576`. Two of the named briefs are still wrong and still open -
`PL-38PN:37` ("around line 943") and `PL-JXVD:16` ("`:1149`") both point past
the end of a 580-line `simulation_view.py`, and `_run_simulation_timer` does
not exist. The sequencing note has lapsed in this item's favour: `PL-XLQ5`
closed 2026-09-12 (#504), so correcting the title no longer has to wait.
`PL-TTMF` is now `dropped`.

## Closed 2026-09-20: the title half done, the briefs half already owned elsewhere

**The title half, which is what the `verify:` measures.** Confirmed against the
tree rather than taken from the brief: `_landing_split` diffs the fork point
against the ref's tip, so it cannot see a blob superseded by a later commit on
the same branch, and `git log -S` puts that shape in `#121` (`PL-CPSY`) - three
weeks before `PL-XLQ5` was filed. So the title was impossible when written,
not merely overtaken. `PL-XLQ5` is retitled to name the mechanism the code has
(the `base_blobs` membership test: no commit on the base ever carried that
exact blob), which is the one `_superseded`'s own docstring cites this item's
id for, and `ROADMAP.md`'s frozen entry now says the same. The item file is
renamed to match its new slug, per the drift advisory; `PL-KBFN`'s `verify:`
names the old path and is a closed record, so nothing replays it.

**This brief's own citation had drifted again**, exactly as it describes: the
gate entry was `:1576` at triage, `:2229` at the 2026-09-19 sweep, and `:2293`
when this was worked. It is deliberately not restated here - a line number in
a file this size is stale on the next edit, and `grep -n 'PL-XLQ5' ROADMAP.md`
is what answers it.

**The five-briefs half is not work this item can do, and dropping it silently
would lose why.** Checked one by one on 2026-09-20:

- `PL-38PN` (open) still carries `_run_simulation_timer`, "around line 943" and
  `:1149` against a 580-line `app/simulation_view.py`. Those are **`PL-JXVD`'s**
  deliverable, not this one's: that item exists for exactly them and its
  `verify:` greps `PL-38PN`'s file for `:1149`. Fixing them here would satisfy
  another open item's command from outside it.
- `PL-TTMF` is `dropped` (2026-09-19).
- `PL-8T3Z` carries no line citation at all now; what remains of it is a
  `touches` omission and a `Where` pointing at a dropped item, which is that
  item's own open work.
- `PL-XLQ5` carries none, and is handled above.

So the count in the title was true when written and names no work left here.
`PL-JXVD` is the live half and is open on the gate list.

