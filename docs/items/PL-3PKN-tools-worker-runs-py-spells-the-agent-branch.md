---
id: PL-3PKN
title: tools/worker_runs.py spells the agent branch prefix again as BRANCH_PREFIX = "claude/" beside docket.claims.AGENT_BRANCH_PREFIX, which fact_home_check passes because a plain string under two names is not compared and claude/ names no path in the tree
priority: P2
effort: S
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.8
touches: tools/worker_runs.py, tools/fact_home_check.py, tests/unit/test_fact_home_check.py, docs/apparatus.md
added: 2026-10-25
closed: 2026-10-25
pr: 1810
payoff: a module-level string bound under a second name in another apparatus module fails make check, unless DISTINCT_WORDS records the two as different facts
verify: uv run pytest -q tests/unit/test_fact_home_check.py -k 'string_bound_under_two_names or distinct_word' && python3 tools/fact_home_check.py
reenters: PL-S08Z
---

**Problem.** tools/worker_runs.py spells the agent branch prefix again as BRANCH_PREFIX = "claude/" beside docket.claims.AGENT_BRANCH_PREFIX, which fact_home_check passes because a plain string under two names is not compared and claude/ names no path in the tree

**What was done.** `tools/worker_runs.py` now imports
`docket.claims.AGENT_BRANCH_PREFIX` and binds no prefix of its own.

The shape is fixed in `tools/fact_home_check.py` rule 2. A plain string bound
under two names in two modules is now a finding, `same string`, just as a call
or a repository path already was. The syntax cannot tell one fact from two
facts that happen to share a word, so `DISTINCT_WORDS` records each string
that is deliberately bound under several names, with every name and the
reason. A new name binding one of those strings is a finding. A listed name
that no longer binds it is reported as a stale entry.

**The count, before choosing.** On `main` at `b6ff4443` on 2026-10-25, nine
strings were bound under different names in two or more modules. One was this
copy. The other eight were different facts sharing a word: `"landed"`,
`"closed"`, `"behind"`, `"unplaced"`, `"apparatus"`, `"code"`, `"unreadable"`
and the em dash. Most of them already carried a `PL-LGDV` comment saying so.
Those eight became the table's entries, so the rule cost eight lines of
recorded decisions and refuses the next copy. A length threshold could not
separate the copy from the coincidences, since `"claude/"` has seven
characters and `"unplaced"` has eight. Numbers and tuples were measured too
and are not compared. Seventeen numbers are shared by coincidence, such as
timeouts of 120 seconds. Two tuples are shared, and one of them, `(".py",
".pyi")` in `docket.verify` and `tools/doc_check.py`, may be one fact, so it
is filed on its own.

**Generator check.** This is the third form of one misread fact in rule 2:
one value bound under two names is one fact, whatever kind of value it is.
`PL-MM3Q` compared calls, `PL-S08Z` added repository paths, and this item adds
plain strings. It is recorded as `reenters: PL-S08Z`, closed today. Numbers,
tuples and f-strings are still not compared, for the reasons measured above.
