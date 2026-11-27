---
id: PL-8PL4
title: The schematic's share bar names its segments only in a text list under it, so a reader cannot tell which colour is fat, and its caption reads as agent held over the whole run rather than at this instant
priority: P2
effort: M
status: done
classes: defect, ux
feature: schematic
touches: src/anesthesia_sim/app/compartment_schematic.py, src/anesthesia_sim/app/qt_schematic.py, docs/INTERFACE.md
deferred-from: v0.7.0 - filed on 2026-11-26, after the gate froze; the owner asked on 2026-11-27 for it to land before the cut; every share it shows was right, so no learner sees a wrong value
added: 2026-11-26
closed: 2026-11-27
pr: 2326
payoff: a learner reads each compartment's share of the agent under its own container, with no colour key to decode, and does not take the shares for agent counted over the whole run
tests: tests/integration/test_compartment_schematic_view.py::test_each_share_bar_is_painted_to_its_share_on_one_scale_under_its_own_label, tests/unit/test_compartment_schematic.py::test_each_label_prints_its_own_compartment_s_share_in_whole_percent, tests/unit/test_compartment_schematic.py::test_the_share_caption_says_the_shares_are_of_the_agent_held_at_this_instant
---

**Problem.** The schematic's share bar names its segments only in a text list under it, so a reader cannot tell which colour is fat, and its caption reads as agent held over the whole run rather than at this instant

**How it was found.** The project owner, test-driving main at `971a9cb9` on
2026-11-26, could not tell which colour was fat and read "Share of the agent
the run holds" as a total over the run. He asked whether the bar is a standard
figure or one made up because the data were there. The values were right: 650
and 420 mL out of 1,092 mL are 60% and 38%. Fat's container is filled to
0.09% of a 5.4% scale, about 2 px, so its colour barely shows there either.

**Why it matters.** An anesthesiologist could not tell which compartment held
38% of the agent, and took the shares for agent counted over the whole run. A
figure an expert misreads teaches a resident the wrong thing, even when every
number in it is right.

**What the bar is for.** The containers fill to tension, so muscle and fat
look nearly empty while they hold most of the agent (`ROADMAP.md` § "v0.7.0 -
the schematic", `PL-S79P`). The stored agent is what returns to the blood on
washout. Eger and Saidman teach the same point: "Anesthetic in tissue depots
and the solubility of the anesthetic in blood ... will determine the rate of
decrease of anesthetic in the arterial circulation during recovery", and an
appreciably soluble agent "will recirculate, and will delay recovery" (Eger EI
II, Saidman LJ. Illustrations of inhaled anesthetic uptake, including
intertissue diffusion to and from fat. Anesth Analg 2005;100:1020-33,
printed p. 1030; full text read from the private reference corpus).

**How the literature draws it, read 2026-11-26.**

1. Gas Man fills each container "to a height representing partial pressure or
   tension in that compartment" (Gas Man Workbook, printed p. 11), and shows
   tensions "as vertical heights, either in containers or on graphs" (printed
   p. 24). It defines capacity as volume times the tissue/gas coefficient
   (Eq. 3-1, p. 24). Read from the private reference corpus.
2. Eger and Saidman draw each tissue group as a circle whose area is its
   capacity, referenced to the FRC, with a speckled inner circle for "the
   anesthetic occupancy of the tissue depots" (Fig. 4 legend, p. 1023). They
   repeat the drawing at 5, 50 and 200 min. They say the figures "illustrate
   concepts but are not necessarily precise (quantitative)" (p. 1020).
3. Neither draws a share bar. The bar was this project's choice at scoping
   (project owner, 2026-10-25, ratified, over containers drawn to scale and
   over Gas Man's Picture as it is), because a container whose width is its
   capacity would be 1 to 7 px wide for four of the six compartments.

**Why a single stacked bar is the weak form.** Wilke's table of the usual
part-to-whole charts marks stacked bars as failing "Allows easy visual
comparison of the relative proportions" and "Works well when the whole is
broken into many pieces", and says "a single column of stacked bars ... looks
awkward" (Wilke CO. Fundamentals of Data Visualization. O'Reilly; 2019. Ch. 10,
Table 10.1, https://clauswilke.com/dataviz/visualizing-proportions.html).
Side-by-side bars "are preferred when we want to directly compare the
individual fractions". On legends: "legends always put an extra mental burden
on the reader", and "Whenever possible, design your figures so they don't need
a legend" (ch. 20, https://clauswilke.com/dataviz/redundant-coding.html). Both
pages were read in full on 2026-11-26. In the owner's run, four of the six
segments were 1% or less, and the names sat in a list under the bar.

**Options, with mock-ups in `/mnt/project-files/v0.7.0/pl-8pl4-screens/`.**

1. **Each container gets its share.** Its label gains a fourth line, "38% of
   the agent", and a short bar under it on a common scale, so the six shares are
   side-by-side bars named by position. The separate bar and its three text
   lines go. One caption line says the shares are of all the agent in the
   circuit and body at this instant. **Recommended**, because it is the form
   Wilke prefers for comparing fractions and needs no key.
2. **Keep the bar and label it.** Name the two large segments inside the bar,
   group the four small ones, and reword the caption to say "now".
3. **Remove the bar.** The mL amounts stay under each container.

**Owner-ask.** Which form, recorded here when answered. The share's formula,
`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
share bar assert", does not change under any option. That section's share-bar
paragraph and its tests change with the option chosen.

**Answered 2026-11-27: option 1, each container gets its share** (project
owner, 2026-11-27, ratified, over keeping the one bar with its segments
labelled and over removing it). He answered "Agree with recs" on the decision
card in this thread, and "Agree with best practice" in the project chat, and
asked for it to land before the v0.7.0 cut.

**Overlap with #2325 and `PL-P83G`, noted 2026-11-26.** #2325 merged on
2026-11-26 as `0fbd7a8d`. The controls-placement
thread's pull request #2325 moves the share bar and its naming lines above the
containers in `RunSchematic` and adds a test that the bar is never on screen
without its naming lines. It files `PL-P83G`: with two runs compared, the second
run's bar can be on screen while its naming lines are scrolled out of the Area.
Option 1 removes the separate bar and puts each share in its container's
label, so it closes `PL-P83G` as well. Build on `main` after #2325 merges, and
retire or rewrite its new test with the bar.

**Generator check.** No generator. The single bar was one scoping choice
(`PL-S79P`), and no other View draws a part-to-whole figure. The rule that
would have caught it, that a proposed figure says how the literature draws the
same quantity, is now a standing instruction in the project's memory.

**Done when.** Each container's label ends with its share of all the agent
that the circuit and body hold, "38% of the agent", and a bar under the label is
filled to that share. The six bars are one length. The separate bar and its
three lines are gone, and one caption line says that the shares are of the
agent held at this instant, circuit included. While the run holds no agent,
each share line shows a dash, each bar is empty, and the caption line says why.
`docs/INTERFACE.md` § "The compartment schematic: what its heights, amounts and
share bar assert" describes the new form, and `PL-P83G` closes with the bar
it was about.

**Docs checked 2026-11-27.** `docs/INTERFACE.md` (the schematic section, and
the amounts paragraph under § "Displayed precision"), `docs/VERIFICATION.md`
(the hazard row on reading a height as an amount), `docs/ARCHITECTURE.md` (the
package map and the snapshot paragraph), `ROADMAP.md` (v0.7.0's scope entry 4,
its definition of done and item 33), `src/anesthesia_sim/data/workspaces/__init__.py`
(the Maintenance Workspace), the docstrings in `app/controller.py` and
`app/formatting.py`, and the lines `tools/doc_check.py candidates` printed for
`tools/contrast_check.py`. `tests/reference/test_compartment_amounts_against_oracles.py`
says the schematic draws "its share bar" from the amounts, which is still true
of the six bars, so it is unchanged.

**Reviews, 2026-11-27.** Both blind review passes named the same should-fix
finding: at 1366×768 the share caption sat under the scale line, below the
fold. `311d8fe6` moved it under the containers, and the Maintenance lesson test
now fails on the old order. A code review followed, and `73b28e92` takes its
fixes. The share text is now worked out from the share each time, so a label
and its bar cannot disagree. Each bar's fill starts inside its outline, and the
documents' wording was corrected. Two of its findings are not this item's
work, and are filed: `PL-3NGZ` (a label's run name, tension unit or the share
caption can scroll away from it at 1366×768) and `PL-KQ0S` (the caption says
the shares are of all the agent in the body, which the six containers do not
hold). Its request to make the `docs/INTERFACE.md` heading say "share bars" was
declined, because 13 references cite the heading as it is. A test review
followed, and `380b0c71` takes its fixes: four mutants of the share-bar code
that the tests had let through now fail them. `bin/docket verify --self
PL-8PL4 PL-P83G` accepted both items, with 31 mutants caught and none missed on
a changed line.
