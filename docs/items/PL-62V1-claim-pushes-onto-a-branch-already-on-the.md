---
id: PL-62V1
title: claim pushes onto a branch already on the remote where the forge reports no pull request open on it, so a rider claim under the push-first protocol reaches the remote without a second push by hand
priority: P3
effort: S
status: blocked
classes: infra, session-cost
feature: claim-integrity
touches: subprojects/docket/src/docket/claiming.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_claiming.py, .claude/skills/docket/modes/start.md
blocked-by: PL-979D, PL-GPJ7, PL-HMZZ, PL-MT3R, PL-PVW2, PL-QHCW, PL-XBV4
added: 2026-09-25
---

**Problem.** claim pushes onto a branch already on the remote where the forge reports no pull request open on it, so a rider claim under the push-first protocol reaches the remote without a second push by hand

**Captured in `PL-1X56`'s commit** (`688827c1`, #1026, 2026-09-25). That item
kept `claim`'s refusal to push onto a branch the remote already has, and
exits 4 for the claim it leaves local, because `claim` "knows nothing about
the forge, so it cannot tell an armed pull request from an unarmed one". Its
commit says: "Pushing where the forge reports no pull request open on the
branch is filed as `PL-62V1` rather than built, under the generator pause."

**Premise confirmed by reading, 2026-09-26, against `78b1a02b`.**
`claiming._publish` still holds back any push onto a branch the remote has
unless `push` is set (`held_back = bool(remote.tip) and not push`), and nothing
in `claiming.py` asks the forge. Since the capture, `PL-ZLJ9` (#1028) added
`bin/docket claim --push`, which a session passes once it has disarmed
auto-merge. So the second step is now that command rather than a push by hand.
It is still a second step, resting on the session's own reading of the forge.

**Why it matters.** Under the push-first protocol a branch is on the remote
from its first claim, so every rider claimed after that takes the held-back
path. It exits 4, then waits for `claim <id> --push` once the session has made
sure no armed pull request rides the branch. Where the forge says no pull
request is open on the branch, nothing can be armed, and that check is already
answered. The step this spares is also the one a session can forget, which
leaves the rider invisible to every other session, the shape `PL-ZLJ9` exists
for. The forge read exists already. `open_pull_requests_command` lists open
pull requests, `cli._open_pull_requests` asks it for `flight`, and every way it
fails is a skip.

**Done when.** `bin/docket claim` on a branch the remote already has pushes
the claim where the forge answered and names no pull request open on the
branch. It holds the claim back with exit 4, as now, where one is open or the
forge could not be asked. A real-git test in
`subprojects/docket/tests/test_claiming.py` with a fake forge holds all three.

**Held by the generator pause, triage 2026-09-26.**
- It is a new mechanism, not a fix to existing behaviour. It adds a forge read
  to `claim`, which has none, to spare a step the current behaviour already
  gets right: exit 4 is the correct answer for a claim left local (`PL-1X56`),
  and `--push` publishes it.
- It is not work on a generator either. Whether a pushed branch has an open
  pull request is not the fact any live head names.
- `blocked-by` names the seven items carrying `generator: live` that day,
  `PL-MT3R` among them. Before unblocking, check that `bin/docket generators`
  marks no head "still generating", rather than this list. A request from the
  project owner lifts the pause for this item (`PL-6Q9L`).

**Generator check.** Not a misreading. `claim` reads correctly what it asks,
and this item asks it to read one thing more. It belongs with `PL-1X56`, whose
close-out captured it.
