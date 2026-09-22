---
id: PL-P669
title: Eleven tagged release spans cover a closing pull request their own notes never name, and nothing points a reader from the tag to where that work is described
priority: P3
effort: M
status: ready
classes: docs
feature: commit-provenance
touches: docs/releases, ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py, subprojects/docket/src/docket/release.py, subprojects/docket/tests/test_release.py
added: 2026-09-14
verify: uv run pytest tests/unit/test_doc_check.py && grep -q 'def check_tag_span_covers_its_notes' tools/doc_check.py
recurrences: 2026-09-22 PL-YKSD
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

**Swept 2026-09-19 under `PL-6ZQY` (crossing-lane consolidation). Still real, and the fault
reproduces at the newest tag.** No check exists
(`grep -c 'def check_tag_span_covers_its_notes' tools/doc_check.py` → 0); the
only mechanism is docket's advisory at `checks.py:838,852`, which landed in the
same commit that filed this item. Re-counted today by docket's own definition:
**12 closing pull requests across 9 spans**, against the brief's "12 … in 11
distinct spans" of 2026-09-14 - the pull request count is unchanged and the
span count should be treated as approximate, since a definitional difference
behind 9-versus-11 could not be excluded. The v0.4.27..v0.4.28 span covers
`#702` and `#703` and `docs/releases/v0.4.28.md` names neither `PL-1YT5` nor
`PL-V1F4`.

One correction: "nothing points a reader from the tag to where that work is
described" is false at the *class* level - `ROADMAP.md:121-125` says the two
records answer different questions and that the work is described in the next
release's notes. That paragraph landed in the same commit as this item, so it
is not later work; what no individual notes file carries is a pointer of its
own, which is the narrower claim to make.
