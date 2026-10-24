---
id: PL-TSXD
title: docket decides whether an item is open by hand in 19 places (6 write status in OPEN_STATUSES, 13 write status not in CLOSED_STATUSES, which differ for a status in neither set) instead of reading Item.is_open, across checks.py, plan.py, cli.py, model.py, verify.py and three tools
status: untriaged
feature: one-source-of-truth
added: 2026-10-19
---

**Problem.** docket decides whether an item is open by hand in 19 places (6 write status in OPEN_STATUSES, 13 write status not in CLOSED_STATUSES, which differ for a status in neither set) instead of reading Item.is_open, across checks.py, plan.py, cli.py, model.py, verify.py and three tools
