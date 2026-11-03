---
id: PL-9PPJ
title: gate-status-guard.sh refuses commands that run no gate: timing tools/doc_check.py with output sent to /dev/null, ruff --version | head, pytest --collect-only | tail; and it refuses make check && echo PASS || echo FAIL while admitting make check || echo failed: $?, though both print the verdict
status: untriaged
feature: guard-review-2026-11
added: 2026-11-03
---

**Problem.** gate-status-guard.sh refuses commands that run no gate: timing tools/doc_check.py with output sent to /dev/null, ruff --version | head, pytest --collect-only | tail; and it refuses make check && echo PASS || echo FAIL while admitting make check || echo failed: $?, though both print the verdict
