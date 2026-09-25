---
id: PL-1X56
title: claim exits 0 for a claim no other session can see, printing 'not pushed', while a failed push leaving the same invisible state exits 4, and every claim made after a branch's first push takes that path
status: untriaged
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/claims.py, subprojects/docket/tests/test_claiming.py
added: 2026-09-25
---

**Problem.** claim exits 0 for a claim no other session can see, printing 'not pushed', while a failed push leaving the same invisible state exits 4, and every claim made after a branch's first push takes that path

Reproduced (scenario i, and 9 distinct instances across 6 seeded random runs): `claim X` exits 0 with "not pushed"; a second clone fetches, `next` offers X, `show X` has no mark. It is the entry route to the late-claim displacement above. Related to PL-WX87, which covers only the stale-tracking-ref variant.

**Why it matters.** Exit status is what a session reports as evidence; 0 says the claim is visible when it is not.

**Done when.** An unpushed claim exits non-zero, or claim pushes; a test holds scenario i.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
