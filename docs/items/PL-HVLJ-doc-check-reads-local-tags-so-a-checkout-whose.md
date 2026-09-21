---
id: PL-HVLJ
title: doc_check reads local tags, so a checkout whose tags were fetched ahead of its working tree errors on a clean main - observed 2026-09-21 as 'git holds v0.4.35, but no row of the version table marks v0.4.35 completed' when the row and the tag are the same commit
status: untriaged
added: 2026-09-21
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
