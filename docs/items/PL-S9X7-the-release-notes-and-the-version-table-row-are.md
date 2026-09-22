---
id: PL-S9X7
title: The release notes and the version-table row are written from the same 21 items but by different hands, so nothing checks that the row's item count matches the notes' line count
priority: P3
effort: S
status: ready
classes: infra
feature: release-process
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-13
verify: grep -q 'def check_release_row_item_count' tools/doc_check.py && uv run pytest tests/unit/test_doc_check.py
---

**Problem.** The release notes and the version-table row are written from the same 21 items but by different hands, so nothing checks that the row's item count matches the notes' line count

**Measured 2026-09-14: the gap is real and the numbers currently agree.** Five
version-table rows carry a parseable `| N items |` count and have a notes file;
none of the five mismatches its notes' bullet count. And nothing checks it -
`tools/doc_check.py` has twenty `check_` functions and none reads that column
against `docs/releases/`. So the agreement is maintained by hand and confirmed
by nobody.

**Why it matters.** `PL-GLBF` already established the pattern and the reason:
`ROADMAP.md`'s subset counts were hand-maintained and unchecked, and the one a
field can decide now is checked. This is the same shape on the release train,
where the cost of being wrong is a permanent record - the version table is the
first thing a reader consults for what a release contained, and a count that
disagrees with the notes gives two answers with nothing to say which is right.
`CLAUDE.md`'s test for building a check is whether the work recurs and the
answer is deterministic: it recurs every release, and both numbers are countable
from files in the tree.

**Why P3.** Nothing is wrong today, and the check is cheap; this is worth doing
when somebody is next in `tools/doc_check.py` rather than on its own.

**Done when.** `tools/doc_check.py` fails when a version-table row's item count
disagrees with the number of item bullets in that version's notes file, rows
with no count or no notes file are skipped rather than reported, and
`tests/unit/test_doc_check.py` covers a mismatch.
