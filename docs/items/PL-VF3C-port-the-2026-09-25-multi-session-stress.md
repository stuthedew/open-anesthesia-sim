---
id: PL-VF3C
title: Port the 2026-09-25 multi-session stress harness into subprojects/docket/tests as a regression suite: each reproduced violation a named scenario test, the seeded random interleavings behind a slow marker, and a fake forge that can say merged and closed as well as open
status: untriaged
feature: workflow-stress-2026-09
touches: subprojects/docket/tests/test_multisession.py, subprojects/docket/tests/conftest.py
added: 2026-09-25
---

**Problem.** Port the 2026-09-25 multi-session stress harness into subprojects/docket/tests as a regression suite: each reproduced violation a named scenario test, the seeded random interleavings behind a slow marker, and a fake forge that can say merged and closed as well as open

The harness (`harness.py` in the evidence archive, one stdlib file) builds a bare origin, a clone playing GitHub (squash-merge with `(#N)` subjects, branch deletion, closing), and N session clones, dates every commit from a world clock, and fakes pull-request state through `open_pull_requests_command`. It found eight violations across 19 scenarios and 180 seeded random steps; three were already filed (PL-X3NY, PL-QSGX, PL-WX87-adjacent). Today every one of those was found by a session stumbling on it during other work: 85% of apparatus defects filed 2026-09-15..25 were found while working another apparatus item.

**Why it matters.** Class B (distributed-state inference) is 26% of apparatus defect inflow and 12 of the 35 generator heads. A defect found by CI in bulk costs one fix; the same defect found by sessions arrives as one item per session that trips it.

**Done when.** The scenario matrix runs under `pytest` in the docket suite with each V1-V8 reproduction as a named test (xfail until its item closes), and a seeded random run is available behind a marker.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
