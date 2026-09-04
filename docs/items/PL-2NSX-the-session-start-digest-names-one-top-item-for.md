---
id: PL-2NSX
title: The session-start digest names one Top: item for every session, so two parallel sessions still open on the same id
priority: P2
effort: S
status: done
classes: session-cost, infra
feature: parallel-sessions
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/cli.py, subprojects/docket/README.md, .claude/skills/docket/SKILL.md
added: 2026-09-04
closed: 2026-09-04
pr: 287
verify: uv run pytest subprojects/docket/tests/test_cli.py -q -k digest
---

**Problem.** `PL-8165` split `docket next` into `product` and `workflow` lanes
so two simultaneous sessions never rank onto the same item. The session-start
digest was left whole, and it is what a session reads *first* — before it would
think to ask for a lane, and before the `docket` skill has loaded. So two
parallel sessions still opened on an identical `Top:` line, and the split only
took effect once somebody remembered to type the lane.

**Why it matters.** The digest is the cheapest moment to prevent the collision,
and the one that needs no instruction to be followed. Every guard downstream of
it depends on a session choosing to run something.

**Where.** `subprojects/docket/src/docket/render.py`, `format_digest`, and a
new `_by_lane` beside the `Top:` line it already builds through `recommend`.

Of the three shapes considered, the project owner chose the first: print both
lane tops. The hook runs before anything has been said, so it cannot know which
half this session is; naming both means it never has to guess, and nothing has
to be configured or remembered at launch. The alternatives — reading a lane
from the environment, or leaving the digest whole — both put the remembering
one step earlier, which is the failure being fixed.

    By lane, for a second session: product PL-F52R, workflow PL-Y0RZ; 15 in neither lane.

Ranked through `recommend` with the same plan the `Top:` line uses, because two
lines in one block ranked by different rules contradict each other where a
reader sees both at once. It costs one line in every digest, single-session
ones included, which is what "for a second session" is doing in it. Omitted
where no `workflow_paths` are declared or neither lane has anything startable.
The spanning count rides the same line: two picks read as the whole queue
without it.

**Done when.** Two sessions started for opposite halves of the project read
different recommended ids at startup, with no flag to set and nothing to
remember.
