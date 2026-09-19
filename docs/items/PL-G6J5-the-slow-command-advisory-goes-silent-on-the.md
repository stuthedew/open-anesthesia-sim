---
id: PL-G6J5
title: The slow-command advisory goes silent on the pool the widened scope produces, because a scope full of test-suite commands has a high median and the 30x ratio never clears
priority: P3
effort: S
status: needs-decision
classes: infra
feature: verify-replay-cost
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-17
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

