---
id: PL-QPJZ
title: Add `bin/docket trend` so the workflow-to-product balance over time is a command rather than a session's derivation
status: done
priority: P2
effort: M
classes: infra, session-cost
feature: dev-tooling
touches: subprojects/docket/src/docket/trend.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/config.py, subprojects/docket/tests/test_trend.py, subprojects/docket/tests/test_cli.py, subprojects/docket/README.md
verify: uv run pytest subprojects/docket/tests/ && grep -q 'def test_trend' subprojects/docket/tests/test_cli.py
added: 2026-09-07
closed: 2026-09-07
---

**Problem.** Asked how the balance of workflow work to product work had moved
over time, a session had no command to run. Every `bin/docket` subcommand
describes the project as it stands — `status` by feature, `wave` by the
release cadence, `next` by what to do now — and none of them looks backwards.
Answering it meant importing `Item.lane`, bucketing every item in the store by
`added` and `closed`, and cross-checking the result against `git log
--numstat` classified by `workflow_paths`, by hand, at full context.

**Why it matters.** The answer is a pure function of the item store and the
git history, so this is the case `CLAUDE.md`'s "Prefer deterministic tooling
over repeated model work" names outright: work moved out of the model is paid
for once and then runs free, while work left in it is re-derived at full
context by every session that gets asked. It is also the shape where a
hand-rolled answer is most likely to be quietly wrong — the classification
rule lives in `Item.lane`, and a session reimplementing it in a throwaway
script can reach a different answer than `docket next product` would, with
nothing to catch the divergence.

**Where.** A new `subprojects/docket/src/docket/trend.py` holds the report;
`vcs.py` gains the `git log --numstat` reader beside the other git wrappers;
`cli.py` and `render.py` gain the subcommand and its table; `config.py` gains
`code_paths`, which is what separates the product's source from prose written
about it. `Item.lane` and `is_under` are reused rather than reimplemented,
which is what makes the trend and the lanes answer with one rule.

**Done when.** `bin/docket trend` prints closed items, effort-weighted
closures and churn side by side, per period, with `crossing` and `unplaced`
kept in their own columns; the queue store is reported but excluded from the
churn share; the command refuses a project with no `workflow_paths` rather
than answering from the whole tree; and it runs from a bare checkout with no
virtualenv.

**Not this.** No verdict on whether the balance is right — the command prints
counts and decides nothing, exactly as `wave` does. Not wired into `make
check` or the session-start digest either: it answers a question asked
occasionally, and a check that fires every run without changing a decision is
a defect in the check.
