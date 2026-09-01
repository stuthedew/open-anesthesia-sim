---
id: PL-H8MQ
title: ROADMAP.md states the v0.2.8 entry count in four places and nothing holds them to the list
priority: P3
effort: S
status: ready
classes: defect, docs
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py, ROADMAP.md
added: 2026-08-31
verify: uv run pytest tests/unit/test_doc_check.py -k "gate and count"
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
numbers by hand, which is the tax this item describes, paid again.
