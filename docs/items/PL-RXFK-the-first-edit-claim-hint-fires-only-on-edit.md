---
id: PL-RXFK
title: The first-edit claim hint fires only on Edit, Write, MultiEdit and NotebookEdit, so a session editing through Bash, which the harness's auto mode recommends for small edits, is never told its branch claims nothing and learns it from CI's branch-id refusal a push later
status: untriaged
touches: .claude/hooks/docket-branch-guard.sh, .claude/settings.json
added: 2026-09-25
---

**Problem.** The first-edit claim hint fires only on Edit, Write, MultiEdit and NotebookEdit, so a session editing through Bash, which the harness's auto mode recommends for small edits, is never told its branch claims nothing and learns it from CI's branch-id refusal a push later

Seen 2026-09-25 in the session that filed this. It inserted `docs/maintainer.md` § "Read a simulator change before you arm it" with a Bash-run Python edit on `claude/awesome-cray-gglruu`. `.claude/hooks/docket-branch-guard.sh` is attached to the four edit tools only (`.claude/settings.json`), so it never ran for that edit. No `/tmp/docket-claim-<session>` marker was written, and no hint reached the transcript. The first word came from CI's `checks` job 108281894829 on #1027, one push later. `python3 tools/branch_id_check.py --hint docs/maintainer.md`, run by hand on the same branch, prints the hint, so the reader is right and only the trigger misses. The harness's auto mode tells sessions to prefer Bash for small edits, so this path is common, not rare.
