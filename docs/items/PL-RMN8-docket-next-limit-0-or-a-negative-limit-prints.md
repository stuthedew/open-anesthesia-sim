---
id: PL-RMN8
title: docket next --limit 0 (or a negative limit) prints 'Nothing is ready to start' while work is startable, because the limit slices the ranking to nothing rather than being refused
priority: P3
effort: S
status: ready
classes: defect, infra
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the first 2026-09-23 triage pass
added: 2026-09-22
payoff: docket next stops telling a session nothing is ready to start when it was only asked for zero picks, so a zero or negative limit fails loudly instead of ending a session's search for work
verify: grep -q 'def test_next_refuses_a_limit_below_one' subprojects/docket/tests/test_cli.py
---

**Problem.** docket next --limit 0 (or a negative limit) prints 'Nothing is ready to start' while work is startable, because the limit slices the ranking to nothing rather than being refused

**Reproduced 2026-09-23.** `bin/docket next` lists three picks. `bin/docket
next --limit 0` prints "Nothing is ready to start." and "19 untriaged item(s)
are waiting", exit 0. A negative limit is worse than the title says, because it
slices from the end: `--limit -2` prints 270 picks, the whole ranking but its
last two, and only `--limit -1000` empties it into "Nothing is ready to start."
`--oldest` shares the fault. There `--limit 0` says "No owed work is ready to
start." over a malformed "Waiting on a decision, oldest first (40): , and 40
more", and `--limit -2` prints 738 lines. Both rankings slice with the bare
`type=int` value, in `plan.recommend` (`ranked[:limit]`) and
`plan.longest_waiting`. `concurrent --limit 0` returns one item rather than
none, so it is off by one rather than false.

**Why it matters.** `docket next` is the command that decides whether a session
has work, and "Nothing is ready to start" is the answer that ends the search.
Many command-line tools read a zero limit as "no limit", so `--limit 0` is a
plausible way to ask for the whole ranking. It answers with a false statement
at exit 0 instead of an error.

**Done when.** `bin/docket next --limit N` with N below 1 exits non-zero with a
message naming the flag, on the default path and under `--oldest`, and never
prints "Nothing is ready to start" while the ranking holds work.
`test_next_refuses_a_limit_below_one` in `subprojects/docket/tests/test_cli.py`
drives 0 and a negative value.

**Generator check.** A one-off. `--limit` is a bare `type=int` passed straight
into a slice, and `PL-Q89J`'s `--oldest` ranking inherited the slice, which is
how its session came to file this. No head names unvalidated arguments, and no
open item shares the mechanism.
