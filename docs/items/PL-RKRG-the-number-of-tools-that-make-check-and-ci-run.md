---
id: PL-RKRG
title: The number of tools that make check and CI run under uv run python is written as a word in six comments and docstrings (Makefile twice, quality.yml twice, docs/apparatus.md twice, test_tools_portability.py), so each new tool must update every copy by hand
priority: P3
effort: S
status: done
classes: defect
feature: one-source-of-truth
milestone: v0.6.15
touches: Makefile, .github/workflows/quality.yml, docs/apparatus.md, tests/unit/test_tools_portability.py
deferred-from: v0.7.0 - captured after the freeze, and not safety or science
added: 2026-11-03
closed: 2026-11-03
pr: 1997
payoff: the comments beside the gates stop describing a tool count that is already wrong in three places, and the next tool added needs no hand edits to stay true
verify: ! grep -qiE '\b(eight|nine|ten|eleven) (of them|tools|lines)|(other|these|same) (eight|nine|ten|eleven)\b' Makefile .github/workflows/quality.yml tests/unit/test_tools_portability.py && ! grep -qE 'Ten of them|other nine' docs/apparatus.md
---

**Problem.** The number of tools that make check and CI run under uv run python is written as a word in six comments and docstrings (Makefile twice, quality.yml twice, docs/apparatus.md twice, test_tools_portability.py), so each new tool must update every copy by hand

**Reproduced 2026-11-03.** `make check` and `.github/workflows/quality.yml`
each run 11 tools only under `uv run python`, nine of them because they parse
source written for Python 3.14. Three of the prose copies already disagree with
those lists. `quality.yml` says "the eight tools further down" in the floor
section's `fact_home_check.py` comment, and "the eight lines after them" above
`branch_id_check.py`, where nine follow. `docs/apparatus.md` says "Ten of them
are nonetheless *invoked* only under `uv run python`", where the lists give 11.
The copies that say nine are in the `Makefile` (twice), `quality.yml` (three
times), `docs/apparatus.md` ("The other nine") and the docstring of
`tests/unit/test_tools_portability.py`. `PL-40SJ`'s work raised these counts by
hand from seven to eight. Two of the copies still say eight now that nine
tools are in the group.

**Why it matters.** A reader who trusts a comment's count reads a wrong
description of what the gates run. Each new tool in the group has to find and
change every copy by hand, and `doc_check.py` deliberately reads no count
written in prose, so nothing says when one is missed.

**Done when.** No comment or document states how many tools are in the
`uv run python` group, or how many lines follow, as a number. Each refers to
the group by what it is, such as "the tools on the lines below", or names the
tools. The `Makefile` and `quality.yml` lists stay the only record of the group.

**Generator check.** An instance of the fact `PL-G424` states (the link between
a document sentence and the tree fact it restates), filed after it closed. It
is not `PL-40SJ`'s fact, the value of a named constant. No constant holds this
count, and `PL-40SJ`'s brief sends prose that restates a number to `PL-G424`'s
family. No `reenters:` is recorded, because `PL-G424`'s fix deliberately leaves
counts in prose to judgment. Feature `one-source-of-truth` works it.

**Done 2026-11-03.** Every count of the group is gone from the four files.
The names of the tools stay in `docs/apparatus.md`, because
`tools/config_home_check.py` already compares that list with the `Makefile`'s
`uv run python` lines, so a tool added to one and not the other fails
`make check`. The test docstring's list had no such check, so it now names two
tools as examples and points at the lines.
