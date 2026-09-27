---
id: PL-29RM
title: In a truncated clone, vcs._written_since reads a grafted commit's whole tree as written since the fork, because git shows a shallow boundary commit as a root, so a restore to content the base holds at the horizon reads as landed - the ever-held misread again, bounded to the horizon's tree; test_a_merge_of_main_read_below_an_uneven_horizon_spends_only_what_a_squash_took passes through it
status: untriaged
added: 2026-09-27
---

**Problem.** In a truncated clone, vcs._written_since reads a grafted commit's whole tree as written since the fork, because git shows a shallow boundary commit as a root, so a restore to content the base holds at the horizon reads as landed - the ever-held misread again, bounded to the horizon's tree; test_a_merge_of_main_read_below_an_uneven_horizon_spends_only_what_a_squash_took passes through it
