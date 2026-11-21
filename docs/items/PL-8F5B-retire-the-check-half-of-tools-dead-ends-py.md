---
id: PL-8F5B
title: Retire the check half of tools/dead_ends.py from make check and CI, and keep emit for the session-start digest
status: untriaged
feature: standing-weight
added: 2026-11-21
---

**Problem.** Retire the check half of tools/dead_ends.py from make check and CI, and keep emit for the session-start digest

**Why it matters.** `PL-LY24` counted what each workflow-record check refused in CI from 2026-08-22 to 2026-11-21, and the owner agreed in `PL-KGPR` to retire this one (project owner, 2026-11-21, ratified, "Agree with recs"). `tools/dead_ends.py check` has never refused. The dead-ends list itself stays: `.claude/hooks/docket-digest.sh` still runs `tools/dead_ends.py emit` at session start.

**What to do.** Remove `tools/dead_ends.py check` from `make check` and `.github/workflows/quality.yml`, then remove the `check` subcommand and its tests. Keep `emit` and `docs/dead-ends.md`.

**Done when.** No command or workflow runs `tools/dead_ends.py check`, and the session-start digest still prints the entries.
