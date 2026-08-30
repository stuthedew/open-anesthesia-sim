---
id: PL-ZRFC
title: '`make docket` is a phony target with no recipe, so it silently succeeds without validating the store'
status: untriaged
added: 2026-08-30
---

**Problem.** `Makefile` line 1 lists `docket` in `.PHONY`, and the target that
actually runs `bin/docket check` is called `punch-list` — the rename never
reached it. `make docket` therefore prints "make: Nothing to be done for
'docket'" and **exits 0**. Both `CLAUDE.md` ("`make docket` after editing the
store — it gates `make check` and CI, and its errors mean an item is about to
be silently wrong") and the docket skill ("`make docket` is the same
validation, wired into `make check`") tell sessions to run it.

**Why it matters.** A check that reports success without running is worse than
one that errors: an erroring command gets investigated, a passing one gets
believed. A session told to validate the store before committing runs this,
sees nothing wrong, and commits. `make check` does still run `bin/docket check`,
so nothing has actually shipped broken — but the guard the two documents
describe does not exist, and the failure mode it was written to prevent is one
a session would not notice.

Same class as PL-K79K, the digest advertising a `triage` command that did not
exist: a live instruction in a document `main` depends on, naming a mechanism
that does not work. `defect` by `ROADMAP.md`'s "What counts", not `infra`.

Present before Gate 0 was frozen — `punch-list` is the pre-rename name — so it
qualifies for that gate under the presence rule if someone is looking.

**Where.** `Makefile:1` (`.PHONY`) and `Makefile:21` (`punch-list:`). The fix
is renaming the target to `docket` and keeping `punch-list` as an alias or
dropping it; `CLAUDE.md:` and `.claude/skills/docket/SKILL.md` already name
`docket`.

**Found.** While adding the `release` target for PL-674D. Not fixed there: it
is a different item's problem, and the batch it was found in was explicitly
scoped to eight items.

**Done when.** `make docket` validates the store and fails when the store is
wrong, and no document names a make target that does not exist.
