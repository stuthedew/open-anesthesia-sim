---
id: PL-W6JM
title: tests/unit/test_headless_worker.py fails 12 tests when the checkout is shallow, as a cloud session's clone starts, because headless_worker clones with the checkout as a reference repository and git refuses a shallow reference (seen in make check on 2026-11-03)
status: untriaged
added: 2026-11-03
---

**Problem.** tests/unit/test_headless_worker.py fails 12 tests when the checkout is shallow, as a cloud session's clone starts, because headless_worker clones with the checkout as a reference repository and git refuses a shallow reference (seen in make check on 2026-11-03)
