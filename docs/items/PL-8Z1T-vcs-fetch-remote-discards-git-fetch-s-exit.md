---
id: PL-8Z1T
title: vcs.fetch_remote discards git fetch's exit status and cmd_branch and cmd_stranded pass fetched=not no_fetch, so after a failed fetch branch prints 'current with origin/main' and stranded prints recover lines with no staleness caveat - the session-start digest's first line reads fresh when the fetch failed
priority: P2
effort: S
status: done
classes: defect, infra
feature: one-snapshot
milestone: v0.5.12
touches: subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_vcs.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; triaged 2026-09-25 with the one-snapshot batch
added: 2026-09-25
closed: 2026-09-26
pr: 1054
payoff: a session whose fetch failed is told its branch was read from the last fetch instead of 'current with origin/main', before it builds on a base that moved or a release guard reads stale refs
verify: grep -q 'def test_branch_after_a_failed_fetch_says_it_read_the_last_fetch' subprojects/docket/tests/test_cli.py
---

**Problem.** vcs.fetch_remote discards git fetch's exit status and cmd_branch and cmd_stranded pass fetched=not no_fetch, so after a failed fetch branch prints 'current with origin/main' and stranded prints recover lines with no staleness caveat - the session-start digest's first line reads fresh when the fetch failed

Reproduced in the simulation (scenario k: origin unreachable after a merge) and in an offline clone with origin/main one commit stale: `branch` says `current with origin/main (1 ahead).`; `branch --no-fetch` correctly adds "Read from the last fetch". `arm`, `claim` and `cli.py:1106` check the status and answer unknown. PL-39B7 added the caveat for `--no-fetch` only; this is PL-XLQ5's incident shape.

**Why it matters.** A confident wrong answer about freshness at the first line a session reads; recovery advice from stale refs is the PL-KBFN loss path.

**Done when.** One fetch helper whose result every command reads; a failed fetch prints what `--no-fetch` prints; a test runs `branch` and `stranded` against an unreachable origin.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).

Re-confirmed 2026-09-25 against 46954a81, in a scratch clone with `origin` unreachable and `origin/main` one commit stale: `branch` printed `current with origin/main (1 ahead).` and exited 0 with no caveat, while `branch --no-fetch` added `Read from the last fetch; nothing refreshed origin/main for this answer.` `fetch_remote` (vcs.py:2000) still returns `None`, and `release` calls it unchecked too (cli.py:3030), ahead of the parallel-cut guard whose own comment calls the fetch "the part without which none of these is worth asking".

**Generator check.** PL-XBV4's fact, how fresh the refs a read answered from are, read wrong after a fetch whose failure nothing records. It is also PL-9RFP's mechanism, a git call's failure discarded (done 2026-09-23, spent), at a runner that head's fix did not name; recorded here rather than reopening it.

**Closed 2026-09-26 with `PL-XBV4`.** `vcs.fetch_remote` returns a `Fetch`
whose outcome is read off git's exit status, and reads `FETCH_HEAD`'s date
before it tries, since a failed fetch truncates it. `branch` and `stranded`
take their `fetched` from the one snapshot, and a failed fetch prints
`format_snapshot`'s sentence naming the failure and the moment the refs are
really from. `test_branch_after_a_failed_fetch_says_it_read_the_last_fetch`
runs both against an unreachable origin. `release` goes through the same
snapshot and prints the same line.
