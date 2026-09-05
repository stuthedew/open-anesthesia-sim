---
id: PL-XXBD
title: Rewrite over-verbose and poorly worded code comments across src/ and tests/
status: untriaged
feature: prose-quality
touches: src, tests
added: 2026-09-05
---

**Problem.** The comments in `src/` and `tests/` are, in the project owner's
reading (2026-09-05), far too verbose and poorly written. Rewrite them.

**Why it matters.** The standard here is **human readability**, and that is the
whole of it: a person opening the file should reach the point faster and
understand more. Wordiness is the defect and cutting it is the fix.

This is deliberately *not* the standard applied to the agent-facing
instructions in `PL-JK0M` (route or justify the resident instruction lines),
and the two must not be collapsed into one pass. There, cutting a rule for
being wordy is the forbidden outcome; here it is the point. The project owner
asked explicitly (2026-09-05) that the same standard not be applied to both.

The safety-critical qualifier: in a calculation path, padding around the
reasoning is what hides it, so trimming serves the reviewer. What a comment
must never lose is the *why* — a provenance note, a unit, a cited equation, or
the reason a value is what it is. Shorten the prose, keep the fact.

**Where.** `src/`, `tests/`.

**Done when.**
