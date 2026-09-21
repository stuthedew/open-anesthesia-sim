---
id: PL-DL4M
title: docs/WORKING_NOTES.md still heads two resolved threads 'Open thread' and opens with a 'Repository state' section describing the v0.2.0 baseline, so a reader picking it up cold is told the rule-routing and scenario-branching questions are open and main is forty releases behind
priority: P3
effort: S
status: done
classes: docs
feature: dev-tooling
touches: docs/WORKING_NOTES.md
added: 2026-09-14
closed: 2026-09-21
pr: 858
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

## Closed 2026-09-21 - all three deleted, and where each outcome lives

**Deleted rather than re-headed**, which the "Done when" left open and which is
a session's call under `.claude/rules/instruction-writing.md` rule 14: the
blast radius is one document's phrasing. The deciding test is `PL-DG84`'s -
whether the outcome is recorded somewhere that maintains itself - and all
three passed it, so a `Settled:` re-head would have kept 299 lines of duplicate
whose only remaining job was to point at the copy that is maintained. Two of
the three are also *worse* than their successors rather than merely older,
which is what settles it:

- **`## Repository state as of this writing`.** `ROADMAP.md` § "Current
  baseline: v0.5.0" is the one maintained statement of the baseline;
  `docs/ARCHITECTURE.md` § "Tests (`tests/`)" carries the test map and is
  current where this still described the Flet-era fake `Page`/`Controller`
  pattern; the rendering-boundedness thread was superseded 2026-09-08
  (`PL-2FM6`). Both test functions it cited -
  `test_a_growing_run_does_not_grow_the_traffic_it_sends` and
  `test_chart_payload_is_bounded_however_long_the_run` - no longer exist, which
  is drift the brief had not catalogued.

- **`## Open thread: scenario branching, bookmarks, and what a snapshot is
  for`.** `ROADMAP.md` item 12's *Branch points* note records this section's
  own framing as superseded, and item 26 confirms the bookmark set against the
  Gas Man Owner's Manual where this recorded it as unverifiable ("the vendor
  documentation could not be checked from the capturing session"). `PL-PFM1`'s
  trap is item 26's *Required properties* and `tests/unit/test_bookmarks.py`,
  whose docstring holds the 1x-against-300x agreement `PL-CTD7` shipped;
  `PL-JW30`'s is `ROADMAP.md` § "The branch reproduces its parent, asserted
  element-wise" and `tests/reference/test_canonical_evaluation.py`; the
  snapshot-interval refusal is item 8; the step-cost measurements are the
  `PL-R460` docstrings in `core/uptake_system.py` and
  `core/matrix_exponential.py`; the per-sample memory projections died with the
  sample store (`PL-011` dropped, `PL-49R8`'s path-scoped rule).

- **`## Open thread: which moment a rule has to reach, not which tree it
  governs`.** `docs/resident-instructions.md` § "Fires when the approach is
  being decided" carries the outcome with its character cost and the refused
  alternative. The unmeasurable watch at its end is stated where it fires
  rather than where it is read about, in `.claude/rules/expert-review.md`'s
  opening scope block, which `PL-6SBB` (done) bought.

**The preamble gained two sentences**, because a deletion that leaves no
address invites the next session to rebuild the section: repository state is
`ROADMAP.md` § "Current baseline", not a thread here.

**Effect on `PL-DG84`'s advisory**, which was being built concurrently on
`claude/funny-knuth-7kwza8`: its narrow signal now fires on two sections rather
than four - § "Open: the repository has no README" (`PL-75R0`, still open and
still stale) and § "Open thread: what makes desflurane wash out too fast", the
permanent legitimate fire that rules out a hard failure. The decision is
unaffected; a test pinning the advisory against the live `docs/WORKING_NOTES.md`
rather than a fixture is not.
