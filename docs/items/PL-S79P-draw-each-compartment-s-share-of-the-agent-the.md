---
id: PL-S79P
title: Draw each compartment's share of the agent the run holds as one bar on the compartment schematic, so fat's growing share shows while its tension stays near zero
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: schematic
touches: src/anesthesia_sim/app, tests/integration, tests/unit, tools/contrast_check.py
blocked-by: PL-RNYV
added: 2026-10-25
closed: 2026-11-01
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

**Checked 2026-10-25 (`PL-F2NX`, Gate 3's staleness sweep): still true.** The named test does not exist, the fat shares quoted match `PL-H5DV`'s table, and its blocker, `PL-RNYV`, is open.

**What `PL-2881` settled for this build, 2026-11-01.** `docs/MODEL.md` § "The compartment schematic: what its heights, amounts and share bar assert" defines the share as the compartment's amount over `stored_agent_l`, circuit included. A share printed in text is a whole percent, a positive share below 0.5% reads `<1%`, and a run that holds no agent draws an empty bar with no shares (§ "Displayed precision").

**Closed 2026-11-01, by `#1921`.** `ShareBar` in `app/qt_schematic.py` draws one bar under each run's containers, divided into six segments in the containers' order and trace colours. Each segment's length is the compartment's amount over `stored_agent_l`, and `share_segments` in `app/compartment_schematic.py` computes it from the snapshot's per-compartment record. Three fixed lines under the bar name every share in whole percent, as `format_compartment_share` writes it, with `<1%` and `>99%` at the ends. While the run holds no agent, the bar is empty and the lines say why, and while the run's values are withheld, the bar is empty with no lines. A panel-coloured divider stands between each pair of neighbouring segments that are at least three pixels wide. So each segment's ends are seen against the panel, whose contrast with every compartment colour `tools/contrast_check.py` checks, and a tiny share's dividers never cover a neighbour. The bar's height, the divider's threshold and the wording of the lines are placeholders. The two blind passes found two optional faults, both fixed, and are recorded in the commit trailers.
