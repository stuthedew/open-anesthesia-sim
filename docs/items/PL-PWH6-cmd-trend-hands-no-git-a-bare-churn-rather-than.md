---
id: PL-PWH6
title: cmd_trend hands --no-git a bare Churn() rather than saying it asked git nothing, so trend infers 'not asked for' from an empty undeclined reading - a history git answered with no line counts reads the same - and test_cli.py's test_trend_omits_the_churn_columns_when_git_cannot_be_read runs --no-git under the other cause's name
priority: P3
effort: S
status: done
classes: defect
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_cli.py, subprojects/docket/tests/test_trend.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by the second 2026-09-26 triage pass
added: 2026-09-26
closed: 2026-09-26
pr: 1071
payoff: trend's key says churn was not asked for only when --no-git stopped it, and the test a reader takes for the unreadable-git path is named for the --no-git path it actually runs
verify: grep -q 'def test_trend_omits_the_churn_columns_under_no_git' subprojects/docket/tests/test_cli.py && grep -q 'def test_a_history_git_answered_with_no_line_counts_is_not_read_as_not_asked' subprojects/docket/tests/test_trend.py
---

**Problem.** cmd_trend hands --no-git a bare Churn() rather than saying it asked git nothing, so trend infers 'not asked for' from an empty undeclined reading - a history git answered with no line counts reads the same - and test_cli.py's test_trend_omits_the_churn_columns_when_git_cannot_be_read runs --no-git under the other cause's name

**Found 2026-09-26 closing `PL-F5NV`**, whose `touches` stop at `render.py`,
`trend.py` and `test_trend.py`. Only `cmd_trend` knows whether it asked git -
its invocation carries no runner under `--no-git` - and it tells the report
nothing, handing `analyze` a bare `Churn()`. So `trend._churn_reading` infers
the cause from the reading's shape: declined reads as "git could not be read",
and empty and undeclined as "not asked for". A history git answered with no
line counts at all - every commit a merge, empty, or binary-only - reads as not
asked too. Separately, `test_cli.py`'s
`test_trend_omits_the_churn_columns_when_git_cannot_be_read` runs `--no-git`,
so its name now names the cause it does not exercise; its assertions still
hold.

**Why it matters.** The residual reading is contrived: it takes a repository
with almost no history, and there the key's churn line is false. The misnamed
test is the likelier trap, since a session reading it takes `--no-git` for the
unreadable path the key now words differently.

**Done when.** The key names the cause from what `cmd_trend` did rather than
from the shape of an empty reading, and the `test_cli.py` trend test is named
for the cause it runs.

**Generator check.** A one-off: the half of `PL-F5NV`'s work its `touches`
could not reach, filed in that item's closing commit (`2c768de5`, #1051). The
fact is whether git was asked at all. The invocation already holds it once:
`--no-git` is `git` being `None` (`cli.py`, beside `NO_GIT`). `cmd_trend` drops
it into a bare `Churn()`, so `trend._churn_reading` re-derives it from the shape
of an empty reading. It sits next to `PL-9RFP`'s fact, whether a git read
answered or failed, but it is not that fact: a read that was never made did
neither.

**Worked.** Re-confirmed on `e991944d` before starting: `cmd_trend` still
handed `--no-git` a bare `Churn()` and `_churn_reading` still inferred the
cause from its shape. `trend.analyze` now takes `churn: Churn | None`, and
`cmd_trend` passes `None` under `--no-git`, after the `None`-means-not-asked
idiom `checks.py` already uses for the replay. A history git answered with no
line counts now reads as read, so its columns are drawn at zero rather than
the key naming a cause: zero lines is then what git said, and a fourth reading
with its own key line would have been new output. A partial reading with days
in it stays read, as before. `cli.py` loses its now-unused `Churn` import.
The renamed test keeps its body and gains a sentence saying which cause it
runs, and the new test also pins `None` to the not-asked reading.
