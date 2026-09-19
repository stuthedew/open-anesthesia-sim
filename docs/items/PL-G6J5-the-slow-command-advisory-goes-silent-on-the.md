---
id: PL-G6J5
title: The slow-command advisory goes silent on the pool the widened scope produces, because a scope full of test-suite commands has a high median and the 30x ratio never clears
priority: P3
effort: S
status: done
classes: infra
feature: verify-replay-cost
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_verify.py, subprojects/docket/tests/test_checks.py, subprojects/docket/README.md
added: 2026-09-17
closed: 2026-09-19
verify: grep -q 'def test_the_costliest_command_is_named_and_held_to_no_threshold' subprojects/docket/tests/test_checks.py && ! grep -q '_check_slow_commands' subprojects/docket/src/docket/checks.py
---

**Problem.** The slow-command advisory goes silent on the pool the widened scope produces, because a scope full of test-suite commands has a high median and the 30x ratio never clears

**Where it comes from.** `_check_slow_commands` names a command that is
`SLOW_COMMAND_RATIO` (30x) above the *median* of the pool it ran in. Its own
docstring records the gap — the advisory "fires on an outlier against the
median and is silent on a store where everything is uniformly heavy, which is
precisely the store whose margin is closing" — and `_note_cost` names the
slowest command on every run for that reason.

**`PL-XMNC` made that store the ordinary case rather than the pathological
one.** The widened scope selects items by the files their commands read, and
the commands that read a test directory are test-suite commands, so a narrowed
pool is now systematically composed of the heavy end of the store rather than a
sample of it. The median rises with the pool and the ratio never clears.

**Why it matters.** The advisory is the only thing that names a command whose
cost is out of proportion to the rest, and it now goes quiet in exactly the case
it was built for. That is `CLAUDE.md`'s "a check earns its place every run" read
from the other side: a check that cannot fire where the problem is is not
coverage, and leaving it in place costs attention on every run while proving
nothing. `PL-8T83` is the instance it failed to name.

**Measured 2026-09-17** on `claude/kind-bardeen-11q5uh`: 29 commands, 92.5 s
wall, 535.6 s serially, slowest `PL-M26Q` at 62.6 s — a command taking 68% of
the run's wall clock, and no advisory naming it. On the whole-store sweep the
same command would be an outlier against a 0.65 s median and would be named.

**Decision needed.** Whether the ratio should be taken against the
*store's* median rather than the pool's, which would make the advisory
scope-independent and is one line; or whether `_note_cost`'s slowest-command
line is already the whole answer and this advisory should be retired on
`CLAUDE.md`'s "a check earns its place every run, or it is retired". Count what
the advisory has caught that the cost line did not before choosing.

**Done when** the advisory names a command that is setting a scoped run's floor,
or it is dropped with the count recorded.

## Answered 2026-09-19: dropped, and the count

**The advisory has caught nothing the cost line did not, and the store-median
variant this item proposed would catch nothing either.** Both halves measured
on this checkout the same day, 179 candidate commands at eight workers.

**1. Nothing filed on its evidence since the cost line existed.** `_note_cost`
landed 2026-09-03 (`PL-9NKK`), the day after the advisory (`PL-VG7G`,
2026-09-02, when it was the only signal there was). In the sixteen days since,
no item in the store cites the advisory's output. The two that quote it are its
own creation and `PL-FRGP`, a defect in its own wording. Over the same span the
cost line's figures are the evidence in `PL-VJ7W`, `PL-8T83` and this item.

**2. It fires on nothing that occurs.** Replayed against the scope
`items_reading` computes for each of the last twenty-five merges into `main`:

| rule | pools it fires on | whole store |
| --- | --- | --- |
| ratio against the pool's median (today) | **0 of 13** | nothing |
| ratio against the *store's* median (this item's proposal) | **0 of 13** | nothing |

The whole store holds a 67.4 s command while this is true.

**3. The reason is structural, and the ratio is one month of growth from being
mathematically dead.** The threshold was calibrated when the typical `verify:`
was a `grep`; it is now `uv run pytest <file>`.

| | 2026-09-02 | 2026-09-19 |
| --- | --- | --- |
| commands in the pool | 46 | **179** |
| median command | 0.65 s | **3.65 s** |
| serial total | 34 s | **1458 s** |
| slowest command | 8.95 s | **67.4 s** |
| the bar, at 30x | ~20 s | **109.5 s** |

`LANDED_TIMEOUT` is 120 s and a command over it is killed and kept out of the
median, so **once the median passes 4.0 s no command can clear the bar at all.**
It is 3.65 s. Some scoped pools are already past it: the pool for a branch
touching `docs/WORKING_NOTES.md` has a 4.29 s median and a 128.6 s bar.

**4. And the silence is the right answer rather than a tuning failure.** 1458 s
of serial work across eight workers is a 182 s floor against 204 s elapsed, so
no single command is what the run waits for — the queue is. That is `PL-FRGP`'s
correction taken to its conclusion.

**5. A replacement was measured and refused.** Naming the commands that stand
above the throughput floor the rest imposes — scope-independent, no median,
reusing the bound arithmetic already there — fires on 5 of 13 pools, but at
least 2 of those 5 are unactionable: five ~30 s commands already narrowed to
one test file, and three ~4 s commands in a 5 s run. A share-of-floor test at
25% fires on 13 of 13 and named 20 commands on one pool.

**Where the cost actually is**, and what no per-command outlier test can
express: three test files carry **59% of the 1458 s**, each re-run by every
item whose command names it — `subprojects/docket/tests/test_cli.py` 415 s
across 14 items, `tests/unit/test_doc_check.py` 292 s across 12,
`subprojects/docket/tests/test_verify.py` 152 s across 4. Filed as `PL-FZ58`.

**What changed.** `_check_slow_commands` and its tests are gone, as are
`LandedReport.slow`, `LandedReport.typical`, `SLOW_COMMAND_RATIO` and
`SLOW_COMMAND_FLOOR`. `_note_cost` is the whole of the project's answer on cost
and its docstring now says so. The numbers above are recorded in `verify.py`'s
constants block and in `subprojects/docket/README.md`, so the next session
reading either finds the count rather than the retired rule.

Dropping the tests that slept through the ratio's thresholds took
`subprojects/docket/tests/test_verify.py` from **31.5 s to 23.4 s**, measured
either side of the change — the file `PL-VJ7W` was filed about.

