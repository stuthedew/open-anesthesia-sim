---
id: PL-QSGX
title: bin/docket flight never fetches, unlike stranded and branch, so it reports refs as old as the clone - the one command whose whole job is reading other sessions' branches
priority: P2
effort: S
status: done
classes: defect, infra
feature: refresh-before-reporting
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-19
closed: 2026-09-26
verify: grep -q 'def test_flight_fetches_by_default' subprojects/docket/tests/test_cli.py && uv run pytest subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket flight never fetches, unlike stranded and branch, so it reports refs as old as the clone - the one command whose whole job is reading other sessions' branches

**Why it matters.** `flight` is the command whose whole job is reporting what
*other sessions' branches* hold, and it is the one that reads them without
asking the remote. `cmd_stranded` and `cmd_branch` both call `fetch_remote`
before they read; `cmd_flight` (`subprojects/docket/src/docket/cli.py:1774`)
does not, so its answer is as old as the last fetch this checkout happened to
make. A session that runs it to decide whether an item is claimed gets a clean
answer from stale refs, which is the exact shape the `docket` skill warns
about under **Mode: start an item** - "Without a fetch the answer is as old as
the clone."

**Found 2026-09-19** while refreshing for a closing block, after the project
owner asked for refresh-before-reporting to be the default. It is the
deterministic half of that request: with this fixed, the rule shrinks from
"remember to fetch first" to naming the command.

**Where.** `subprojects/docket/src/docket/cli.py`, `cmd_flight`. Follow
`cmd_stranded`'s shape exactly - fetch unless `--no-fetch`, and say in the
report which of the two happened, so a bare or offline checkout still answers.

**Done when.** `bin/docket flight` fetches by default, takes `--no-fetch` like
its siblings, says which it did, and a test pins both directions.

**Closed 2026-09-26 with `PL-XBV4`.** `flight` fetches by default through
`cli._snapshot`, as every read command now does, takes the shared `--no-fetch`,
and says which happened on the refs line.
`test_flight_fetches_by_default_and_says_when_told_not_to` pins both
directions, and the census holds every other read command to the same.
