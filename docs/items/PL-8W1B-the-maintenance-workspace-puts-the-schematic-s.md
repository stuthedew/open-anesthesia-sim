---
id: PL-8W1B
title: The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading
priority: P1
effort: M
status: done
classes: defect, safety
feature: presentation-safety
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/qt_schematic.py, tests/integration/test_compartment_schematic_view.py, tests/unit/test_compartment_schematic.py, docs/MODEL.md
added: 2026-11-02
closed: 2026-11-14
pr: 2145
payoff: a learner cannot read a compartment's tension off the concentration chart's gridlines from the height of its container
verify: grep -rq 'def test_a_container_cannot_be_read_against_the_chart' tests/
---

**Problem.** The Maintenance Workspace puts the schematic's 96 px containers beside the full-height concentration chart, so one tension stands at different screen heights in the two Views and a learner may read a fill level across against the chart's gridlines; align the containers to the plot's scale or caption them against that reading

**Where this came from.** The second blind review pass on `#1929` (`PL-PR1W`) named it as optional on 2026-11-02. Each container's label still prints its tension in text, and the schematic's caption says a height is a tension on the chart's 0 to 3 MAC scale, so no value is lost. The risk is a reading across the two Views. The containers are `_CONTAINER_HEIGHT` (96 px) tall in `app/qt_schematic.py` and sit at the top of their Area, while the plot beside them is several hundred pixels tall.

**Why it matters.** The caption says each container fills against the chart's scale. In the Maintenance Workspace the chart stands beside the containers at full height. A learner who reads a fill level across to the chart's gridlines reads the wrong tension. The label under each container still prints the right value, so the risk is a misleading picture rather than a lost number. The safety-critical standard counts a misleading plot as a defect.

**Reproduced 2026-11-03, by reading; no screenshot.** `_CONTAINER_HEIGHT` is 96 in `src/anesthesia_sim/app/qt_schematic.py`. `scale_caption` in `src/anesthesia_sim/app/compartment_schematic.py` takes the top of the scale from the chart's own axis. `src/anesthesia_sim/data/workspaces/maintenance.json` puts the chart at full height with the schematic beside it.

**Done when.** In the Maintenance Workspace a container's fill cannot be read as a tension against the chart's gridlines. Either the containers share the plot's vertical scale, or the caption says their height is not on the gridlines' scale. Which of the two is a placeholder choice for the session that builds it. A test shows the chosen route.

**Generator check.** One-off. The fact is the vertical scale a drawn height stands for, when two Views draw one quantity at different heights. No head states it.

**Release question, put to the owner 2026-11-03. Superseded on 2026-11-07, see below.** v0.7.0 releases the schematic, and this item is a defect in how the schematic reads beside the chart. Whether the release waits for it is the owner's call, because the safety-critical standard reaches it. **Recommended:** release v0.7.0 with this item deferred, and take it in the first patch. The tension printed under each container is correct, so no number a learner reads is wrong. The risk is a misreading by eye in one Workspace.

**Checked 2026-11-07 against the tree at the freeze (`PL-GW0P`).** The problem began after Gate 3 froze at `817a4d88`. The item is classed `safety`, so it joins v0.7.0's frozen list whatever that answer. It is not deferred, because a learner can read a wrong tension from the containers now. The schematic did not exist at `817a4d88`. It came with `489c568d`, and its place beside the chart in the Maintenance Workspace with `506c8b50`, both on 2026-11-02.
 This replaces the 2026-11-03 recommendation to release v0.7.0 with the item deferred. Under `PL-8C8W` a `safety` entry may be deferred only when no learner can see a wrong value now, and a fill level read across against the chart's gridlines is a wrong tension a learner can see. So the release waits for this item unless the owner decides otherwise.

**Built 2026-11-14.** Each container now carries the chart's gridlines as
short marks inside its two sides, and the caption names their spacing.
Aligning the containers to the plot's own height was not taken, because one
View would have to read another View's geometry, which the View contract does
not allow. The marks need no such read. `scale_marks` in
`app/compartment_schematic.py` takes the chart's ticks from the same
`percent_axis_ticks` call as the chart's axis, and returns each interior tick
as a share of the axis top: every 0.5 MAC below 3 MAC, so sixths of the
container. `SchematicShown.marks` carries them, empty while the values are
withheld. `SchematicCanvas._paint_marks` in `app/qt_schematic.py` draws each as
an 8 px rule in `MUTED` in from both sides, leaving the middle of the fill
clear. The caption's second line reads "Marks stand at the chart's gridlines,
every {step} ({step_mac})." `docs/MODEL.md` § "The compartment schematic: what
its heights, amounts and share bar assert" said a height on the schematic and
on the chart "show the same tension". It now says a share of a container's
height matches the same share of the chart's axis, that the fill does not line
up with the chart's gridlines on screen, and that the containers carry marks
at them. `test_a_container_cannot_be_read_against_the_chart` opens the
Maintenance Workspace, checks that the chart's plot is more than twice a
container's 96 px, and finds five `MUTED` rows inside each container's left
side at the sixths. `test_each_container_is_marked_at_the_chart_s_gridlines`
checks the shares and the caption's spacing for all three agents, with the
spacing taken from each agent's data file.

**Blind review, 2026-11-14.** Both passes named one should-fix and one
optional finding, the same two. The first build only added a caption sentence
saying the heights do not line up with the chart's gridlines. Both passes said
a warning in small type is the weaker route, and that the View can prevent the
misreading on its own by drawing the chart's gridlines inside each container.
That is the build above. Both also said the caption had dropped
"concentration", so in a Workspace beside the wash-in chart "the chart" named
the wrong one. The first line is back to "on the concentration chart's scale".
