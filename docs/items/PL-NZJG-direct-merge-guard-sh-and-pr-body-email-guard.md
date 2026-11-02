---
id: PL-NZJG
title: direct-merge-guard.sh and pr-body-email-guard.sh are wired on exact GitHub MCP tool names (merge_pull_request, create_pull_request, update_pull_request), so a rename by the GitHub server stops both guards with no sign; widen each to the namespace or say in its header what goes unchecked, as owner_ask_guard.py now does (found building PL-YN60)
status: untriaged
feature: guard-tool-names
added: 2026-11-02
---

**Problem.** direct-merge-guard.sh and pr-body-email-guard.sh are wired on exact GitHub MCP tool names (merge_pull_request, create_pull_request, update_pull_request), so a rename by the GitHub server stops both guards with no sign; widen each to the namespace or say in its header what goes unchecked, as owner_ask_guard.py now does (found building PL-YN60)
