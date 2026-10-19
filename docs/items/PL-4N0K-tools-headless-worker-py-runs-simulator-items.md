---
id: PL-4N0K
title: tools/headless_worker.py runs simulator items at max effort, but the owner set high for all work on 2026-10-19 (PL-6XZG): read the level from effortLevel in .claude/settings.json, its one home, instead of a lane table
status: untriaged
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py, docs/maintainer.md
added: 2026-10-19
---

**Problem.** tools/headless_worker.py runs simulator items at max effort, but the owner set high for all work on 2026-10-19 (PL-6XZG): read the level from effortLevel in .claude/settings.json, its one home, instead of a lane table

**Why it matters.** The project owner set `high` effort for all work on 2026-10-19, simulator sessions included, over `max` and `xhigh` (`PL-6XZG`, `docs/maintainer.md` § "Match effort to the standard the work is held to"). `PL-KFJY` was briefed against the record that decision replaced, and merged the same day as #1685 with a table that runs simulator items at `max`. So every runner run on a simulator item ignores the owner's setting. The level was also a second copy: `.claude/settings.json` already holds it as `effortLevel`, which is the home every interactive session reads.

**Fix.** The runner reads `effortLevel` from `.claude/settings.json` and passes it as `--effort` to every run. It refuses before any spend when the key is missing, rather than falling back to the model's default. The lane table, `effort_for` and `read_lanes` go. `docs/maintainer.md`'s runner paragraph says the run takes the project's level.

**Done when.** `tools/headless_worker.py` holds no effort level of its own, a dry run prints the level the settings file holds, and a settings file with no `effortLevel` is refused.

**Generator check.** One stale brief. `PL-KFJY` was written before `PL-6XZG` widened `high` to all work, and nothing re-read it. The one-source-of-truth inventory (`PL-K88Z`) counts configuration copies like this one.
