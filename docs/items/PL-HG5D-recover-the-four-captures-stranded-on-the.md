---
id: PL-HG5D
title: Recover the four captures stranded on the desflurane branch by the history rewrite
priority: P2
effort: S
status: done
classes: infra
feature: parallel-sessions
touches: docs/items
added: 2026-09-06
closed: 2026-09-06
pr: 387
not-delegable: The work is a `git checkout` of four files off a ref, so no command can fail before it and pass after except a `grep` for the files themselves; `make docket` proves the recovered items parse, which is what actually needed checking.
---

**Problem.** The copyrighted-PDF purge rewrote `main` and left seven branches
on the pre-rewrite history, unable to merge into anything (`PL-YGF3`). One of
them, `claude/desflurane-tec6-vaporizer-kulwij`, held four captures that exist
on no other ref: `PL-439V`, `PL-5K5C`, `PL-CXYT` and `PL-SHG5`.

**Why it matters.** While those refs exist nothing is lost, but two ordinary
actions destroy them and only one has a guard - a prune, which
`.claude/hooks/no-prune-guard.sh` refuses, and a `git reset --hard
origin/main`, which nothing refuses. `PL-SHG5` is the sharpest case: it reports
two publisher-copyright full texts being redistributed from the now-public
repository, and it was invisible to `docket next`, `docket check` and the debt
gate for as long as it sat off the default branch.

**What was checked, and what was deliberately not recovered.** Enumerating by
filename overcounts: `PL-3D2M` and `PL-XYRN` appeared missing from `main` but
are present under changed filenames, so the comparison was redone by `id`.
Modified - as opposed to new - item files across all seven branches were
examined and none carried work `main` lacks: every difference is `main` being
ahead (`ready` against `done`, `untriaged` against triaged, shorter briefs),
so taking any of them would have regressed landed work. The two files where a
branch held one extra line carried a `pr:` field that `bin/docket record` had
already written on this branch.

**Where.** `docs/items/`, from
`origin/claude/desflurane-tec6-vaporizer-kulwij`. The branch itself is left
alone: it belongs to a live session, and recovering the item files neither
touches it nor settles the copyright question `PL-SHG5` raises.

**Done when.** The four items are on a branch descended from the rewritten
`main` and `make docket` reads them, so that losing the original ref costs
nothing. Done.
