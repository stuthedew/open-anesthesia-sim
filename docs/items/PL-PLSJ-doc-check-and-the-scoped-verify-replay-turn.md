---
id: PL-PLSJ
title: doc_check and the scoped verify replay turn pull requests red every day - 64 of 391 red runs, rising from W37 - and a 15-log sample splits them in two: branch text quoting a file that does not exist, which make check refuses locally, so the push went out unchecked; and a store-wide rule tripped by main's state at CI time, not by the branch
status: untriaged
feature: fewer-red-runs
touches: .claude/hooks/docket-branch-guard.sh, Makefile
added: 2026-09-27
---

**Measured 2026-09-27** by `PL-JYJJ`'s census:

| Check | Red runs on pull requests | By week (W37, W38, W39) |
|---|---|---|
| `doc_check` | 32 | 3, 8, 21 |
| scoped verify replay | 32 | 5, 10, 14 |
| `docket check` | 9 | |
| `branch_id_check` | 8 | |

A subagent read the logs of 15 of these failures (job ids are in this
session's census). It found two different mechanisms.

**1. Caught by `make check`, but pushed without it.** All 4 `doc_check`
failures in the sample were the branch's own text:

- an item quoting `start.md` or `capture.md` by bare name, which
  `doc_check` cannot resolve; both live under
  `.claude/skills/docket/modes/`;
- an item quoting `CLAUDE.md` for words that file does not contain;
- `ROADMAP.md` citing a path that does not exist.

The one `branch_id` failure was also local: a branch that had claimed no item.
`make check` runs both checks, so each of these went out without it. Three of
the four were item files, which is the capture path, and capture is kept cheap
on purpose.

**2. Red because of `main`, not because of the branch.** All 4 scoped-verify
failures said "PL-X is open but its `verify:` command already passes". In two
of them PL-X was not the branch's own item, so the work had landed on `main`
through another branch. One `docket check` failure read an item "marked done
on `origin/main`" that records no `pr`. `pull_request` runs check the merge
with the current `main`, so these fail on state the branch did not create.

**Options.**

- For mechanism 1, a push guard: `.claude/hooks/` already guards Bash
  commands. It would run `doc_check` and `branch_id_check`, the two checks
  that account for the sampled cases and are fast, before any `git push`.
  Measure their time first. This costs seconds per push, where a red run
  costs a whole fix cycle.
- For mechanism 2, the question is whose failure it is. The check correctly
  reports that the store is inconsistent, but it reports it to a branch that
  can neither cause nor fix it. `PL-85NT` (repository-level breakage visible
  to every session, claimed by none) was dropped on 2026-09-16, and this data
  bears on reopening it.

**Recommendation.** Build the push guard for mechanism 1, since the fix and
the failure sit in the same session. Put mechanism 2 back to the project owner
as a reopening of `PL-85NT`, with these counts.
