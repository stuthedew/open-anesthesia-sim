---
id: PL-HVLJ
title: doc_check reads local tags, so a checkout whose tags were fetched ahead of its working tree errors on a clean main - observed 2026-09-21 as 'git holds v0.4.35, but no row of the version table marks v0.4.35 completed' when the row and the tag are the same commit
priority: P2
effort: S
status: done
classes: defect, infra
feature: tag-error-names-its-cause
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/items/PL-LT77-git-fetch-tags-does-not-prune-so-a-tag-deleted.md
added: 2026-09-21
closed: 2026-09-26
pr: 1063
payoff: a checkout that is merely behind is told to pull, instead of being told a correct ROADMAP.md is wrong and to fix it before committing
verify: grep -q 'def test_a_tag_ahead_of_the_working_tree_names_its_own_remedy' tests/unit/test_doc_check.py
---

**Problem.** doc_check reads local tags, so a checkout whose tags were fetched ahead of its working tree errors on a clean main - observed 2026-09-21 as 'git holds v0.4.35, but no row of the version table marks v0.4.35 completed' when the row and the tag are the same commit

**Observed 2026-09-21**, by the project owner in a warm local clone, running
the command this session handed them to settle `PL-7H9Y`:

```
Errors (the documentation is wrong; fix before committing):
  ROADMAP.md: git holds v0.4.35, but no row of the version table marks v0.4.35
  completed; a release that shipped is one this table has to name
```

**The documentation is not wrong.** `ROADMAP.md:98` carries
`| v0.4.35 | Completed / current baseline | ... |` on `origin/main` and on
every branch forked from it, and `python3 tools/doc_check.py check` reports
`0 errors` in a checkout holding both the tag and that row.

**Where.** `tools/doc_check.py:2620-2627`, the final loop of the release-tag
check: for each tag git holds, error unless the parsed version table marks that
version completed. The tag set comes from local `git tag`; the table comes from
the working tree. Those two move independently - `git fetch --tags` updates the
first and not the second - so a clone that fetched tags without moving its
branch fails a check about a file that is correct.

**Why this instance is exact.** The `v0.4.35` row was added by `cce6f28c`,
which is the commit the `v0.4.35` tag points at (`PL-F1SZ`, #778). Tag and row
are therefore the *same* commit, so the window in which the tag exists and the
row does not is precisely "tags fetched, tree not updated" - the state
`git fetch --tags` leaves behind on its own.

**Why it matters.** The error text says "the documentation is wrong; fix before
committing", which is a false accusation against a correct file, and the remedy
it implies is a documentation edit. The remedy is `git pull`. A session that
believed the message would edit `ROADMAP.md` to satisfy a check about its own
staleness.

**Neighbours, and why this is filed separately rather than onto one of them.**
`PL-LT77` is the same *class* - `doc_check` reading local tags, with nothing
distinguishing stale local state from a real repository fault - but the
opposite direction: a tag *deleted* on origin that lingers locally. `PL-PNW6`
is a withdrawn tag re-cut at the same number. This is the third direction, a
tag arriving *ahead* of the tree, and it is the one that fires on a completely
healthy repository. Whoever takes any of the three should read the other two;
they may well be one fix.

**Done when.** A tag git holds for a version the working tree's table does not
name is reported as a checkout that is behind - naming `git pull` as the remedy
- rather than as an error against `ROADMAP.md`; and a test in
`tests/unit/test_doc_check.py` drives a tag set that is ahead of the tree it is
read against.

**Closed 2026-09-26.** `check_tags` asks `_ahead_of_the_tree` which of the tags
the version table does not name the default branch holds and `HEAD` does not,
and declines those as a checkout that is behind: "git holds v0.4.35, which
origin/main has and this checkout's HEAD does not, so the working tree predates
that release rather than leaving it out of ROADMAP.md; `git pull` brings it in
on main, and `bin/docket branch` says how on any other branch". **Done when.**
is read by the problem it states rather than by its first clause alone: taken
literally, every tag the table does not name would read as a checkout behind,
which retires the error for a release whose row really is missing - the case
`test_a_tag_the_version_table_does_not_name_is_an_error` pins. So a tag whose
commit `HEAD` holds keeps the error, and so does one the default branch lacks
too, since no pull brings its row in
(`test_a_tag_the_default_branch_does_not_hold_either_is_still_an_error`). In a
shallow clone a merge base not found may be history never fetched, so the line
says so and names `git fetch --unshallow`. The wording of the error that
remains is `PL-LT77`'s.
