---
id: PL-RXFK
title: The first-edit claim hint fires only on Edit, Write, MultiEdit and NotebookEdit, so a session editing through Bash, which the harness's auto mode recommends for small edits, is never told its branch claims nothing and learns it from CI's branch-id refusal a push later
priority: P2
effort: S
status: ready
classes: defect
feature: claim-record
touches: .claude/hooks/docket-branch-guard.sh, .claude/settings.json, tests/unit/test_docket_branch_guard.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-25
payoff: a session editing through Bash is told its branch claims nothing at its first edit that is work, as an Edit-tool session is, instead of by CI refusing its pull request a push later
verify: grep -q 'def test_branch_guard_says_to_claim_after_the_first_bash_edit_that_is_work' tests/unit/test_docket_branch_guard.py
---

**Problem.** The first-edit claim hint fires only on Edit, Write, MultiEdit and NotebookEdit, so a session editing through Bash, which the harness's auto mode recommends for small edits, is never told its branch claims nothing and learns it from CI's branch-id refusal a push later

Seen 2026-09-25 in the session that filed this. It inserted `docs/maintainer.md` § "Read a simulator change before you arm it" with a Bash-run Python edit on `claude/awesome-cray-gglruu`. `.claude/hooks/docket-branch-guard.sh` is attached to the four edit tools only (`.claude/settings.json`), so it never ran for that edit. No `/tmp/docket-claim-<session>` marker was written, and no hint reached the transcript. The first word came from CI's `checks` job 108281894829 on #1027, one push later. `python3 tools/branch_id_check.py --hint docs/maintainer.md`, run by hand on the same branch, prints the hint, so the reader is right and only the trigger misses. The harness's auto mode tells sessions to prefer Bash for small edits, so this path is common, not rare.

**Reproduced 2026-09-26 against 78b1a02b.** `.claude/settings.json` attaches `docket-branch-guard.sh` to `PreToolUse` on `Edit|Write|MultiEdit|NotebookEdit` alone. `Bash`'s `PreToolUse` runs the three command guards and not this one, and no `PostToolUse` hook watches `Bash`. The hook's other half, the stale-base line (`PL-Q9NJ`), misses a Bash edit the same way.

**Why it matters.** The claim is how every other session learns an item is taken, and the hint is what makes a forgetful session write one before its work is visible. A session editing through Bash, which auto mode recommends, gets neither line. It learns from CI's branch-id refusal a push later, by which time another session may have started the same item. This is not held by the generator pause: the hint exists and misses a common path, which is a defect in what exists.

**Done when.** A session whose first edit outside the queue is made through Bash gets the claim hint, and the stale-base line with it, once, as an Edit-tool session does. A session whose Bash calls write only item files is still not asked. Tests in `tests/unit/test_docket_branch_guard.py` hold both.

**Recommendation: a `PostToolUse` hook on `Bash` that reads the tree, not the command** (triage 2026-09-26). After each Bash call, until the session's markers exist, `git status --porcelain` (7-8 ms here) names what changed. The first path outside the queue goes to `tools/branch_id_check.py --hint` (0.94 s, once a session), and the answer travels as `additionalContext`. The other route, running the hint on every Bash call before it runs, is weaker both ways. A Bash call names no path, so it either asks at a session's first read-only command, spending the one question the hook's header keeps for work, or it parses the command for write targets, which the `python3 -c` edit seen here defeats. Speaking just after the edit rather than just before costs nothing, because the hint adds context rather than blocking, and what it replaces arrives a push later. A tree already holding work when the session starts is flagged at the first Bash call, which is right, since the branch still claims nothing.

**Generator check.** Re-entry of `PL-J9S0` (closed 2026-09-24), whose first-edit claim hint rode a hook attached to the four edit tools, and of `PL-Q9NJ` (closed 2026-09-01) for the stale-base half. The fact misread is which tool calls change the working tree. No head's `misread:` states it, and no other item misreads it.
