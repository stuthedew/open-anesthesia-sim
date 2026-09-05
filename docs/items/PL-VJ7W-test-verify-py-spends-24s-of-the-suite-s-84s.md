---
id: PL-VJ7W
title: test_verify.py spends 24s of the suite's 84s serial cost sleeping, and sets the parallel floor
priority: P3
effort: M
status: needs-decision
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/tests/test_verify.py
added: 2026-09-05
---

**Problem.** `subprojects/docket/tests/test_verify.py` runs 24.0 s serially,
measured 2026-09-05, against 37.4 s for all of `subprojects/docket/tests` and
84 s for the whole suite. Nearly all of it is deliberate: the file's fixtures
give items `verify:` commands like `sleep 5`, `sleep 4`, `sleep 2` and
`sleep 30`, because what is under test is cost reporting and the timeout - the
`slow`, `slowest`, `typical`, `serial` and `timed_out` fields of `LandedReport`.

Its slowest single test, `test_the_named_commands_come_worst_first`, is 4.08 s,
the slowest in the repository. Under any parallel run one test that long is a
floor contributor: with the suite at 84 s serial over four workers the
arithmetic floor is 21 s, and 4.08 s of that is one test nobody can split.

**Why it matters.** It is the second-largest concentration of wall clock after
the parallelism question in `PL-VZ8P`, and unlike that one it is real work being
done rather than scheduling. It also compounds with `PL-VZ8P`: shortening these
lowers the floor that oversubscription is working around.

**Where.** `subprojects/docket/tests/test_verify.py`, the `sleep` durations at
roughly lines 513-766.

**Decision needed.** Which is why this is `needs-decision` rather than `ready`.
Whether the margins can be cut is a judgment about flake risk, not a
measurement. The durations are generous on purpose: several assertions compare
one command's cost against another's, and `dominant` reads the *ratio*, so the
gap has to stay well above scheduler noise on a loaded box - which is exactly
what a `make check` run is. Halving every sleep would halve the file and might
buy 10 s of serial time; it might also produce a suite that fails once a
fortnight for no reason, which is a far worse outcome than 24 s. `sleep 30` is
the safe subset: those tests assert a kill at a *limit* the test itself sets, so
the 30 is never waited out and shortening it changes nothing.

Do not take this item as a licence to trim until something breaks. It wants
someone to work out which sleeps are load-bearing ratios and which are only
"comfortably longer than zero", and shorten the second kind alone.

**Done when.** Either the file's serial cost is materially below 24 s with the
timing assertions still meaningful and no new flakiness across repeated runs, or
the item is dropped with the reasoning that the margins are load-bearing.
