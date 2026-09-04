---
id: PL-66FP
title: Two sessions cut the same release independently: docket release has no in-flight guard, so a second session bumps the version and writes notes for a version already on main
status: untriaged
added: 2026-09-04
---

**Problem.** Two sessions cut the same release independently: docket release has no in-flight guard, so a second session bumps the version and writes notes for a version already on main

**Why it matters.**

**Where.**

**Done when.**

**Observed 2026-09-04.** Two sessions cut v0.3.7 within the same hour. One
merged as #301 with seven items plus `PL-DR1Z`; the other reached #302 with the
same seven minus `PL-DR1Z`, having bumped `pyproject.toml`, relocked `uv.lock`,
written `docs/releases/v0.3.7.md`, stamped seven items with `milestone: v0.3.7`,
added a version-table row and written a whole `## Current baseline: v0.3.7`
section. All of it duplicate. Resolving the merge meant taking `origin/main`'s
side of both conflicted files, after which `git diff origin/main` was empty and
#302 had nothing left to merge.

**Why the existing guards did not fire.** Every in-flight guard this project
has matches a `PL-` id - `docket flight`, `show`, `next`, `concurrent`, the
digest, `branch_id_check`. A release cut carries no item id by design:
`branch_id_check` prints "a release commit, which owes no id". So the one piece
of work that writes to `pyproject.toml`, `uv.lock`, `ROADMAP.md` and a new
`docs/releases/` file - the most collision-prone change in the repository -
is the only one no guard can see. `PL-CP74` closed exactly this hole for
unfiled housekeeping; a release is the same shape and was not covered.

**Where a check could go.** `bin/docket release` already refuses to cut while
the previous release is untagged. The same command could refuse, or warn, when
the version it is about to write already exists on the default base - readable
from `git show origin/<base>:pyproject.toml` or from `docs/releases/`, and
needing no network beyond the fetch a session has already done. Whether it
should be a refusal or an advisory is the open question: a session cutting a
release deliberately after a failed attempt would trip a refusal.

**Cost.** One session's release work, and a merge that had to be resolved by
discarding it. Nothing was lost from `main`, because the better cut won.
