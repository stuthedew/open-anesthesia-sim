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
