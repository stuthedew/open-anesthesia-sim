---
id: PL-XX68
title: tests/reference/test_published_wash_in_and_elimination.py: the module docstring says confirming the open-circuit inference needs the papers' full texts, but the comment above APPARATUS_DEAD_SPACE_L says both papers were supplied and read on 2026-09-13 (found in the PL-FDMJ prose pass, 2026-10-25)
priority: P3
effort: S
status: done
classes: docs
feature: stale-source-claims
touches: tests/reference/test_published_wash_in_and_elimination.py
added: 2026-10-25
closed: 2026-10-25
pr: 1817
payoff: the published-data comparison states correctly that its open-circuit inference was checked against the papers
verify: ! grep -qF 'needs the full texts' tests/reference/test_published_wash_in_and_elimination.py
---

**Problem.** tests/reference/test_published_wash_in_and_elimination.py: the module docstring says confirming the open-circuit inference needs the papers' full texts, but the comment above APPARATUS_DEAD_SPACE_L says both papers were supplied and read on 2026-09-13 (found in the PL-FDMJ prose pass, 2026-10-25)

**Reproduced 2026-10-25.** `grep` on `main` at `b6ff4443` finds line 95 of the module docstring ("needs the full texts"), while the comment above `APPARATUS_DEAD_SPACE_L` records both papers supplied and read on 2026-09-13.

**Why it matters.** This module compares the model with published wash-in and elimination data. Its docstring tells a reader whether the open-circuit inference was checked against the papers. Saying it was not, when it was, understates the evidence behind the comparison.

**Done when.** The module docstring says what reading the two papers on 2026-09-13 found about the open-circuit inference, in agreement with the comment. No test changes behaviour.
