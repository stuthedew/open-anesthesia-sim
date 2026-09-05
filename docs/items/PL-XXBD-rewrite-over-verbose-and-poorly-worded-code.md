---
id: PL-XXBD
title: Rewrite over-verbose and poorly worded code comments across src/ and tests/
status: dropped
added: 2026-09-05
closed: 2026-09-05
reason: split into two items, with the project owner's agreement (2026-09-05), because at `L` this could not be started from a queue entry. PL-1K5X takes `src/` and PL-FDMJ takes `tests/`. The halves are even by the measure that matters: 4,644 lines of comment and docstring prose in `src/` against 4,530 in `tests/`, measured 2026-09-05. The safety-critical qualifier this item stated - shorten the prose, keep the *why* - is carried into both, and PL-1K5X records that it lands almost entirely in `core/`. The body below is the reasoning; it was not rewritten into either child
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

**Where.** `src/`, `tests/` - 9,654 and 17,356 lines respectively, which is
what makes this `L`.

**Done when.** Every comment and docstring in `src/` and `tests/` has been read
and, where it was padded, cut: nothing restating the line below it, no
docstring paragraph repeating its own first sentence, no clause that adds
nothing. Every *why* is still on the page - each provenance note, unit, cited
equation and reason-a-value-is-what-it-is, in the same file it was in - and
`make check` passes.
