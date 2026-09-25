---
id: PL-8Z1T
title: vcs.fetch_remote discards git fetch's exit status and cmd_branch and cmd_stranded pass fetched=not no_fetch, so after a failed fetch branch prints 'current with origin/main' and stranded prints recover lines with no staleness caveat - the session-start digest's first line reads fresh when the fetch failed
status: untriaged
feature: one-snapshot
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-25
---

**Problem.** vcs.fetch_remote discards git fetch's exit status and cmd_branch and cmd_stranded pass fetched=not no_fetch, so after a failed fetch branch prints 'current with origin/main' and stranded prints recover lines with no staleness caveat - the session-start digest's first line reads fresh when the fetch failed

Reproduced in the simulation (scenario k: origin unreachable after a merge) and in an offline clone with origin/main one commit stale: `branch` says `current with origin/main (1 ahead).`; `branch --no-fetch` correctly adds "Read from the last fetch". `arm`, `claim` and `cli.py:1106` check the status and answer unknown. PL-39B7 added the caveat for `--no-fetch` only; this is PL-XLQ5's incident shape.

**Why it matters.** A confident wrong answer about freshness at the first line a session reads; recovery advice from stale refs is the PL-KBFN loss path.

**Done when.** One fetch helper whose result every command reads; a failed fetch prints what `--no-fetch` prints; a test runs `branch` and `stranded` against an unreachable origin.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
