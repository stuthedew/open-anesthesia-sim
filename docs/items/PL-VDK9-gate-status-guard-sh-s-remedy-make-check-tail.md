---
id: PL-VDK9
title: gate-status-guard.sh's remedy 'make check && tail -45 /tmp/gate.log' has no redirect, so copied as written it prints the whole run and then the tail of an older log; its test pins the text, not what it does
status: untriaged
feature: guard-review-2026-11
added: 2026-11-03
---

**Problem.** gate-status-guard.sh's remedy 'make check && tail -45 /tmp/gate.log' has no redirect, so copied as written it prints the whole run and then the tail of an older log; its test pins the text, not what it does
