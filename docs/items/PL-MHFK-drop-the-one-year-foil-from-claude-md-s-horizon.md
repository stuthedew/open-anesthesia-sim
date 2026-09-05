---
id: PL-MHFK
title: Drop the one-year foil from CLAUDE.md's horizon paragraph, which keeps being read as a leftover of the pre-correction horizon
priority: P2
effort: S
status: done
classes: docs
feature: worker-instructions
touches: CLAUDE.md
added: 2026-09-05
closed: 2026-09-05
pr: 346
verify: grep -q 'rather than traded for speed' CLAUDE.md && ! grep -q 'one-year' CLAUDE.md
---

**Problem.** `2f8c6bb` (`PL-QSWS`, #238) corrected the horizon from one year to
multi-year and, in the same edit, added a sentence arguing *why* the horizon is
load-bearing. It made the argument by contrast, naming the thing this project
is not:

> internal quality in the simulator that **a one-year project** could
> rationally trade for speed is worth paying for here

The contrast is sound and the sentence is true. It is also the most misread
sentence in the file, on the evidence of two independent failures:

- The project owner has twice returned to this line believing the one-year
  framing had survived the correction, most recently on 2026-09-05, which is
  the finding `PL-JRPP` was opened to sweep. A reader who meets "a one-year
  project" in the opening section does not reliably carry the negation four
  lines to where it is discharged.
- `PL-6SBB` found the same sentence failing in the other direction, and named
  the mechanism: **the standard is stated first and its scope arrives later**.
  It narrowed the clause to "in the simulator" but kept the foil, so the half
  that misfires on a human reader was left in place.

**Why it matters.** A resident sentence is read by every session and, being
resident, is quoted from memory rather than re-read in context. A foil is the
worst possible shape for that: strip the negation and the sentence asserts
exactly the horizon the correction removed, which is the horizon under which
trading internal quality for speed is the rational move. The cost is not
tidiness — it is that the file's opening section can be quoted as licence for
the failure mode the same paragraph names.

**Where.** `CLAUDE.md:24-25`, inside § "What this project is".

**Approach.** State the claim positively and delete the counterfactual. The
argument does not need it: "well above the design-payoff line" already carries
the comparison, so the foil was restating the premise in a form that could be
detached from it.

> …so internal quality in the simulator is worth paying for here rather than
> traded for speed, and slow accumulations that a single year would not
> surface…

"a year" became "a single year" in the following clause for the same reason:
that clause is about what an elapsed year fails to reveal, not about the
project's span, and the bare article let it be read as the latter. The
paragraph stays five physical lines, so the resident-instruction total is
unchanged at 548.

**Not a rewrite of the section.** Everything else in § "What this project is"
is the project owner's own framing and was left exactly as it stands.

**Decided 2026-09-05 (project owner).** Recommended in the `PL-JRPP` sweep
reply and approved: "yes, reword line 24".
