---
id: PL-F7XT
title: Retire tools/pr_body_check.py --anchors from make check and CI, and keep docs/pr-bodies/ as a closed archive
priority: P2
effort: S
status: done
classes: infra
feature: standing-weight
touches: Makefile, .github/workflows/quality.yml, tools/pr_body_check.py, tests/unit/test_pr_body_check.py, tools/doc_check.py, tests/unit/test_doc_check.py, docs/apparatus.md, docs/pr-bodies/README.md, .claude/skills/docket/modes/release.md
added: 2026-11-21
closed: 2026-11-21
pr: 2185
payoff: make check and CI run one check fewer, and the tool that recovers a dropped pull request body loses the mode that never refused
verify: ! grep -qF 'pr_body_check.py --anchors' Makefile && ! grep -qF 'pr_body_check.py --anchors' .github/workflows/quality.yml && ! grep -qF 'def anchors' tools/pr_body_check.py
---

**Problem.** Retire tools/pr_body_check.py --anchors from make check and CI, and keep docs/pr-bodies/ as a closed archive

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). The `--anchors` mode has never refused, and the tool has cost 34 items. The recovered bodies in `docs/pr-bodies/` stay as a closed archive.

**What to do.** Remove `--anchors` from `make check` and `.github/workflows/quality.yml`. Then remove what nothing else uses: the mode, and any part of the tool only it needed, with their tests. Keep `docs/pr-bodies/`.

**Done when.** Neither `make check` nor CI runs `tools/pr_body_check.py --anchors`, and `docs/pr-bodies/` is unchanged.

**Triaged 2026-11-21: the archive is kept, and it still grows.** This brief calls `docs/pr-bodies/` a closed archive. It is not closed. `.claude/skills/docket/modes/release.md` runs `python3 tools/pr_body_check.py` at each release, and `--recover` where that names a squash commit that lost its body. Five records carry a `recovered:` date after 2026-09-25: two on 2026-09-26 and one each on 2026-09-28, 2026-10-12 and 2026-10-18. This item removes the `--anchors` mode and nothing else. The release step stays, because a body that a merge drops is otherwise kept only on GitHub. `--recover` writes each record's `commit:` from the squash commit that it read, so a new record's `commit:` is right when it is written. After this item no check notices a `commit:` that a later rewrite of `main`'s history leaves naming nothing. GitHub's rulesets refuse a forced push to `main` (`tools/github_refusals_check.py`).

`docs/pr-bodies/README.md` says that `--anchors` keeps `commit:` current, so that sentence changes. No record changes.

**Generator check.** One-off. It is the removal that the owner decided in `PL-KGPR` from `PL-LY24`'s count, and no fact was misread to cause it.

**Done 2026-11-21.** `make check` and `.github/workflows/quality.yml` no longer run `--anchors`. `tools/pr_body_check.py` loses the mode and `parse_record`, the record reader that only the mode used. Their tests go with them. One test stays in a new form: `docs/pr-bodies/README.md` is not counted as a record. The default mode, `--recover`, `--compare` and `--screen-push` are unchanged, and so is the release step that runs the first two.

Documents checked, and changed where they said the mode runs: `docs/pr-bodies/README.md` (the sentence on `commit:`), `.claude/skills/docket/modes/release.md` (the recovery step), `docs/apparatus.md` (the tool list and the floor commands), and two docstrings in `tools/doc_check.py`. Checked and left: `docs/maintainer.md` and `docs/resident-instructions.md` name the tool's default mode and `--recover` only. The `Makefile` comment above `tools/rules_paths_check.py` still pointed at the branch-id check that `PL-HS2T` removed, and is corrected here.
