---
id: PL-PWH6
title: cmd_trend hands --no-git a bare Churn() rather than saying it asked git nothing, so trend infers 'not asked for' from an empty undeclined reading - a history git answered with no line counts reads the same - and test_cli.py's test_trend_omits_the_churn_columns_when_git_cannot_be_read runs --no-git under the other cause's name
status: untriaged
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/trend.py, subprojects/docket/tests/test_cli.py
added: 2026-09-26
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
