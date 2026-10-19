---
id: PL-KFJY
title: tools/headless_worker.py runs every worker at Opus 5.5's default medium effort because it passes no --effort, not at the owner's high for apparatus work and max for simulator work (docs/maintainer.md, Match effort to the standard the work is held to)
priority: P2
effort: S
status: done
classes: defect
touches: tools/headless_worker.py, tests/unit/test_headless_worker.py, docs/maintainer.md
deferred-from: v0.6.0 - a workflow-lane runner defect outside the layout release
added: 2026-10-19
closed: 2026-10-19
pr: 1685
payoff: each worker runs at the effort the owner chose for the standard its item is held to: high for apparatus work, max for simulator work
verify: grep -q -- '--effort' tools/headless_worker.py
---

**Problem.** `claude_argv` in `tools/headless_worker.py` passes no `--effort`, and the project's `.claude/settings.json` sets no effort level. So every worker runs at Opus 5.5's default, `medium` (Claude Code docs, *Model configuration*, section "Adjust effort level", https://code.claude.com/docs/en/model-config, read 2026-10-19). The owner chose `high` for apparatus sessions and `max` for simulator sessions (`docs/maintainer.md` § "Match effort to the standard the work is held to", `PL-SW0B`). The first credit run, on PL-3R6L, ran at `medium`.

**Why it matters.** On Anthropic's SWE-bench Pro subset, Opus 5.5 solved 92.8% of tasks at `medium` and 95.3% at `high` (*Optimizing for cost and intelligence*, https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence, § "Tune effort", read 2026-10-19). Workers on simulator items would run two levels below the owner's choice.

**Done when.** The runner reads each item's lane through docket and passes `--effort max` for an item whose lane reaches the simulator (`product` or `crossing`) and `--effort high` otherwise. The ledger records the level, and a test pins both.

**Generator check.** A one-off: the runner is the only code that launches a session with a chosen effort, so no other reader of the effort-per-standard rule exists to misread it.
