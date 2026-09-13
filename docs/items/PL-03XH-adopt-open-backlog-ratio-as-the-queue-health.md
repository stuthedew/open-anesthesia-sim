---
id: PL-03XH
title: Adopt open-backlog ratio as the queue health measure
status: dropped
added: 2026-09-13
closed: 2026-09-13
reason: the comparison set is multi-contributor projects where an open issue is a promise to a stranger; the measure does not transfer to a solo queue
---

**Problem as filed.** This store is 238 open of 820 filed (29%) against
microsoft/vscode 7.3%, kubernetes/kubernetes 3.7%, home-assistant/core 3.6%
(GitHub Search API, measured 2026-09-13).

**Why it is dropped.** The ratio is real but it is not a health measure here.
In those projects an open issue is an outstanding promise to an external
reporter, and the low ratio is produced by closing aggressively to manage that
relationship - vscode closed 42.2% of its 2024 cohort as `not-planned`. On a
solo project every item is a note to oneself; 29% open describes how one person
works, not a defect. Chasing the number would import a policy whose purpose is
community management.

**What the store's own dynamics say.** Open set peaked at 258 on 09-10 and is
238 now; last 7 days net +1.4/day, last 3 days -6.7/day. Nothing has ever taken
more than 14 days to reach terminal; 58.7% close the same day. There is no
divergence to correct.
