---
id: PL-3Z9X
title: "Cut v0.4.14: the untriaged queue emptied, and the five ways bin/docket verify rejected correct work"
priority: P2
effort: S
status: ready
classes: planning, docs
feature: release-process
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases
added: 2026-09-12
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.14"' pyproject.toml && test -f docs/releases/v0.4.14.md
---

**Problem.** Cut v0.4.14: the untriaged queue emptied, and the five ways bin/docket verify rejected correct work

**Why it matters.** Seventeen items had landed since v0.4.13 and `queue-hygiene`
had completed, which is past the point where release notes can be written from
memory rather than from the store.

**Done when.** `pyproject.toml` reads `version = "0.4.14"`, `uv.lock` is
relocked to match, `docs/releases/v0.4.14.md` exists and the seventeen items
carry `milestone: 0.4.14`; `ROADMAP.md` has the v0.4.14 version-table row, the
`current baseline` mark moved off v0.4.13 onto it, and a baseline section saying
what the release was for; and `make check` is green.

**The version is 0.4.14, named by the project owner** (2026-09-12, "go on
v0.4.14"). `ROADMAP.md`'s "Versioning decision" says the number marks the
capability boundary a release crosses. **This one crosses none, and the check is
mechanical rather than a judgement:** `git diff --stat v0.4.13..HEAD -- src/`
is empty, so `src/anesthesia_sim/` is byte-identical to v0.4.13 and no equation,
parameter, unit, numerical method, solver step or displayed value moved.
`docs/MODEL.md` is unchanged in the same range. The three changed files under
`tests/` are `test_doc_check.py`, `test_stop_hook_patch.py` and
`test_workflow_paths_check.py` - apparatus tests, none of them a reference case.

**Preconditions checked before cutting**, both of which `bin/docket release`
refuses on: v0.4.13 is tagged on the remote (`git ls-remote --tags origin`
shows `refs/tags/v0.4.13` at `5f8b93d`), and no other session is cutting -
`list_sessions` showed this session running and the rest archived, with no open
pull request on the repository. That check is `PL-66FP`'s, two sessions having
cut v0.3.7 within the hour.

**What was done.** `make release VERSION=0.4.14`, which bumped `pyproject.toml`,
relocked `uv.lock`, wrote `docs/releases/v0.4.14.md` and stamped the seventeen
items. Then the three things it names as owed by hand: the version-table row,
moving the `current baseline` mark off v0.4.13, and the baseline section - the
prose saying what the release was *for*, which nothing generates.

**The tag is outstanding and is the project owner's to push**, `PL-N936` having
established that a session's tag push fails while reporting success.
