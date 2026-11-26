---
id: PL-9WDN
title: The interface has no written design language: no type scale, spacing scale or rule for surfaces, colour and standing text, so each View is styled on its own and the whole reads as unprofessional
status: untriaged
feature: interface-design-review
added: 2026-11-26
---

**Problem.** The interface has no written design language: no type scale, spacing scale or rule for surfaces, colour and standing text, so each View is styled on its own and the whole reads as unprofessional

**How it was found.** Test-driving main at `971a9cb9` on 2026-11-26, the
project owner said the interface "still feels amateur" as a whole, that
iterating on it feels like polishing, and asked what UI/UX best practice is
for this kind of software and what a best-practice design language is.

**What the screen shows, measured 2026-11-26** on the Maintenance Workspace
at 3h8m11s of a sevoflurane run, rendered offscreen at 1500 by 1000
(`/mnt/project-files/v0.7.0/design-language/1-now-annotated.png`):

1. The brightest element is the version string, in a yellow pill.
2. The readouts are seven separate rounded cards, and the control-change
   record is an eighth at a different height.
3. The concentration chart's legend is five lines of prose above the plot,
   naming line styles in words, so the plot gets about half its View.
4. The schematic carries six standing caption lines.
5. The largest block of saturated colour is the share bar (`PL-8PL4`).
6. View headings are 12 px bold, smaller than the 14 px readout labels.
7. The Parameters View nests cards inside its panel, and each value sits
   above its slider.
8. Half the schematic's Area is empty while the chart is cramped.

Visible widgets alone use 10 combinations of size, weight, slant and colour,
at 12, 13, 14 and 22 px, before the chart's and the schematic's painted text.
Nothing written states which size, weight or surface a new element takes, so
each View chose its own.

**What a design language is.** It is a short written set of rules that every
surface follows: a type scale, a spacing scale, one way to make a surface,
colour roles with fixed meanings, and the patterns for things that recur, such
as a readout, a chart and a control.

**Sources read in full on 2026-11-26, and what each gives.**

1. Apple Human Interface Guidelines, Typography
   (https://developer.apple.com/design/human-interface-guidelines/typography):
   macOS body text is 13 pt and the minimum 10 pt; the built-in macOS styles
   are Title 3 15 pt, Headline 13 pt bold, Body 13, Callout 12, Subheadline 11
   and Footnote 10. "Minimize the number of typefaces you use", and "Adjust
   font weight, size, and color as needed to emphasize important information".
2. Apple HIG, Color: "Avoid using the same color to mean different things."
   Layout: "Group related items ... you might use negative space, container
   shapes, or separator lines", and "Align elements to make them easier to
   scan".
3. Nielsen Norman Group, visual hierarchy
   (https://www.nngroup.com/articles/visual-hierarchy-ux-definition/): use
   "no more than 3 sizes"; "Don't use too many colors"; a container helps
   grouping, but "These additional elements can create visual clutter, so use
   them sparingly"; check the result with a squint test and with target users.
4. Nielsen's heuristics (https://www.nngroup.com/articles/ten-usability-heuristics/):
   number 8, "Every extra unit of information in an interface competes with
   the relevant units of information"; number 4, consistency and standards.
5. Nielsen Norman Group, aesthetic-usability effect
   (https://www.nngroup.com/articles/aesthetic-usability-effect/): users
   perceive attractive products as more usable, and the effect "can mask UI
   problems during usability testing". So looks are worth paying for, and
   are not evidence of usability.
6. ISA-101 high-performance HMI, as described in "Going Gray: A New HMI
   Standard" (https://control.com/technical-articles/going-gray/): "Color
   should be used sparingly and only where attention is needed such as alarms
   and abnormal equipment and / or instrument modes or states", on mostly
   grey graphics. The standard itself is paywalled and was not read.
7. Wilke, Fundamentals of Data Visualization (https://clauswilke.com/dataviz/),
   ch. 19 and 20: avoid "coloring for the sake of coloring", and "Whenever
   possible, design your figures so they don't need a legend", by labelling
   lines directly.
8. IBM Carbon, spacing and type (carbon-design-system/carbon-website on
   GitHub): a spacing scale of 2, 4, 8, 12, 16, 24, 32 px and up, and a
   "productive" type set for "product spaces, where users benefit from a more
   condensed treatment of content to maintain focus on tasks".

**Recommendation, put to the owner 2026-11-26.** Stop correcting surfaces one
at a time. Run planned-milestone item 33, the interface pass, which
`ROADMAP.md` already places right after v0.7.0, and start it by writing the
design language below into one short document, with its values as tokens in
`app/theme.py` and a check that refuses a size, colour or radius outside them.
Then restyle every surface against it in one pass. Do not adopt a third-party
design system whole: Carbon and Material are web systems, and their Qt ports
are outside dependencies. Borrow their scales instead.

1. Neutral chrome. Colour only for agent identity (ISO 5360), compartment
   identity in data, and a state that needs attention.
2. One family, two weights, three text sizes taken from the macOS styles
   (11, 13 and 15 px), plus one size for readout values. No italics to carry
   meaning.
3. Group by space and alignment, with one level of container. The readouts
   become one strip, and no card sits inside another.
4. One spacing scale in steps of 4 and 8 px.
5. Charts label their own lines and reference lines; no legend block.
6. A label, unit or axis title carries meaning; any longer explanation goes
   behind an information button (`.claude/rules/ui-reader.md`).
7. Controls and required values stay in one place across Workspaces, which
   `PL-YS8M` raises for the Parameters controls.

`/mnt/project-files/v0.7.0/design-language/2-restyle-mockup.png` is an HTML
mock-up of the same screen and values under these rules. It is a starting
point for item 33's design round, not a decided look.
