---
id: PL-GWQ7
title: required_checks_check assumes a two-space indent under jobs: and on:, so a workflow indented four spaces is skipped silently; latent
status: untriaged
feature: required-check-trigger-reading
touches: tools/required_checks_check.py, tests/unit/test_required_checks_check.py
added: 2026-10-04
---

**Problem.** required_checks_check assumes a two-space indent under jobs: and on:, so a workflow indented four spaces is skipped silently; latent

**Found 2026-10-04 by `PL-R417`'s last-slice sweep (`#1353`)**, eight read-only auditors over every reader in `tools/`, `subprojects/docket/src/docket/` and `.claude/hooks/`, each case reproduced on bare python3 3.11.15 and re-run by the session that filed it.

YAML lets a mapping use any indentation consistently; the reader matches its keys at a fixed two-space indent, so a workflow written with four reads as holding no jobs or triggers, with nothing said. Not a member of `PL-R417`; a member of `PL-848V`, the head for which events a workflow's `on:` names. Latent: the six workflows all indent two spaces.
