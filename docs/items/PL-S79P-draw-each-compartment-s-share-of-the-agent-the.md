---
id: PL-S79P
title: Draw each compartment's share of the agent the run holds as one bar on the compartment schematic, so fat's growing share shows while its tension stays near zero
priority: P1
effort: M
status: blocked
classes: safety, anticipated
feature: schematic
touches: src/anesthesia_sim/app, tests/integration, tests/unit, tools/contrast_check.py
blocked-by: PL-RNYV
added: 2026-10-25
payoff: a learner sees fat's growing share of the agent while its tension stays near zero
verify: grep -rq 'def test_the_share_bar_shares_add_up_to_the_whole' tests
---

**Where this came from.** `PL-LF0P` scoped v0.7.0, the schematic, on 2026-10-25. The project owner chose containers that fill to tension, labelled with their amounts, plus a bar showing each compartment's share of the agent (project owner, 2026-10-25, ratified, over containers drawn to scale and over Gas Man's Picture as it is). `ROADMAP.md` § "v0.7.0 - the schematic" has the reasoning and the measurements behind it.

**Problem.** Containers that fill to tension show fat nearly empty while it
holds a fifth of the stored agent at one hour and almost a third at three
(`PL-H5DV`). Labelled amounts alone make a learner compare numbers.

**What to build.** One bar on the schematic, divided by compartment, each
segment's length the compartment's share of all the agent the run holds,
circuit included, as `PL-2881` specifies. Each segment is named in text, so no
compartment is told apart by colour alone. The bar is read from the same
per-compartment record (`PL-KFTM`) as the container labels.

**Tests.** The shares add up to 100% at every instant tested, and each
segment's share matches its container's amount divided by `stored_agent_l`.

**Why it matters.** Position on a common scale is read more accurately than
area (Cleveland and McGill, 1984), so the bar carries the amount lesson that
to-scale containers could not in this model.

**Done when.** The bar is drawn on the schematic, labelled, and tested as
above.

**Generator check.** None: the only workflow path touched is
`tools/contrast_check.py`, which gains this View's colours as every new View's
colours are added, and that produces no findings of its own.
