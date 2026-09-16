---
id: PL-DL4M
title: docs/WORKING_NOTES.md still heads two resolved threads 'Open thread' and opens with a 'Repository state' section describing the v0.2.0 baseline, so a reader picking it up cold is told the rule-routing and scenario-branching questions are open and main is forty releases behind
priority: P3
effort: S
status: ready
classes: docs
feature: dev-tooling
touches: docs/WORKING_NOTES.md
added: 2026-09-14
verify: python3 tools/doc_check.py check && ! grep -qF 'Open thread: which moment a rule has to reach' docs/WORKING_NOTES.md
---

**Problem.** docs/WORKING_NOTES.md still heads two resolved threads 'Open thread' and opens with a 'Repository state' section describing the v0.2.0 baseline, so a reader picking it up cold is told the rule-routing and scenario-branching questions are open and main is forty releases behind

**Notes.** Found 2026-09-14 by a session reading the plan cold, which is the
reader the file's headings are for. Three headers state a status their own
items no longer hold:

- `## Open thread: which moment a rule has to reach, not which tree it governs
  - PL-WWDT, PL-H588` (line 995). `PL-WWDT` is `done` and `PL-H588` is
  `dropped`; what remains is the unmeasurable watch-item at the section's end.
- `## Open thread: scenario branching, bookmarks, and what a snapshot is for -
  PL-DHV7, ROADMAP items 8, 11, 12 and 26` (line 463). Its own closing
  condition, "the thread stays open until item 26 is scoped" (line 473), was
  met on 2026-09-06 when v0.5.0 promoted item 26; `ROADMAP.md`'s v0.5.0
  section now carries the design.
- `## Repository state as of this writing` (line 63) describes `main` as "the
  v0.2.0 baseline" with a basic agent picker added after it. The baseline is
  v0.4.25; nothing in the section is current.

`PL-DG84` is the systemic item - the file's own header asks for resolved
threads to be deleted and nothing reads that policy - and lists five earlier
instances (`PL-5748`, `PL-60CQ`, `PL-BHJW`, `PL-C92D`, `PL-75R0`). This is
three more, filed the same way so the count that decides `PL-DG84` is
complete. The playback-speed heading (line 343, `PL-009`, dropped 2026-08-25
and shipped as planned-milestone item 25 in v0.4.0) is the same shape and is
already `PL-5748`'s section.

**Done when.** Each of the three sections is deleted, or re-headed with the
status word the file already uses for settled threads (`Settled:`,
`Decided:`), with its outcome pointed at where it now lives; and the
`Repository state` section either states the current baseline or is removed
in favour of `ROADMAP.md` § "Current baseline", which is the one place that
statement is maintained.

**Why it matters.** `docs/WORKING_NOTES.md` is what a session reads to pick up
an open thread cold, and `docket.toml` wires it in as this repository's
`notes_file`, so `bin/docket show` surfaces its `##` headings against the item
being shown. All three stale headings mislead in the same direction: they
present a settled question as live.

A session reading the rule-routing heading is told `PL-WWDT` and `PL-H588` are
open, when one is `done` and the other `dropped`. One reading the
scenario-branching heading is told the thread stays open until item 26 is
scoped, which happened on 2026-09-06 - `ROADMAP.md`'s v0.5.0 section now
carries the design. One reading `Repository state as of this writing` is told
`main` is the v0.2.0 baseline when it is v0.4.25, forty releases on. The cost
is a session spending its opening turns re-deriving a decision already recorded
somewhere else, which is the expensive half of a cold start.
