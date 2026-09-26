---
id: PL-HY56
title: docket concurrent --limit 0 or a negative limit offers a one-item batch instead of refusing the value, the off-by-one PL-RMN8's brief recorded and left outside its done-when
priority: P3
effort: S
status: ready
classes: defect
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the 2026-09-26 triage pass
added: 2026-09-26
payoff: concurrent answers a zero or negative --limit with a refusal instead of a one-item batch that reads as a real answer
verify: grep -q 'def test_concurrent_refuses_a_limit_below_one' subprojects/docket/tests/test_cli.py
---

**Problem.** docket concurrent --limit 0 or a negative limit offers a one-item batch instead of refusing the value, the off-by-one PL-RMN8's brief recorded and left outside its done-when

**Found 2026-09-26** while closing `PL-RMN8` (next refuses a `--limit` below
one). On `origin/main` at `cfa51ff3` plus that branch, `bin/docket concurrent
--limit 0` and `bin/docket concurrent --limit -1` both print "A batch that can
be worked at once (1 items, best-first)" at exit 0. `PL-RMN8`'s brief noted
this as "off by one rather than false" and scoped only `next`, whose `--limit`
now goes through `cli._at_least_one`; `concurrent`'s is still a bare
`type=int, default=None`.

**Why it matters.** A zero or negative count cannot be honoured, and answering
one with a batch of one reads as a real answer. Lower stakes than `next`'s,
since the output is never "nothing to do".

**Reproduced 2026-09-26 against 78b1a02b.** `bin/docket concurrent --limit=0` and `--limit=-1` both print "A batch that can be worked at once (1 items, best-first):" and exit 0. `cli.py:4716` still reads `concurrent.add_argument("--limit", type=int, default=None)`, where `next`'s goes through `_at_least_one` (`cli.py:4676`).

**Done when.** `bin/docket concurrent --limit` goes through `cli._at_least_one` as `next`'s does, so a zero or negative count is refused when the arguments are parsed, with its message. A test in `subprojects/docket/tests/test_cli.py` holds it.

**Generator check.** One-off sibling of `PL-RMN8` (closed 2026-09-26), known when it closed: its brief recorded this and scoped `next` alone. The fact, which counts a `--limit` accepts, is already one function, `cli._at_least_one`, which `concurrent`'s flag does not use. No head's `misread:` states it.
