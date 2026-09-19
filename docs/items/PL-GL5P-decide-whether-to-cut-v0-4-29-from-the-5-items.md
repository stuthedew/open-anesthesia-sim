---
id: PL-GL5P
title: Decide whether to cut v0.4.29 from the 5 items finished since v0.4.28, or hold for the gate's last 4 entries
status: untriaged
added: 2026-09-19
---

**Problem.** Decide whether to cut v0.4.29 from the 5 items finished since v0.4.28, or hold for the gate's last 4 entries

**Why it matters.** `bin/docket release --dry-run` on `origin/main` at
2026-09-19 15:00 UTC reports 5 finished items since v0.4.28, and the command
refuses nothing: the previous release is tagged and no unmerged ref is carrying
a cut. So the release is available to take; what is open is whether it should
be.

The five are `PL-1YT5` (record the auto-pull-request clause as ratified),
`PL-G6J5` (retire the slow-command advisory), `PL-T2LH` (the v0.4.28 cut
itself), `PL-V1F4` (repair `PL-ZG5J`'s stale route) and `PL-ZG5J` (the
frame-cost harness under `tests/benchmarks/`). **All five are apparatus.**
Nothing in `src/`, nothing in `docs/MODEL.md`, nothing a reader of the
simulator would see.

**Recommendation: hold.** `bin/docket wave` puts the project at step 5 of 14
with the beat "clear the gate - 4 entries of 175 still open here", and two of
those four (`PL-H4N8`, `PL-QBX0`) were in flight on
`origin/claude/eloquent-bell-s9bi5y` when this was filed. A patch cut now
spends a version number on workflow-only work hours after v0.4.28; the same
number cut after those land carries the gate progress as well, which is what
`ROADMAP.md`'s version table is for - "the capability boundary a release
crosses". Against that: v0.4.28 was itself cut today, so the cadence here is
fast and a thin patch is not out of character, and holding leaves five closed
items unstamped for however long the gate takes.

**This is the owner's call rather than a session's**, because which capability
boundary a version marks is direction. It is filed rather than left in a reply
because the session that first raised it has been archived, which deletes its
`needs_action` line silently (`PL-H1JD`, and rule 14 of
`.claude/rules/instruction-writing.md`).

**First step.** Answer cut-or-hold. If cut: `make release VERSION=0.4.29`, then
the `ROADMAP.md` edits it names, then `make check`, then the tag.

**Done when.** Either v0.4.29 is cut and tagged, or this records the decision
to hold and what it is waiting for.

**The recommendation above is withdrawn; cut it. Re-measured 2026-09-19 after
ten more merges** (`PL-2P9L`, `PL-FZ58`, `PL-09G9`, `PL-VHVJ`, `PL-H4N8`,
`PL-QBX0`, `PL-LBR6`, `PL-QMC0`, `PL-5QLP`, `PL-JF5Z`), both of the grounds
this item was filed on have gone:

- **It is no longer apparatus-only.** `bin/docket release --dry-run` now
  reports **15** finished items since v0.4.28, and two of them are the
  simulator's: `PL-H4N8` (ROADMAP item 28's agent cost basis - the
  science-classed one, where "exhausted" understated delivered agent) and
  `PL-QBX0` (ROADMAP item 24's preferences gate, which did not cover the ISO
  5360 identification colours). Both are Gate 1 entries. "Nothing a reader of
  the simulator would see" was true of five items and is false of fifteen.
- **The gate is nearly clear.** `bin/docket wave` reads 170 of 175 cleared,
  **2** open here (`PL-JVHL`, `PL-7DMJ`) and 3 blocked outside it, against the
  4-open reading this item was filed on. So "hold for the gate's last four" is
  holding for two, one of which nobody is on.

Cutting mid-gate is this project's own practice rather than an exception:
`PL-T2LH` cut v0.4.28 "carrying one Gate 1 entry". The title of this item
still says five, which is what it was filed on; the number to read is fifteen.

**Recommendation: cut v0.4.29.** `make release VERSION=0.4.29`, then the
`ROADMAP.md` edits it names, then `make check`, then the tag.
