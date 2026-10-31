---
id: PL-8D7L
title: Cut v0.6.9 from the 95 items finished since v0.6.8
status: done
resource: release-train
added: 2026-10-31
closed: 2026-10-31
pr: 1894
verify: grep -q '^## Current baseline: v0.6.9' ROADMAP.md
---

**Problem.** Cut v0.6.9 from the 95 items finished since v0.6.8

**Done 2026-10-31.** `make release VERSION=0.6.9` stamped the 95 items and
wrote `docs/releases/v0.6.9.md`. `core/` and `data/` moved since the v0.6.8
tag, so the trajectories were compared against it, with the kept scripts in
the project's shared `release-trajectory` folder. Every state vector,
canonical state, drawn window, hover string and halt instant is identical
over 81 cases and three 24-hour runs. The only moved values are the
accounting totals, which `PL-XST1` now sums with Kahan compensation: the
delivered total reads a different tenth of a litre in 398 of 236,313 sampled
readouts, each at an amount exactly halfway between two tenths.
`v0.6.9-against-v0.6.8.txt` in that folder has the count.
