---
id: PL-SRNF
title: Correct PL-C3K1's count of the apparatus path set's copies from three to two, and record that PL-LZ54 waits on PL-Z6C8
priority: P2
effort: S
status: done
classes: housekeeping
touches: docs/items/PL-C3K1-tools-rules-paths-check-py-keeps-the-apparatus.md, docs/items/PL-LZ54-after-whole-second-stepping-lands-correct-each.md
added: 2026-11-21
closed: 2026-11-21
pr: 2195
payoff: two open briefs state what the tree holds, and the queue check stops printing an advisory about PL-LZ54 on every run
verify: grep -qF 'Two copies remain' docs/items/PL-C3K1-tools-rules-paths-check-py-keeps-the-apparatus.md
---

**Problem.** Correct PL-C3K1's count of the apparatus path set's copies from three to two, and record that PL-LZ54 waits on PL-Z6C8

**Generator check.** One-off. `PL-C3K1` (one home for the apparatus path set) describes the check as its counted refusals saw it, before `PL-2PJ6` (move the history out of the launch instructions) removed one copy on the same day. `PL-LZ54` (correct the interface documents after whole-second stepping) was filed with its wait stated in prose only. Neither is a fact that readers keep misreading.

**Built 2026-11-21.** Two open briefs now state what the tree holds.

1. `PL-C3K1` (one home for the apparatus path set) says in its title, its problem and its plan that two copies remain. A dated note names them: the list in `CLAUDE.md` and the `paths:` of `.claude/rules/apparatus-standard.md`, each compared with `docket.toml`'s `workflow_paths`. `APPARATUS_LISTS` in `tools/rules_paths_check.py` and the check's own output, "the apparatus set's 2 copies agree with each other and with workflow_paths", were read at `a5d582f0c`. The count of six refusals that named three copies is a record of what CI printed, and stays.
2. `PL-LZ54` (correct the interface documents after whole-second stepping) lists `PL-Z6C8` (the last item of that build) in `blocked-by`. Its status stays `untriaged`, because triage sets a status and runs outside this thread. `bin/docket check` no longer prints its advisory about that item.

No file outside `docs/items/` changed, so the full check suite was not run again. It passed on `PL-G3KZ`'s branch at about 06:20 UTC on 2026-11-21. `bin/docket check` reports no error.
