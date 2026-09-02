---
id: PL-K2YF
title: ROADMAP.md's release narrative skips v0.2.6, so the convention that each release adds a paragraph has already been missed once
priority: P2
effort: S
status: ready
classes: defect, docs, infra
feature: planning-cadence
touches: ROADMAP.md, tools/doc_check.py, tests/unit/test_doc_check.py
added: 2026-09-01
verify: uv run pytest tests/unit/test_doc_check.py && grep -q '^v0.2.6 was' ROADMAP.md && grep -q 'def test_a_completed_release_needs_a_narrative_paragraph' tests/unit/test_doc_check.py
---

**Problem.** `ROADMAP.md`'s "Release narrative" says of itself that "adding a
release means adding a paragraph here and editing one heading". Its paragraphs
now run v0.2.7, v0.2.5, v0.2.4, v0.2.3: **v0.2.6 is absent**. Cutting v0.2.8
moved v0.2.7's baseline prose down into the narrative, which is what the
convention describes; v0.2.6's prose was replaced rather than moved when
v0.2.7 was cut, and nothing noticed.

**Why it matters.** Small on its own - one release's reasoning is in
`docs/releases/v0.2.6.md` and in the version-table row either way. It matters
because of what the narrative is *for*: the version table carries one sentence
per release and the narrative carries why the change was made, and a reader
looking for the reasoning behind the delegation and release-tooling work finds
the paragraph missing with no indication that it ever existed. A convention
that has silently failed once will fail again, and this is the second document
in the release path where the fix is a check rather than a habit - `PL-M5FK`
and `PL-8HJ2` were both the same shape.

**Where.** `ROADMAP.md` - the `### Release narrative` section under
`## Current baseline`. `tools/doc_check.py` already parses the version table
for the release-train and baseline checks, so it holds the rows to compare
against.

**Approach.** Two halves, and the second is the point. Write the missing
v0.2.6 paragraph from `docs/releases/v0.2.6.md`; then have `doc_check` compare
the versions marked completed in the table against the versions the narrative
names, and report any completed release with neither a narrative paragraph nor
the current-baseline mark. That is decidable by reading the file, which is the
`CLAUDE.md` test for putting it in code rather than in prose.

**Done when.** The narrative carries a v0.2.6 paragraph, and `make check`
fails if a completed release is added to the version table without one.
