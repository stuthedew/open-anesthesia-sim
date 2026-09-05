---
id: PL-1K5X
title: Cut the padded comments and docstrings across src/
priority: P2
effort: M
status: ready
classes: docs
feature: prose-quality
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, src/anesthesia_sim/app
added: 2026-09-05
not-delegable: readability is judged by a person, and no command separates a trimmed comment from a padded one. A length ceiling would be met by deleting the provenance note this item exists to keep, which is the one outcome it forbids. `touches` reaches `src/anesthesia_sim/core` and `src/anesthesia_sim/data` besides, which delegation may never modify
---

**Problem.** The comments and docstrings in `src/` are, in the project owner's
reading (2026-09-05), far too verbose and poorly written. One of two halves
split out of `PL-XXBD` (rewrite the code comments across `src/` and `tests/`),
which was `L` and therefore unstartable from the queue.

**Measured 2026-09-05, with the tokenizer:** roughly 4,600 of `src/`'s ~9,700
lines are comment or docstring prose - about half the tree. It is concentrated
in `src/anesthesia_sim/app` (~3,800 lines of prose in ~7,300), with
`src/anesthesia_sim/core` carrying ~790 in ~2,300 and `src/anesthesia_sim/data`
effectively none. That is where the two standards below divide, and it is worth
knowing before starting: most of the volume is UI prose, and most of the care
is owed to a tenth of it.

**Why it matters.** The standard is **human readability**, and that is the
whole of it: a person opening the file should reach the point faster and
understand more. Wordiness is the defect and cutting it is the fix. This is
deliberately *not* the standard `PL-JK0M` applies to the agent-facing
instruction files, where cutting a rule for being wordy is the forbidden
outcome.

**The safety-critical qualifier, which lands almost entirely in `core/`.** In a
calculation path, padding around the reasoning is what hides it, so trimming
serves the reviewer. What a comment must never lose is the *why* - a provenance
note, a unit, a cited equation, or the reason a value is what it is. Shorten
the prose, keep the fact.

**Where.** `src/`. Counts are measured 2026-09-05 and rounded because they move every release; re-measure before starting rather than trusting them - they are here for ordering, not as a claim.

**Done when.** Every comment and docstring under `src/` has been read and,
where it was padded, cut: nothing restating the line below it, no docstring
paragraph repeating its own first sentence, no clause that adds nothing. Every
*why* is still on the page - each provenance note, unit, cited equation and
reason-a-value-is-what-it-is, in the same file it was in. `make check` passes.
