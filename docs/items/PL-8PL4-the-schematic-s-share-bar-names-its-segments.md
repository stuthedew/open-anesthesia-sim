---
id: PL-8PL4
title: The schematic's share bar names its segments only in a text list under it, so a reader cannot tell which colour is fat, and its caption reads as agent held over the whole run rather than at this instant
status: untriaged
feature: schematic
added: 2026-11-26
---

**Problem.** The schematic's share bar names its segments only in a text list under it, so a reader cannot tell which colour is fat, and its caption reads as agent held over the whole run rather than at this instant

**How it was found.** The project owner, test-driving main at `971a9cb9` on
2026-11-26, could not tell which colour was fat and read "Share of the agent
the run holds" as a total over the run. He asked whether the bar is a standard
figure or one made up because the data were there. The values were right: 650
and 420 mL out of 1,092 mL are 60% and 38%. Fat's container is filled to
0.09% of a 5.4% scale, about 2 px, so its colour barely shows there either.

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
pages were read in full on 2026-11-26. Here four of six segments are below 1%,
and the names sit in a list under the bar.

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
