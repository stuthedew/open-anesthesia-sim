---
id: PL-HXF0
title: doc_check reads an absent: marker in an item brief with _marked_span, so a marker under a list covers only the list's last item, while _marked_scope, which the provenance and derived markers use, reaches back over the whole list
priority: P2
effort: S
status: ready
classes: defect
feature: one-source-of-truth
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-11-03
payoff: a brief that names a deleted file in an earlier list item can be marked so the documentation check accepts it
verify: grep -q 'def test_an_absent_marker_under_a_list_covers_its_first_item' tests/unit/test_doc_check.py
---

**Problem.** doc_check reads an absent: marker in an item brief with _marked_span, so a marker under a list covers only the list's last item, while _marked_scope, which the provenance and derived markers use, reaches back over the whole list

**Found 2026-11-03, building `PL-1ZZ0`.** In `tools/doc_check.py`,
`_absent_paths` scopes each `absent:` marker in an item brief with
`_marked_span`, which returns only the block directly above the marker. Under a
list, that block is the last list item. `_marked_scope` reaches back over the
whole list, and its docstring says a marker under a list is the only way to
tie an earlier item, because a marker cannot stand inside a list item. The
`provenance:` and `derived:` readers use `_marked_scope`. In
`PL-SG93`'s brief, a marker under a two-item list did not cover the first item,
so the check reported both a missing marker and a marker with nothing to mark.

**Why it matters.** Two readers of one fact, what a marker covers, give two
answers. A brief that names a deleted file in an earlier list item has no
marker placement that the check accepts.

**Done when.** `_absent_paths` reads the marker's scope from `_marked_scope`,
and a test puts a deleted path in the first of two list items with the marker
under the list and finds no error.

**Generator check.** One-off. The fact misread is what a marker under a list covers, and `_marked_scope` already states it; `_absent_paths` is the one reader of the three that reads it another way. No head's `misread:` states it (checked with `bin/docket generators --misread`, 2026-11-04).

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem was present in part when Gate 3 froze at `817a4d88`, so the item joins v0.7.0's frozen list. At `817a4d88`, `_absent_paths` already used `_marked_span` (`3aaeb0b2`, 2026-09-26). The disagreement with `_marked_scope` is newer: that function arrived in `5ec0ee9b` (2026-10-25 06:17).
