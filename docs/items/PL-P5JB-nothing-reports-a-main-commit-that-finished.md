---
id: PL-P5JB
title: Nothing reports a main commit that finished with no verdict: bin/docket's red-main line reads the latest conclusion rather than asking whether every commit has one, so a run cancelled while pending is indistinguishable from one that passed
status: dropped
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-16
closed: 2026-09-16
reason: Duplicate of `PL-SMN4`, whose **Done when.** already carries this as one of its two candidate shapes - "or accept the queue and add a check that a commit on `main` carries a completed run". Captured in this session before `PL-SMN4` had been read, which is the same not-looking failure `PL-99YZ` describes and this item was split out of `PL-X0ND` to avoid. Nothing is lost: `PL-SMN4` is `ready`, open, and names the reporting half explicitly
---

**Problem.** Nothing reports a main commit that finished with no verdict: bin/docket's red-main line reads the latest conclusion rather than asking whether every commit has one, so a run cancelled while pending is indistinguishable from one that passed
