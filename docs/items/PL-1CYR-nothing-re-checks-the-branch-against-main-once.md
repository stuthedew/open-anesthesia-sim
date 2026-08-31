---
id: PL-1CYR
title: Nothing re-checks the branch against main once a session is already underway
priority: P2
effort: S
status: ready
classes: defect, infra
feature: parallel-sessions
milestone: v0.2.8
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, .claude/hooks/docket-digest.sh, subprojects/docket/README.md
added: 2026-08-31
verify: uv run pytest subprojects/docket/tests/test_vcs.py -k branch_state
---

**Problem.** `PL-037` put the branch-vs-`main` check in the session-start
hook, which was right for the case it had: a session that picks up an
already-merged branch. But the check runs **once, at session start**, and the
condition it guards against develops *during* a session.

The owner's actual pattern makes that the common case rather than the edge
one: open a session to discuss the next piece of work while another session is
still finishing something, talk for a while, and by the time the discussion
becomes implementation the other session has merged and this branch's base is
stale. The digest opened this very session with `Branch:
claude/parallel-session-workflow-kpeet1, current with origin/main (0 ahead)` —
true when printed, and false the moment the other session lands. Nothing looks
again, so the staleness is discovered at push time in merge conflicts, which
is the rework cycle `PL-037` was written to prevent.

**Why it matters.** It costs a full rework cycle, paid at the end of a session
rather than the start — and it is paid precisely in the sessions the owner
uses to think, which are the ones that must stay cheap.

**One implementation, two callers.** `branch_state()` in
`.claude/hooks/docket-digest.sh` is ~50 lines of bash that duplicates logic
`vcs.py` already half-carries in `default_base` and `behind_remote`. Move the
decision into `vcs.py`, expose it as `bin/docket branch`, and have the hook
call that. Same total surface, one copy of the rule, and the mid-session gap
closes as a side effect rather than as a second mechanism.

**It prints; it does not act.** `git checkout -B` discards commits, so it must
never fire unattended, and printing keeps the property `vcs.py`'s own
docstring names — this reports rather than blocks. It picks between
`checkout -B` (the branch has nothing of its own) and `rebase origin/main`
(the branch carries only its own capture commits) and shows the command.

**The fetch stays outside it.** `docket check` must run from a bare checkout
with no network, and `merged_pull_requests` already declines to fetch for that
reason. The caller runs `git fetch origin main` first.

**What it prints is what makes it worth having.** Position against `main`, the
correct command, **which items landed on `main` since this branch forked**, and
what is still in flight (`PL-KWC1`). That last pair answers "did the thing I
was waiting on finish?" from the command already being run — no polling, no
wake subscription, no second mechanism to keep true.

**Where.** `subprojects/docket/src/docket/vcs.py` for the decision,
`cli.py`/`render.py` for the command, `.claude/hooks/docket-digest.sh` reduced
to a fetch plus the call.

**Done when.** `bin/docket branch` reports the branch's position, names the
correct recovery command for each of the states the hook currently handles,
lists the items that landed on `main` since the fork, and the hook produces
its existing digest line by calling it rather than by its own bash.
