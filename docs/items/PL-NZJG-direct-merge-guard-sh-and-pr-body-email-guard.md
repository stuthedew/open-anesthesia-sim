---
id: PL-NZJG
title: direct-merge-guard.sh and pr-body-email-guard.sh are wired on exact GitHub MCP tool names (merge_pull_request, create_pull_request, update_pull_request), so a rename by the GitHub server stops both guards with no sign; widen each to the namespace or say in its header what goes unchecked, as owner_ask_guard.py now does (found building PL-YN60)
status: untriaged
feature: guard-tool-names
added: 2026-11-02
---

**Problem.** direct-merge-guard.sh and pr-body-email-guard.sh are wired on exact GitHub MCP tool names (merge_pull_request, create_pull_request, update_pull_request), so a rename by the GitHub server stops both guards with no sign; widen each to the namespace or say in its header what goes unchecked, as owner_ask_guard.py now does (found building PL-YN60)

**Next steps, written 2026-11-02 before a reset for length.** The project
owner asked for this fix on 2026-11-02, right after `PL-YN60`. Build it on a
fresh branch from `main` once `#1931` has merged, since this file arrives
with it.

1. Triage the item: priority, effort, classes, touches, payoff, Done when,
   verify.
2. Read both hooks whole. `direct-merge-guard.sh` lets a session's merge
   through only while GitHub holds it to the base branch's checks (`PL-NXRJ`).
   `pr-body-email-guard.sh` refuses a pull request title or body that holds
   the owner's email address.
3. Widen each `.claude/settings.json` matcher so that a renamed GitHub tool
   still reaches its hook, and let each script decide which calls it judges.
   This follows `.claude/rules/apparatus-standard.md` § "The floor", the
   paragraph on guards keyed on names another system owns. Two hazards to
   test: `enable_pr_auto_merge` contains "merge" and must pass the merge
   guard untouched, and most `pull_request` tools carry no title or body, so
   the email guard must pass any call without one. Where widening would
   refuse real work, say instead in the hook's header what goes unchecked
   when a name changes.
4. Add regression tests that fail against today's matchers: a renamed merge
   tool, and a renamed create or update tool carrying the email address.
