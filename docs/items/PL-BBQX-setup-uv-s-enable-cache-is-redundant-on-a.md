---
id: PL-BBQX
title: setup-uv's enable-cache is redundant on a persistent self-hosted runner, whose uv cache already survives between runs
status: dropped
feature: ci-cost
touches: .github/workflows/quality.yml
added: 2026-09-05
closed: 2026-09-05
reason: Conditional on PL-PVHD, which was reverted 2026-09-05. On GitHub-hosted
  runners nothing survives between jobs, so setup-uv's enable-cache is doing
  real work rather than redundant round-trips. Reopen with PL-PVHD.
---

**Problem.** setup-uv's enable-cache is redundant on a persistent self-hosted runner, whose uv cache already survives between runs

**Why it matters.**

**Where.**

**Done when.**
