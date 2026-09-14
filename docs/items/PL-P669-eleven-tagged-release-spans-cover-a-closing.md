---
id: PL-P669
title: Eleven tagged release spans cover a closing pull request their own notes never name, and nothing points a reader from the tag to where that work is described
priority: P3
effort: M
status: ready
classes: docs
feature: commit-provenance
touches: docs/releases, ROADMAP.md, tools/doc_check.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def check_tag_span_covers_its_notes' tools/doc_check.py
---


**Problem.** Eleven tagged release spans cover a closing pull request their own notes never name, and nothing points a reader from the tag to where that work is described

**The eleven were not re-counted here**, and that is the first thing whoever
picks this up should do - the count was taken at capture and the history has
moved since, including the `v0.4.25` cut. What can be said from this pass is
that the mechanism is real and is the same one two other items describe:
`PL-2M5T` (notes written before `bin/docket record` backfills `pr`, so 9 of
v0.4.22's 15 bullets name no pull request) and `PL-028F`, which v0.4.22 records
as having closed the case of work landing *between* a cut and its merge.

**Why it matters.** A tag is what a reader resolves a commit to, and the notes
are where that release's reasoning lives. Where a span covers a closing pull
request its notes never name, the two records disagree about what shipped and
neither points at the other - so the work is findable only by someone who
already knows it happened. This is provenance of the permanent kind: nothing
rewrites a cut release's notes, so each instance is permanent once tagged.

**Done when.** The count has been re-taken against today's tags; each span whose
closing pull request its notes do not name is either repaired or recorded as
knowingly left, with the reason; and a check fails the *next* one rather than
leaving it to be noticed - which is the half that stops this recurring.
