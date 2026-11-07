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

**Moved from `ROADMAP.md` on 2026-11-07 (`PL-DWGC`).** The version table's row for v0.6.9 carried this text after its first sentence until then. The project owner's answer in `PL-LVN8` keeps one sentence for each row in the roadmap and moves the rest of the row to the release's cut item.

> 95 items, and a patch on both halves of § "Versioning decision"'s test. No capability boundary is crossed: v0.7.0, the schematic, is scoped and not built, and v0.7.0 and v0.8.0 are given to milestone sections. **No stored value changed, and every modelled state is bit-identical**: `core/` moved (`5e150fb` to `dbba1c0`) and `data/` moved (`2a85cd0` to `2f84dbb`), and the trajectory comparison against the v0.6.8 tag found every state vector, canonical state, drawn window and hover string identical over 81 cases and three 24-hour runs. `data/` gained each agent's molar mass and liquid density (`PL-KZ99`, `#1866`) and changed no value it already held. What moved is the agent accounting: `PL-XST1` (`#1826`) sums the delivered and exhausted totals with Kahan compensation, so the delivered total, shown in litres to a tenth, reads a different tenth in 398 of 236,313 sampled readouts, each one an amount exactly halfway between two tenths. **It finishes ten features**, among them `model-spec-accuracy` and `fewer-red-runs`, and closes four generator heads, all spent (`PL-58D7`, `PL-HJKN`, `PL-N7MM`, `PL-ZR49`). **39 are Gate 3 entries**, three of them in v0.7.0's Required scope, and the gate stands at 64 of 87 cleared, from 25 of 48 at the v0.6.8 tag. `PL-8D7L`, the cut, ships in no release under `PL-KRS6`.
