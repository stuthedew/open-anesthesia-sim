---
id: PL-F7XT
title: Retire tools/pr_body_check.py --anchors from make check and CI, and keep docs/pr-bodies/ as a closed archive
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** Retire tools/pr_body_check.py --anchors from make check and CI, and keep docs/pr-bodies/ as a closed archive

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). The `--anchors` mode has never refused, and the tool has cost 34 items. The recovered bodies in `docs/pr-bodies/` stay as a closed archive.

**What to do.** Remove `--anchors` from `make check` and `.github/workflows/quality.yml`. Then remove what nothing else uses: the mode, and any part of the tool only it needed, with their tests. Keep `docs/pr-bodies/`.

**Done when.** Neither `make check` nor CI runs `tools/pr_body_check.py --anchors`, and `docs/pr-bodies/` is unchanged.
