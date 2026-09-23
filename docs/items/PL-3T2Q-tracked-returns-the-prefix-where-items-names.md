---
id: PL-3T2Q
title: _tracked returns the prefix '.' where --items names the repository root itself, which its docstring calls the empty-prefix case
priority: P3
effort: S
status: done
classes: docs
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/tests/test_cli.py
added: 2026-09-21
closed: 2026-09-23
pr: 930
payoff: the next caller written against _tracked's docstring gets the behaviour the docstring describes rather than the opposite one
verify: grep -q 'def test_a_store_at_the_repository_root_is_the_empty_prefix' subprojects/docket/tests/test_cli.py
---

**Problem.** _tracked returns the prefix '.' where --items names the repository root itself, which its docstring calls the empty-prefix case

**Measured 2026-09-21.** Resolving the repository root against itself returns
`.` rather than the empty string, so `--items` naming the root takes the first
branch of `_tracked`'s `try` and never reaches the `ValueError` path the
docstring describes as the empty-prefix case.

**Why it matters.** Nothing misbehaves today, and that is the finding: both
readers of the value happen to be safe in the same direction. `_item_paths_on`
builds its prefix by appending a slash, so `.` becomes `./` and matches no path
git prints; `_queue_only_touches` strips the slashes off and compares against
declared entries, none of which begins with a bare dot. Both therefore withhold,
which is the direction `_tracked`'s own docstring argues for. What is wrong is
that the docstring tells the next reader the value is the empty prefix, and a
third reader written against that sentence - a membership test rather than a
prefix match, where the empty string matches everything and `.` matches nothing
- gets the opposite behaviour from the one described. A wrong statement where a
reader learns the contract, rather than a wrong answer, which is why this is
classed `docs` and sits in the bottom band.

**Done when.** The two cases `_tracked`'s docstring treats as one return the
same value, or the docstring names `.` as the repository root's own answer and
says what relies on it; and a test in `subprojects/docket/tests/test_cli.py`
pins whichever it is.
