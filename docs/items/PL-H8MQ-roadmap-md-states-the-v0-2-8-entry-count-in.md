---
id: PL-H8MQ
title: ROADMAP.md states the v0.2.8 entry count in four places and nothing holds them to the list
priority: P3
effort: S
status: done
classes: defect, docs
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-08-31
verify: uv run pytest tests/unit/test_doc_check.py -k "gate and count"
milestone: v0.2.8
closed: 2026-09-01
---

**Problem.** The number of entries on v0.2.8's frozen list is written in prose
in four places — the version table row, the "Rows 1 and 2" paragraph, the
frozen-list intro, and the out-of-scope list — plus once more as a per-group
count on each of the list's two headings. Nothing reads the list and checks
them. On 2026-08-31 three of them said "nineteen" and one said "twenty-two",
having gone stale when five entries were admitted after the freeze; admitting
seven more made every one of them wrong at once, and they were corrected by
hand in the same change.

**Why it matters.** `ROADMAP.md` already states the principle — "a count
written into a document goes stale the next time an item closes" — and applies
it to the *closed* count, which is deliberately not recorded and read from
`bin/docket wave` instead. The *total* was left in prose in five places, so
the rule is stated and then broken a few paragraphs below itself. A reader
deciding whether the release is nearly done reads a number that no longer
matches the list above it.

**Where.** `ROADMAP.md`; `tools/doc_check.py`, which already decides the
package-map, provenance-table, dangling-citation and release-train questions
and is where a fifth would go. `bin/docket wave` already parses the entry ids
out of the gate subsection, so the list length is available.

**Approach.** This is the decidable half of a documentation question, so it
belongs in a script rather than in a session's judgment: count the `- PL-XXXX`
entries under the gate subsection, count them per group heading, and hold
every spelled-out number that claims to be that count to it. The judgment half
— whether the prose around the number is still true — stays with the reader.
Spelled-out numerals ("twenty-nine") rather than digits are what the file
uses, so the check needs a small words-to-int map or the file needs to stop
spelling them out.

**Done when.** A count in `ROADMAP.md` that disagrees with the frozen list
fails `make check`, and the failure names both numbers.

**Re-measured 2026-09-01, and admitted to v0.2.8's frozen list under the scope
test.** The count is stated in six places, not four - the version table row,
the timeline table row, the "Rows 1 and 2" paragraph, the frozen-list intro,
the `not-delegable` paragraph and the out-of-scope bullet - with three further
counts beside them: the two group headings and the debt/capability split. On
that date three different totals were live at once: the timeline row said
eighteen, four paragraphs said thirty-one, and the frozen-list intro said
thirty-two. Admitting four entries the same day required correcting all nine
numbers by hand; admitting a fifth an hour later required correcting eight of
them again. That is the tax this item describes, paid twice in one day.

**Done 2026-09-01.** Both halves of the approach, because neither is enough
alone. `check_gate_counts` in `tools/doc_check.py` holds every count a frozen
list states about itself to the entries in it — each group heading against what
follows it, the group counts against the list's length, the stated item-id
count against the ids the entries hold, and the version- and timeline-table
rows naming that release. The failure names both numbers, as the item asked:
`ROADMAP.md:541: this group heading of v0.2.8's frozen list says 21 entries,
but 22 follow it`. Watched it fail on three separately perturbed counts before
it was written into the item.

The prose half is the reason the check can be trusted. A checker cannot tell
"the thirty-seven entries below are its whole content", a claim about today's
list, from "frozen ... at seventeen entries", a dated fact that must never
change — and guessing at that is the judgment half `CLAUDE.md` says not to
script. So the counts are read only where their meaning is fixed by where they
sit (a group heading over the entries it counts; a table row naming that
release), and the six prose restatements were removed instead: the "Rows 1 and
2" paragraph, the freeze paragraph's running tallies, the debt/capability
split, the `not-delegable` sentence, the out-of-scope bullet, and the v0.3.0
timeline row. `ROADMAP.md` now says beside the closed-count rule where a size
may be stated. Five checked sites remain, down from nine hand-maintained
numbers.

**One stale count found and corrected.** The v0.3.0 section said its contents
were "the fourteen listed under 'Debt gate: the frozen list' in the v0.4.0
section" — fourteen was the freeze-day figure, and six entries had been added
since, so the list has held twenty since 2026-08-30. A reader would have taken
the foundation release to be six items smaller than it is. It is outside every
site the check reads (prose, in a section that records no gate of its own), so
it was de-numbered rather than corrected in place: the entries are the record.

**Not covered, captured as `PL-GLBF`.** Counts of a *subset* of a list — seven
entries `not-delegable`, three reaching into `src/` — state a property of the
entries rather than the list's size and are still hand-maintained. The
`not-delegable` one is decidable from the item files; the other two are not,
and the item asks for that decision before any code.
