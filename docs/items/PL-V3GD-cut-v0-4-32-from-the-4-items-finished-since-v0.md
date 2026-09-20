---
id: PL-V3GD
title: Cut v0.4.32 from the 4 items finished since v0.4.31: the release that completes pr-title-enforcement
priority: P2
effort: S
status: done
classes: housekeeping
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases, docs/items
added: 2026-09-20
closed: 2026-09-20
pr: 747
payoff: clears the release the session-start digest re-raises in every session, and unblocks the next cut, which docket refuses while a release is untagged
verify: grep -q '^version = "0.4.32"' pyproject.toml
---

**Problem.** Cut v0.4.32 from the 4 items finished since v0.4.31: the release that completes pr-title-enforcement

The four are `PL-4DCG` (the anesthesia-machine survey), `PL-R5VS` (the `v0.4.31`
cut itself), `PL-XZD0` (reconciling CI's reporting jobs against the
branch-protection required list) and `PL-JVHL` (the chart hover answering for
every run inside the radius). All four are merged on `origin/main`; `v0.4.31` is
cut and tagged, so nothing is outstanding from the previous release.

`0.4.32` is the number because no capability boundary is crossed — it is the
mechanical guess and it is also the right one. Offered to the project owner and
approved on 2026-09-20.

**The cut also clears four `pr:` backfills.** `PL-4DCG` (#742), `PL-JVHL`
(#743), `PL-R5VS` (#739) and `PL-XZD0` (#740) are marked `done` on the base and
record no `pr`. `bin/docket record` bare writes every number the base can
supply; let it ride the release commit rather than composing one for it.

**Procedure**, from the `docket` skill's release mode, in order:

1. `make release VERSION=0.4.32` — never `bin/docket release` alone, which
   leaves `uv.lock` stale and fails the next `uv sync --locked`.
2. `bin/docket record` (or `make fix`) for the four `pr:` numbers above.
3. The edits `bin/docket release` prints as outstanding: a `ROADMAP.md`
   version-table row, the `current baseline` mark moved onto it, and a baseline
   section saying what the release was *for*. Nothing generates that prose.
4. `make check`, which is what proves step 3 landed. Running it earlier fails on
   edits nobody has been asked for yet.
5. Commit, push, open the pull request, merge.
6. The tag is the **project owner's** to push — tag pushes fail from a session
   here, convincingly, reporting `Everything up-to-date` while `git ls-remote
   --tags` shows nothing (`PL-N936`). Paste the three commands filled in, with
   no angle-bracket placeholder, and say the tag is outstanding until they
   confirm it.

**Why it matters.** The release train is this project's cadence, and the
session-start digest asks every session to offer the release before taking new
work — so an uncut release is re-raised in every session until somebody cuts it.
It also gates the next one: `bin/docket release` refuses to cut while the
previous release is untagged.

**Done when.** `pyproject.toml` reads `0.4.32`, `docs/releases/v0.4.32.md`
exists, `ROADMAP.md` carries the row and the baseline section, `make check`
passes, and the tag is pushed.
