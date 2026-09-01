---
id: PL-1CYR
title: Nothing re-checks the branch against main once a session is already underway
priority: P2
effort: S
status: done
classes: defect, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py, tests/unit/test_docket_digest_hook.py, .claude/hooks/docket-digest.sh, subprojects/docket/README.md
added: 2026-08-31
closed: 2026-08-31
pr: 125
verify: uv run pytest -k branch_state
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

**Done 2026-08-31, as `bin/docket branch`.** The decision is `branch_state` in
`vcs.py`, which returns the position, the disposition (`current`, `restart`,
`pull`, `merge`), the ids that landed on the base since the fork, and why it
declined where it did; `render` turns one of those into the sentence and the
command; the hook is two calls and no git of its own.

**Four things the brief did not ask for, and one it did that was not built.**

*Not built:* the `rebase origin/main` recovery. Distinguishing "carries only its
own capture commits" from any other commits means guessing, and a rebase of a
pushed branch needs a force-push, which this project's squash-merge path exists
to avoid. The two commands the hook already printed are kept and a test asserts
no third appears.

*Built anyway:* the hook fetched **after** running the digest, so the
stranded-item line was computed from the previous session's refs while the
comment above it said the fetch was there to give that line something to read.
The order is now fetch (inside `docket branch`), then digest.

*Built anyway:* the command fetches and the function does not. The brief put
the fetch outside on the grounds that `docket check` must run from a bare
checkout - true of the *decision*, which is why `branch_state` never fetches -
but a command whose one question is "has the base moved" would answer
"current" from a ref nobody refreshed. `--no-fetch` is for the caller that
cannot, and the line says so.

*Built anyway:* "no comparison exists" is separated from "the comparison could
not be made". A detached HEAD, no base, and the default branch with no remote
copy are the first; the hook's silence in those cases is preserved through
`--brief`, and a person who runs the command is told why. A clone sharing no
readable history is the second, and still says so out loud.

*Built anyway:* `tests/unit/test_docket_digest_hook.py` stubbed `bin/docket`,
so its four cases would have gone on passing against a hook that no longer did
anything. They now install a shim that execs the real command and run with
`cwd` set to the fixture, which tests the whole path a session start takes -
hook, fetch, command, git - on real shallow and unrelated-history clones. They
are not selected by `-k branch_state`; `make check` runs them.

**What it does not do, and this is the half worth deciding.** Nothing calls it
mid-session. The brief said the gap closes "as a side effect rather than as a
second mechanism", and it does not: `bin/docket branch` can now be asked at any
moment, which makes the gap *closable* rather than closed. What would close it
is either a line naming the command in the digest (which is resent on every
turn, so it is always in front of the session) or a `PreToolUse` hook on the
first edit, which fires whether or not the session remembers. Left for the
project owner, per the reply that closed this out.
