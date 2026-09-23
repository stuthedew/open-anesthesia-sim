---
id: PL-8YXJ
title: A status or blocker change rewrites the front matter and leaves the brief's prose narrating the old state, and nothing reports it: the prose-dependency advisory skips closed prerequisites and nothing reads a brief's claims about its own status
priority: P2
effort: M
status: done
classes: defect, infra
feature: brief-state-agreement
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md, .claude/skills/docket/modes/triage.md, docs/worker.md, docs/items
added: 2026-09-22
closed: 2026-09-23
payoff: a brief can no longer tell a session its item waits on a decision or blocker the front matter says has cleared, and the next such passage is reported when the status moves
verify: grep -q 'def test_a_brief_naming_a_closed_prerequisite_is_advised' subprojects/docket/tests/test_checks.py && grep -q 'def test_a_brief_narrating_a_status_it_has_left_is_advised' subprojects/docket/tests/test_checks.py
root-cause-of: PL-X4RX, PL-7G5M, PL-9K7K
generator: live - every docket set --status or --blocked-by write leaves the brief's narration of the old state standing, and nine unreported instances turned up on 2026-09-22 alone
---

**Problem.** A status or blocker change rewrites the front matter and leaves the brief's prose narrating the old state, and nothing reports it: the prose-dependency advisory skips closed prerequisites and nothing reads a brief's claims about its own status

**Measured 2026-09-22, counting `PL-X4RX`'s class across the 341 open items.**
Queue state is stored twice. The front matter holds it, `docket set` writes it
and every command reads it; the brief narrates it - "Left at `needs-decision`",
"**Blocked on `PL-XJ5P`**", "Land it with `PL-D8KW`" - and nothing reads that
copy once the item it names has closed. A transition moves the first copy only,
and the convention that keeps answered decisions readable (leave the question
standing, write the dated answer underneath, `docs/worker.md`) keeps the second
standing on purpose, unmarked at the site. `subprojects/docket/README.md`
§ "The item format" states the opposite premise - keeping both in one file
"means the machine-readable state and the human-readable brief cannot drift
apart" - but `docket set --status ready` is a one-line diff that never shows
the paragraph 180 lines below it.

**The instances, all in open items, found in one pass:**

- **Own status.** `PL-SYG4` (`PL-X4RX`); `PL-Z34C`, "It is left
  `needs-decision`" under an undated heading while its status is `blocked`;
  `PL-Z3V5`, "deliberately left at `blocked`" while it is `ready`, appended on
  2026-09-19 inside a section headed 2026-09-13; `PL-LT77`, a dated triage note
  that reads as history.
- **Closed prerequisites.** `checks._prerequisite_matches` run over open items
  without its open-only filter fires 7 times in 6 items, 5 real: `PL-B396` and
  `PL-KZ99` on `PL-S6WW`, `PL-WZVZ` on `PL-4DCG`, and `PL-MBP6` on `PL-YCWZ`
  and `PL-Z3V5` on `PL-XJ5P` (those two answered further down, unmarked where
  the claim stands). Both false positives are the `requires` cue narrating
  history (`PL-HJPY` on `PL-C842`, `PL-KZ99` on `PL-ZF2G`); without that cue
  it is 5 of 5.
- **Sequencing on a closed item, outside the cue list.** `PL-M3X6`, "Land it
  with `PL-D8KW`" (done); `PL-8JY7`, "Cheapest to land alongside `PL-68XK`"
  (dropped).
- **The compound form the continuation pattern misses.** `PL-B396`'s
  "**Blocked by `PL-S6WW` and `PL-KZ99`.**": `PROSE_DEPENDENCY_CONTINUATION`
  needs "and on" or "and by", so the open `PL-KZ99` is unreported - and
  `PL-KZ99`'s own `blocked-by` names `PL-B396`, so prose and field disagree
  about which way the edge runs.

Checked and clean: the reverse drift, a `needs-decision` item whose decision is
answered in its brief but whose status never moved - 14 candidates by text,
none real.

**Why it matters.** A session reads the brief to decide whether it may start,
and the cheap reading stops at the first status claim it meets.
`_check_prose_dependencies` was scoped to open prerequisites on the prediction
that closed-item mentions are "history rather than a defect" and would make the
advisory "unreadable inside a week". Counted with its own matcher, the closed
direction fires 7 times across the whole store. The prediction is why the half
that is live today was never built. `PL-X4RX`'s triage declined a check on a
count of one, from a search for the literal "Left at `needs-decision`"; the
same claim in other words is in `PL-Z34C` and `PL-Z3V5`, and `PL-7G5M` (closed
2026-09-15) was the identical failure a week earlier.

**Done when.**

1. `docket check` advises on an open item whose brief (a) names a closed item
   as a prerequisite - the existing cues less `requires`, plus "land(s) with",
   "alongside" and "sequenced after"; (b) names its own status in a
   self-referential phrase ("left at", "left", "kept at", "stays at", "held
   at") other than its current one; (c) states a second blocker as "blocked by
   A and B". A passage carrying an explicit superseded marker is skipped, so
   the advisory reaches zero without deleting history. The marker is one
   greppable token, spelled by the implementing session.
2. `docket set`, when it moves `status` or `blocked-by`, prints the passages
   the same matcher finds, so the session holding the context repairs them in
   the same commit.
3. The instances above are marked or reworded, and the advisory reports zero
   on the store.
4. The marker convention is written where the writing session reads it -
   `.claude/skills/docket/modes/triage.md` (with `PL-RWJD`, same file) and the
   decision-section paragraph of `docs/worker.md` - and the README's "cannot
   drift apart" sentence says what co-location actually buys: both copies in
   one diff, not agreement between them.

**Considered and not recommended now: a rewritable "Where it stands" block**
at the top of every brief, dated, which `check` would hold to be no older than
the brief's newest dated heading - the issue-body-plus-timeline shape. It also
cures the wider "which of twelve updates is current" problem (`PL-SYG4`'s last
paragraph warns that every measured number in it is spent), but it is a format
change across 341 open briefs and a rewrite on every update. What would reopen
it: brief-versus-tree staleness - the `PL-HH52`, `PL-3M3K`, `PL-5F26` and
`PL-T7PY` shape, which no matcher reaches - still arriving at more than about
one item a week after this lands.

**Worked 2026-09-23.** Built as the Done-when lists, with four departures a
measurement over the store decided, each recorded beside its pattern in
`checks.py`:

- **Bare `alongside` is not a cue; `land(s) alongside` is.** Bare, it fired on
  `PL-28HG`'s "filed rather than fixed alongside `PL-MM7F`", correct prose that
  no marker should have to be written over. `landed with` is left out as past
  tense (three hits, all history); `sequenced behind` joins `sequenced after`.
- **The own-status phrases are wider than listed** - `stays`, `remains` and
  `parked at` beside the five named - since `PL-Y4YX` and `PL-162Y` use them
  today and would be missed the day their status moves. A phrase counts as the
  item's own only when no other item is named earlier in its sentence
  (`PL-X4RX`'s title is about `PL-SYG4`). `ready`, `blocked`, `done` and
  `dropped` count only in backticks; `untriaged` and `needs-decision` bare too,
  which is what found `PL-X5PK`, an instance the 2026-09-22 pass missed.
- **Quotations are not read**, in any direction: this brief and `PL-X4RX`
  quote the passages they are about.
- **The marker is `[superseded YYYY-MM-DD: ...]`**, dated for when the passage
  stopped holding, covering its paragraph or its own list item.

Fourteen passages in twelve items were marked or reworded, and the advisory
reports zero. A cue ending one line with its id on the next stays unread:
letting the window cross a line break added four passages, two of them wrong.
