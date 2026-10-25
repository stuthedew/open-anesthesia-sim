---
id: PL-KM19
title: tests/unit/test_parameters.py: two docstrings count the payload models as seven and eight, but the test below them asserts nine subclasses of _StrictPayload (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: ready
classes: docs
feature: stale-source-claims
touches: tests/unit/test_parameters.py
added: 2026-10-25
payoff: the parameter tests' docstrings stop stating a count of payload models that the code has already outgrown
verify: ! grep -qF "today's eight" tests/unit/test_parameters.py && ! grep -qF 'The seventh payload model' tests/unit/test_parameters.py
---

**Problem.** tests/unit/test_parameters.py: two docstrings count the payload models as seven and eight, but the test below them asserts nine subclasses of _StrictPayload (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 685 ("The seventh payload model added later") and line 703 ("not just today's eight"), above a test that walks the subclasses of `_StrictPayload`.

**Why it matters.** The count is meant to tell a reader how many payload models exist today. Two different wrong counts in one file teach a reader that the docstrings cannot be trusted.

**Done when.** Neither docstring states a count that the code can outgrow, or both state the current count. No test changes behaviour.
