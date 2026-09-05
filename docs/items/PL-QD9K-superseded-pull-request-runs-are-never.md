---
id: PL-QD9K
title: Superseded pull request runs are never cancelled, so about eight percent of CI minutes go to results nobody reads
status: dropped
feature: ci-cost
touches: .github/workflows/quality.yml, .github/workflows/pr-title.yml
added: 2026-09-05
closed: 2026-09-05
reason: Duplicate of PL-FFLL, which captured the same finding on 2026-09-01 and
  prescribed the same guarded `concurrency` block. Filed without checking the
  open queue first; PL-TH7P is the item that would have caught it at capture
  time. The work landed under PL-FFLL.
---

**Problem.** Superseded pull request runs are never cancelled, so about eight percent of CI minutes go to results nobody reads

**Why it matters.**

**Where.**

**Done when.**
