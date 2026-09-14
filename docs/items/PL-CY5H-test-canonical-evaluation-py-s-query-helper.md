---
id: PL-CY5H
title: test_canonical_evaluation.py's _query helper probes from a hard-coded 0.0 rather than the definition's own opening, so it cannot be pointed at a branch-shaped definition
priority: P3
effort: S
status: ready
classes: test
feature: scenario-branching
touches: tests/reference/test_canonical_evaluation.py
added: 2026-09-14
verify: uv run pytest tests/reference/test_canonical_evaluation.py && ! grep -q 'probe from a hard-coded 0.0' tests/reference/test_canonical_evaluation.py && grep -q 'definition.opened_at_s' tests/reference/test_canonical_evaluation.py
---


**Problem.** test_canonical_evaluation.py's _query helper probes from a hard-coded 0.0 rather than the definition's own opening, so it cannot be pointed at a branch-shaped definition

**Verified 2026-09-14.** The helper is `_query` at
`tests/reference/test_canonical_evaluation.py:184`, and it probes from a fixed
`0.0` rather than from the definition's own opening.

**Why it matters.** The canonical evaluation rule is what `docs/MODEL.md` states
determinism on - which of two routes to a time is authoritative - and it is
safety- and science-classed scope inside v0.5.0. A branch's definition opens at
the fork instant, not at induction, so a helper anchored to zero cannot be
pointed at one: the property the suite exists to prove is currently proven only
for trunk-shaped definitions. That is a gap in coverage of a rule whose whole
purpose is to hold when a time can be reached by more than one route, which is
exactly the branch case.

**Done when.** `_query` probes from the definition's own `opened_at_s` rather
than from `0.0`, so the same assertions run against a branch-shaped definition,
and `tests/reference/test_canonical_evaluation.py` exercises one.
