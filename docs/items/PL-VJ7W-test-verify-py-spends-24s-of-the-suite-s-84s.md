---
id: PL-VJ7W
title: test_verify.py spends 24s of the suite's 84s serial cost sleeping, and sets the parallel floor
priority: P3
effort: M
status: done
classes: session-cost, infra
feature: dev-tooling
touches: subprojects/docket/tests/test_verify.py
verify: uv run pytest subprojects/docket/tests/test_verify.py && ! grep -q 'verify="sleep 4"' subprojects/docket/tests/test_verify.py && grep -q 'verify="sleep 0.5"' subprojects/docket/tests/test_verify.py
added: 2026-09-05
closed: 2026-09-05
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

**Closed 2026-09-05. Three sleeps shortened, four kept, and two of the brief's
premises corrected by measuring before touching anything.**

Measured serially with `--durations`, 64 tests: **22.5 s before, 19.9 s after**
(19.81 / 20.11 / 19.86 over three runs). The file's slowest test drops from
4.11 s to 3.11 s.

**What was trimmed, and why each was safe.**

- `test_the_named_commands_come_worst_first`, `sleep 4` to `sleep 3` beside its
  `sleep 2`. The assertion is an *ordering*, so the gap is what carries it, and
  1 s is the same margin the rest of this file uses against a threshold. `sleep`
  cannot return early, so the pair can only be misordered if startup jitter
  exceeds a second.
- `test_the_costliest_command_is_the_one_that_actually_cost_the_most`, `sleep 1`
  to `sleep 0.3`. `slowest` is a maximum held to no threshold at all - unlike
  `slow` - so it only has to beat four commands that take milliseconds.
- `test_the_run_carries_what_it_would_have_cost_serially`, four `sleep 1` to
  four `sleep 0.5`, with `serial >= 4` becoming `serial >= 2`. What is under
  test is that the total is summed while the wall clock is not, and the
  four-to-one ratio is unchanged.

**What was kept, and this is the half the brief was right about.** The three
`sleep 2`s in the `slow`-naming tests are load-bearing against
`SLOW_COMMAND_FLOOR = 1.0`: a command is named slow only at
`max(typical * 30, 1.0)` seconds, so 2 s is exactly the 2x margin over an
absolute floor, and cutting it spends the margin for half a second.

**First correction: `sleep 5` and `sleep 30` cost nothing and were never
candidates.** Every one of them runs under a `timeout=` of 0.2 s or 0.3 s and
is killed there - that is the behaviour under test. They cost 0.2 s each, not
5 s or 30 s, so shortening them saves nothing while spending the margin that
makes the kill unambiguous. The brief called `sleep 30` "the safe subset" to
shorten, which is true and pointless.

**Second correction: only about half the file was ever sleeping.** The five
sleep-driven tests account for 10.5 s of the 22.5 s. The other ~12 s is 59
tests that do not sleep at all, each paying `_repo(tmp_path)`'s five git
subprocesses - roughly 320 git processes across the file. That is now
`PL-W6NY`, filed rather than fixed: a shared fixture is the obvious move and is
not obviously safe, because several tests in this file commit into the
repository they are handed.

**Third correction, and it retires the premise this item was ranked on.** The
brief's second paragraph says this file's slowest test "is the slowest in the
repository" and so a floor contributor. Measured 2026-09-05 on the whole suite
at `-n 8 --dist worksteal`, 1829 tests in 36.6 s, the five slowest are
`test_chart_patching.py` at 6.24 s and 5.41 s, two `test_coupled_dynamics.py`
parameterisations at 3.44 s and 3.36 s, and only then this file at 3.21 s. It
was fifth even before the trim, and the arithmetic floor of a 36 s parallel run
is nowhere near any of them. So no single test here is binding on the wall
clock, and there is nothing further to buy by shortening these.

**Answered rather than referred back**, per the project owner's instruction for
this session to work the CI items. The decision the brief asked for - which
sleeps are load-bearing ratios and which are only comfortably longer than zero
- is answered above by the constant each one is held against, which is a fact
in `verify.py` rather than a judgment: `SLOW_COMMAND_FLOOR` for the ones kept,
nothing at all for the ones cut.
