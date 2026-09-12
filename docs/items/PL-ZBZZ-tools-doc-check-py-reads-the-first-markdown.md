---
id: PL-ZBZZ
title: tools/doc_check.py reads the first markdown table under 'Parameter provenance' as the provenance table, so a table added anywhere in that 500-line section reports 11 missing-row errors that all name the wrong cause
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-10
closed: 2026-09-12
pr: 496
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def test_a_decoy_table_above_the_provenance_table_is_named_as_the_cause' tests/unit/test_doc_check.py
---

**Problem.** tools/doc_check.py reads the first markdown table under 'Parameter provenance' as the provenance table, so a table added anywhere in that 500-line section reports 11 missing-row errors that all name the wrong cause

**Measured 2026-09-10 while working `PL-8SDL`.** A four-row markdown table of
literature citations was added to `docs/MODEL.md`'s "Parameter provenance"
section at about line 1435. The real provenance table starts at line 1723.
`make doc-check` then failed with eleven errors of the form:

> `docs/MODEL.md`: no provenance row for `data/patients/reference_adult.json`
> `weight_kg` = 70; every constant a clinician could read belongs in the table

Every one of them is true of the table the checker read and false of the
document. Nothing said a second table existed, and the suggested remedy - add
rows - would have made things worse by putting parameter rows into a citation
list. The fix was to render the citations as bullets instead.

**Why it happens.** `table_rows` in
`subprojects/docket/src/docket/roadmap.py` yields "the rows of the **first**
markdown table under `heading`", stopping at the next heading of the same depth
or above. `check_provenance` calls it with `"Parameter provenance"`. That
section is over 500 lines of prose in this document, all under one `##`
heading, so *any* table anywhere in it displaces the provenance table.

**Why it is worth fixing rather than tolerating.** The check works - it failed
loudly and CI would have caught it. What it gets wrong is the *cause*, and it
gets it wrong in the direction that costs most: a session that trusts the
message edits the provenance table, which is a safety-critical record of where
every displayed constant comes from. `CLAUDE.md`'s standard for an advisory is
that it changes a decision correctly; this one points at the wrong file region
with complete confidence.

**Candidate fixes, cheapest first.**

1. **Say what was read.** When the first table under the heading has a header
   row that does not match the expected four columns, report *that* - "the
   first table under 'Parameter provenance' has 3 columns and does not look
   like the provenance table; is there a second one?" - instead of walking the
   parameters. One conditional, and it converts eleven misleading errors into
   one accurate one.
2. **Anchor the table rather than the section.** Give the provenance table an
   HTML-comment marker in `docs/MODEL.md` and have `check_provenance` find it
   by that, so prose above it is free to contain tables. This is the robust
   answer and costs a marker in the document.
3. **Match on the header row.** Scan the section's tables and take the one
   whose header is `| Parameter | Selected value | Unit | Source ... |`. No
   document change, but it couples the checker to the header wording.

Option 1 is the one to take if only one is taken: it is a few lines, it needs
no document change, and it removes the misleading half without changing what
the check enforces.

**Note the blast radius.** `table_rows` is shared with the roadmap parsers -
`parse_version_table`, `parse_timeline` and `parse_milestones` all use it - so
fix this in `check_provenance` or in `docs/MODEL.md`, not by changing
`table_rows` itself.

## The same defect, three days earlier (`PL-K997`, 2026-09-07)

`PL-K997` recorded this independently while `PL-1JDD` was writing the schema-2
fields into `docs/MODEL.md`. A three-row field table was added to
§ "Source hierarchy" - a `###` inside `## Parameter provenance`, and therefore
above the provenance table - and `make check` reported **29** errors of the form
"no provenance row for `data/...` = 6", one per stored constant, with nothing
naming the cause. The fix taken there was the same workaround taken on
2026-09-10: write the fields as a bullet list instead.

Two independent captures three days apart, each costing a session the same
diagnosis and each resolved by not writing a table, is the evidence that this is
a recurring tax rather than a one-off. `PL-K997` is dropped in favour of this
item, which carries the ranked options.

`PL-K997` adds one option to the three below: anchor on the header cells, since
the provenance table is the only table in the document whose header reads
`| Parameter | Selected value | Unit | Source (data file - key path) |`.

**Why it matters.** The check is upstream of every constant a clinician can
read, and when it misfires it points a session at the wrong file region with
complete confidence. The remedy its message suggests - add rows - would put
parameter rows into whatever table displaced the real one, which is an edit to
the safety-critical record of where each displayed value comes from. Two
sessions have now met it (`PL-1JDD`, `PL-ZBZZ`) and both resolved it by not
writing a table, so the section is in practice closed to tables by a rule nobody
wrote down.

**Done when.** A markdown table added anywhere under `## Parameter provenance`
above the provenance table no longer produces missing-row errors: either the
provenance table is found by something other than position, or the checker says
in one message that it could not find a table with the provenance header. A test
covers a document with a decoy table above the real one.
