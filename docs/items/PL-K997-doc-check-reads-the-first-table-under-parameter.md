---
id: PL-K997
title: doc_check reads the first table under '## Parameter provenance' as the provenance table, so any table added above it is silently read in its place
status: dropped
added: 2026-09-07
closed: 2026-09-12
reason: Duplicate of PL-ZBZZ (doc_check reads the first table under 'Parameter provenance' as the provenance table). Same defect three days apart; PL-ZBZZ carries three ranked candidate fixes and the blast-radius note that table_rows is shared with the roadmap parsers. This item's own instance - PL-1JDD, 29 errors, 2026-09-07 - has been appended to PL-ZBZZ so nothing is lost.
---

**Problem.** doc_check reads the first table under '## Parameter provenance' as the provenance table, so any table added above it is silently read in its place

`docket.roadmap.table_rows(text, "Parameter provenance")` yields the rows of
the *first* markdown table under that heading and stops at the next heading of
the same depth or above. `check_provenance` calls it, so the provenance table
is identified by position rather than by anything in the table itself.

**How it was found.** `PL-1JDD` added a three-row field table to
§ "Source hierarchy", which is a `###` inside `## Parameter provenance` and
therefore above the provenance table. `make check` then reported 29 errors of
the form "no provenance row for data/... = 6" - one per stored constant - and
nothing naming the cause. The fix was to write the fields as a bullet list
instead, which is a workaround rather than a repair: the next session to want
a table in that section will spend the same time on the same 29 errors.

**Why it is not merely cosmetic.** The failure is loud, so nothing is silently
wrong today - but the reported errors describe a documentation gap that does
not exist, and the obvious response to them is to start adding rows to the
wrong table. The check is upstream of every constant a clinician can read.

**Options, cheapest first.** Anchor the table by its header cells rather than
by position - it is the only table in the document whose header reads
`| Parameter | Selected value | Unit | Source (data file - key path) |` - or
have `check_provenance` skip tables whose header does not match and report
"no table with the provenance header found under 'Parameter provenance'" when
none does, which the existing no-rows branch already has the shape for.
`subprojects/docket/src/docket/roadmap.py` is shared with `ROADMAP.md`'s
release-train and version tables, so the header test belongs at the call site
in `tools/doc_check.py` rather than in `table_rows`.

**Found.** `PL-1JDD`, 2026-09-07, while recording the schema-2 fields in
`docs/MODEL.md`.
