---
id: PL-3Z9X
title: "Cut v0.4.14: the five ways bin/docket verify rejected correct work, and the checks that named the wrong cause"
priority: P2
effort: S
status: done
classes: planning, docs
feature: release-process
milestone: v0.4.15
touches: pyproject.toml, uv.lock, ROADMAP.md, docs/releases
added: 2026-09-12
closed: 2026-09-12
pr: 498
verify: python3 tools/doc_check.py check && grep -q '^version = "0.4.14"' pyproject.toml && test -f docs/releases/v0.4.14.md
---

**Problem.** Cut v0.4.14: the five ways bin/docket verify rejected correct work, and the checks that named the wrong cause

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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.4.14 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> Nothing computational moved, and this one can say so more strongly than the last: `git rev-parse v0.4.13:src HEAD:src` resolves to the same tree object at both ends, so the whole of `src/` is byte-identical - `core/`, `app/` and `data/` alike - where v0.4.13 could claim only `core/`. `docs/MODEL.md` is byte-identical and `.github/` untouched, so no equation, parameter, unit, numerical method, solver step, displayed value or CI gate moved; the three changed files under `tests/` exercise `tools/` and none imports `anesthesia_sim`. **Fifteen of the seventeen items are one defect wearing different clothes:** a piece of the apparatus produced a signal a session could act on, and the signal was false. **Five are `bin/docket verify` refusing exactly what the instructions mandate** - a branch carrying a capture (`PL-66PR`), a close-out letting `docket record` ride its commit (`PL-ZYQC`), an item whose declared work *is* editing `.claude` (`PL-69JZ`), the front matter that closing an item necessarily edits (`PL-B5YN`), and a batch branch audited as one item (`PL-4LT9`) - all five the same inability to tell a delegated worker from a session reviewing its own branch. **The repair is deliberately partial and the gap is recorded rather than implied:** two shapes are exempt unconditionally, the other three only under the new opt-in `verify --self`, and nothing on the documented close-out path names that mode yet - `PL-7XTS` was filed in this range to say so. `PL-4LT9` is *reported rather than repaired* by explicit decision; `item_commits` still matches every subject, so the new check never blocks. **Two are the stop hook demanding a push for work already pushed**, from unrelated causes: `--depth 1` implies `--single-branch`, so `git push` never creates the ref the hook reads (`PL-3SGR`), and the merged-PR recovery's `checkout -B` repoints the upstream (`PL-483K`) - whose dangerous variant is that the same missing ref makes `--force-with-lease` refuse with `stale info` and invites a bare `--force` mid-rebase. What shipped widens `remote.origin.fetch` at session start and deliberately never fetches and never prunes. **Three named a wrong cause with complete confidence**, which is worse than failing: eleven missing-row errors pointing a session at the safety-critical provenance table when the fault was a decoy table 300 lines above (`PL-ZBZZ`), a checker erroring on an elaborated `**Decision needed**` heading its own README permits (`PL-VJ1X`), and stale `.pyc` bytecode producing a `make check` failure unreachable from the source in front of the reader (`PL-01GD`). **Three reported nothing or the wrong number:** one unparseable glob token aborting the whole documentation gate on a traceback (`PL-0M7L`), `docket next` understating the queue by exactly the untriaged pile (`PL-ZWBK`), and `docket check` advising every run that a `P1` `safety` item was ready to promote when it must ship behind an unshipped port (`PL-L09X`). `PL-KY7M` removes ten deprecation lines per run; `PL-BBDD` is the same class at opposite polarity, an uncovered `ruff.toml` letting a delegated diff relax the linter and still report ACCEPT. **They were found by running the tools rather than reading them:** `PL-3B47`'s pass over the 46 untriaged captures closed 23 ids, eight of them dropped as duplicates, already fixed, or overtaken by the Qt port. **Seventeen items, one of which is the v0.4.13 cut itself.** Two debts leave with it rather than inside it: `PL-01GD` shipped with no test at all (`PL-H9GV`), and the same triage pass wrote into this document a sentence calling every drawn chart point an M4 representative of roughly 120 recorded samples - a path `PL-2FM6` deleted in v0.4.12 (`PL-DZFJ`).
