---
id: PL-HNXS
title: tools/workflow_paths_check.py's ruff_configs and tools/fixture_id_check.py walk the filesystem rather than git's tracked files, so a worktree-isolated subagent's checkout under .claude/worktrees/ fails make check (6 ruff configs found where 3 are tracked; malformed-id hits inside the agent's copy of docs/items), seen 2026-10-03 during PL-YZ17's review
status: untriaged
added: 2026-10-03
---

**Problem.** tools/workflow_paths_check.py's ruff_configs and tools/fixture_id_check.py walk the filesystem rather than git's tracked files, so a worktree-isolated subagent's checkout under .claude/worktrees/ fails make check (6 ruff configs found where 3 are tracked; malformed-id hits inside the agent's copy of docs/items), seen 2026-10-03 during PL-YZ17's review
