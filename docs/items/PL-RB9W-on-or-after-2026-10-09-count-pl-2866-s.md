---
id: PL-RB9W
title: On or after 2026-10-09, count PL-2866's falsifier: apparatus findings that blocked or were captured during product items, against simulator items closed since the 2026-09-25 switch; the blocking rule is wrong above about 1 per 10
status: untriaged
feature: workflow-stress-2026-09
added: 2026-09-25
---

**Problem.** On or after 2026-10-09, count PL-2866's falsifier: apparatus findings that blocked or were captured during product items, against simulator items closed since the 2026-09-25 switch; the blocking rule is wrong above about 1 per 10

**How.** `PL-2866` pre-registered it. Its blocking rule (an apparatus finding stops a product session only when it blocks it) is wrong if deferred apparatus defects bite product sessions more often than about 1 per 10 product items. The baseline is 7 apparatus defects found during product work against 72 simulator items closed, 2026-09-15..25, counted by the inflow scripts in `docs/stress-2026-09-25/evidence.tar.gz`. Re-run them over 2026-09-25..10-09 and count two things apart: findings that *blocked* a product item, so it stopped for them, and findings captured during one and deferred. A deferred one that later bit a product session counts against the rule. Not before 2026-10-09, the two weeks the decision named.
