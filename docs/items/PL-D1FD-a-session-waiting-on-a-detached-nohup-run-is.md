---
id: PL-D1FD
title: A session waiting on a detached nohup run is never woken when it ends or when the container restarts kills it; start runs as tracked background tasks and schedule a check-in
priority: P2
effort: S
status: done
touches: CLAUDE.md
added: 2026-10-25
closed: 2026-10-25
pr: 1793
payoff: a session waiting on a long run is re-invoked when it ends or dies, instead of sitting idle for hours
verify: grep -q 'Wait on a long run only through the harness' CLAUDE.md
---

**Problem.** On 2026-10-25 a project thread started two long runs with
`nohup sh -c '...' &` and ended its turn to wait on them. The runs were the
new `restated-constants` check across all limits and the full test suite on
the src/ prose rewrite. Nothing was set to wake the thread. A container
restart at about 06:30Z killed both runs. The thread sat idle until the
project owner asked "What are you waiting for?" at 13:41Z, about seven hours
later. No model tokens were lost, since both runs were plain programs, but
the wall-clock time and the container time were.

**Why it happened.** A process started with `nohup` or a trailing `&` is
invisible to the harness. Its end does not re-invoke the session, and neither
does its death. The Bash tool's `run_in_background` does re-invoke the
session when the command exits, and `send_later` delivers a check-in that
survives a container restart.

**Done when.** `CLAUDE.md` § "Session and tool-use efficiency" tells every
session to start a run it will wait on with `run_in_background`, to schedule a
`send_later` check-in before going idle, and to check `uptime` after a gap. It
also tells a thread facing a wait of more than an hour to take ready work
from `bin/docket next` first, or to tell the coordinator there is none.

**A second rule, for the same stall** (project owner, 2026-10-25, ratified,
over leaving the coordinator to notice an idle thread). The coordinator
recommended it and the owner agreed. While a thread waits on a run of more
than an hour, its place in the project does nothing. So before going idle on
such a wait, a thread runs `bin/docket next` in its lane and takes a ready
item inside the scope it was given. If there is none, it tells the
coordinator, so that the place can be filled.

**Why resident and not a hook.** A `PreToolUse` hook that refused `nohup`
would cost no resident context and would never fail to fire. But the
repository's hooks do not run in project threads (measured on `PL-CR81`),
which is where this happened, so the rule has to be in the file every session
loads. Nothing in that section can be cut to pay for it: each other bullet
there governs a different moment. The two added rules come to about 1,000 characters.

**Generator check.** Not a generator: one rule closes one cause, and no other
open item comes from detached runs.
