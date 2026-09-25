---
id: PL-D1P5
title: next, show and the session-start digest never fetch and print nothing about the age of the refs they read - PL-QSGX's flight defect in three more commands
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** next, show and the session-start digest never fetch and print nothing about the age of the refs they read - PL-QSGX's flight defect in three more commands

Reproduced in the simulation (k, b): a stale `flight` reports merged work as live; `next` offers an item merged as done; `show` says ready. PL-QSGX names `flight` only.

**Why it matters.** Every stale read looks exactly like a fresh one.

**Done when.** Each command either reads after the snapshot's fetch or prints the age of the refs it read; decided together with PL-QSGX.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` on `claude/upbeat-heisenberg-27vafn` (PL-P0FP).
