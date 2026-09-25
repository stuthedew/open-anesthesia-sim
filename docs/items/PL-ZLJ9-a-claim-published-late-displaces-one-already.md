---
id: PL-ZLJ9
title: A claim published late displaces one already confirmed first, because claims are ordered by commit author date rather than by when they became visible, and claim's retry path never asks whether a visible rival claimed in between
status: untriaged
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claiming.py
added: 2026-09-25
---

**Problem.** A claim published late displaces one already confirmed first, because claims are ordered by commit author date rather than by when they became visible, and claim's retry path never asks whether a visible rival claimed in between

Reproduced (scenarios i2, a3): s1 captures and pushes, then `claim X` exits 0 with "not pushed"; s2 `claim X` exits 0, pushed, reads back first; s1 `git push`; now every fetched clone says s1 holds X and s2 is told "This branch yields: stop". Same via a failed push (exit 4) then a retry that exits 0 "already holds it first". Order `(%aI, hash)` is PL-MB2W's design; PL-J9S0's CI fence fires only after the fact.

**Why it matters.** Two sessions each told, in turn, that they hold the item: the duplicated-work failure the claim record exists to prevent.

**Done when.** A claim confirmed first-visible is never revoked by one published later; a test holds scenario i2.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
