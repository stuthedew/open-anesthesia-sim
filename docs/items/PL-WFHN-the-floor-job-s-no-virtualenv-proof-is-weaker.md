---
id: PL-WFHN
title: The floor job's no-virtualenv proof is weaker on a persistent self-hosted runner, where state survives between jobs
status: dropped
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
closed: 2026-09-05
reason: Conditional on PL-PVHD, which was reverted 2026-09-05. CI runs on
  GitHub-hosted runners, where every job gets a fresh VM, so the floor job's
  isolation is not at risk. Reopen with PL-PVHD if a self-hosted runner is
  ever adopted.
---

**Problem.** The floor job's no-virtualenv proof is weaker on a persistent self-hosted runner, where state survives between jobs

**Why it matters.**

**Where.**

**Done when.**
