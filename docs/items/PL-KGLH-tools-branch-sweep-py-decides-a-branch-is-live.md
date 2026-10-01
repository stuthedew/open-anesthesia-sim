---
id: PL-KGLH
title: tools/branch_sweep.py decides a branch is live from 72 h of committer age (GRACE) although the claim record names the holding session, so a live session's branch past the grace reads as finished and a dead one inside it as live
status: untriaged
feature: recorded-not-inferred
added: 2026-10-01
---

**Problem.** tools/branch_sweep.py decides a branch is live from 72 h of committer age (GRACE) although the claim record names the holding session, so a live session's branch past the grace reads as finished and a dead one inside it as live

**Recorded alternative, from the 2026-10-01 survey.** Read the session id the claim record holds, or a recorded branch-opened fact. The 72 h grace is documented in the module docstring as covering a first push, so triage should weigh whether the claim record now covers that case. Shape A.
