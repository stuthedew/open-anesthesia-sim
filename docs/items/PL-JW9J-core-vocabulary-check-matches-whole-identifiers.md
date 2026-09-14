---
id: PL-JW9J
title: core_vocabulary_check matches whole identifiers because two live names would have failed a substring rule, and since PL-6KNM neither exists: decide whether to tighten
priority: P3
effort: S
status: needs-decision
classes: defect
feature: dev-tooling
touches: tools/core_vocabulary_check.py, tests/unit/test_core_vocabulary_check.py
added: 2026-09-14
---


**Problem.** core_vocabulary_check matches whole identifiers because two live names would have failed a substring rule, and since PL-6KNM neither exists: decide whether to tighten

**Verified 2026-09-14.** `tools/core_vocabulary_check.py:46` states the rule in
the tool's own words - "**Matching is on the whole identifier, never on a
substring.**" - and gives the reason it was written that way: two live names
would have failed a substring rule. `PL-6KNM` renamed one of them and the item
records that neither now exists, so the constraint the rule was relaxed for is
gone.

**Why it matters.** A whole-identifier rule cannot see a retired name embedded
in a longer one, which is the shape the retirements actually take - a local, a
keyword argument, a docstring phrase - so the check passes over exactly the
residue a rename leaves behind. Against that, tightening to a substring rule
buys nothing if the population it would newly catch is empty, and costs a false
positive on every legitimate identifier that contains a retired word.

**Decision needed.** Whether to tighten `core_vocabulary_check` from
whole-identifier matching to substring matching now that `PL-6KNM` has removed
the two names the relaxation was written for.

`.claude/rules/expert-review.md` requires the number that would make tightening
wrong to be named and then counted before the proposal is made, and this item
was filed without it. The count to take is on `src/anesthesia_sim/core/`, under
the retired-name list the tool already holds: how many *additional* occurrences
a substring rule would flag, and how many of those are real residue rather than
an unrelated identifier that happens to contain the word. Tightening is right
only if the second number is a clear majority of the first.

- **Tighten.** Right if the substring rule finds real residue and few or no
  false positives.
- **Leave it, and record why.** Right if the additional population is empty or
  is dominated by legitimate identifiers - and then this item closes as
  `dropped` with the count as its reason, so the question is not re-raised.

Whoever answers it should take the count first; the answer follows from it
rather than from an argument.

**Done when.** The count above has been taken and acted on: either
`tools/core_vocabulary_check.py` matches on substrings with
`tests/unit/test_core_vocabulary_check.py` covering a retired name embedded in a
longer identifier, or this item is closed `dropped` with the count as its
reason.
