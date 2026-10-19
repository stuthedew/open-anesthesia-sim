---
id: PL-MZCN
title: tools/headless_worker.py records a failed run with no reason: it drops claude's stdout and stderr, so the owner's first real run printed 'error, $0.00' and nothing said why
status: untriaged
feature: api-credit-runs
added: 2026-10-19
---

**Problem.** tools/headless_worker.py records a failed run with no reason: it drops claude's stdout and stderr, so the owner's first real run printed 'error, $0.00' and nothing said why
