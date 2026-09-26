---
id: PL-N6JP
title: gate-status-guard.sh reads a tools/*_check.py invocation as a gate whatever its arguments, so python3 tools/pr_body_check.py --help | head is refused as throwing a verdict away, though --help prints usage and exits 0 with no verdict to lose - met 2026-09-26 in ordinary work, by the PL-61FT design session
status: untriaged
feature: bash-guard-bound
added: 2026-09-26
---

**Problem.** gate-status-guard.sh reads a tools/*_check.py invocation as a gate whatever its arguments, so python3 tools/pr_body_check.py --help | head is refused as throwing a verdict away, though --help prints usage and exits 0 with no verdict to lose - met 2026-09-26 in ordinary work, by the PL-61FT design session
