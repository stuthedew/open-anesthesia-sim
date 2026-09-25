---
id: PL-D1P5
title: next, show and the session-start digest never fetch and print nothing about the age of the refs they read - PL-QSGX's flight defect in three more commands
priority: P2
effort: M
status: ready
classes: defect, infra
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
payoff: next, show and the digest say when what they read is stale, so a session is not handed an item another session claimed since its last fetch as free to start
verify: grep -q 'def test_next_show_and_digest_do_not_read_unfetched_refs_as_fresh' subprojects/docket/tests/test_cli.py
---

**Problem.** next, show and the session-start digest never fetch and print nothing about the age of the refs they read - PL-QSGX's flight defect in three more commands

Reproduced in the simulation (k, b): a stale `flight` reports merged work as live; `next` offers an item merged as done; `show` says ready. PL-QSGX names `flight` only.

**Why it matters.** Every stale read looks exactly like a fresh one.

**Done when.** Each command either reads after the snapshot's fetch or prints the age of the refs it read; decided together with PL-QSGX.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

Reproduced 2026-09-25 against 46954a81, in scratch clones: one clone claimed and pushed `PL-HMZZ`; in a second, before a fetch, `next` still offered `PL-HMZZ` first, `show` and `flight` said nothing of the claim, and none of the three said how old its refs were; after `git fetch`, `next` listed it under `Excluded, already in flight`. Only `branch`, `stranded` and `release` call `fetch_remote`, and `new`, `claim` and `arm` fetch through `claiming._git`. The session-start hook runs `bin/docket branch --brief`, which fetches, just ahead of `digest`, so the digest is fresh at session start unless that fetch failed (PL-8Z1T), and stale on any later run.

**Generator check.** PL-XBV4's fact: refs of unknown age read as current.
