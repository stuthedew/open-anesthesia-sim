---
id: PL-BQB6
title: Where the window's right edge cuts across an Area while the page scrolls sideways, a line of the Area's header or its View's pinned row is cut mid-sentence, such as the schematic's 'Tensions are in % of 1 atm.'
priority: P1
effort: M
status: needs-decision
classes: defect, safety
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/pinned_heading.py
added: 2026-11-28
filed-pr: 2355
payoff: a user who arranges Areas wider than the window reads each header line, unit lines included, whole or marked as continuing
---

**Problem.** A window narrower than the Areas' least widths scrolls the page sideways. Where the window's right edge then cuts across an Area, a line of the Area's header or of its View's pinned row runs past that edge and is cut mid-sentence, while a short value at the Area's left stays wholly in view. The schematic's pinned row can read "Tensions are in % of 1" with " atm." cut off, which could be read as a different unit. `PL-DKQ5` made each line start at the left edge of the part in view, so a line is now always read from its start; its end can still be cut.

**What was measured** (`PL-DKQ5`, 2026-11-28, offscreen platform, the container's font). Four Areas in a row (the View under test, then three of the compartment schematic, agent cost, wash-in and concentration chart) in a window 1400 by 1000 scroll the page about 685 px sideways. Checking that every line of the header and pinned row is wholly in view wherever a value of its Area is, rather than that each line starts in view, failed for all eight registered Views: at the page's left end, the Area cut by the right edge showed a short label whole while its pinned row's "Model outputs — not measurements." or its View chooser's name was cut. Shipped Workspaces at 1366 by 768 and larger do not scroll sideways, so this takes an arranged layout of several wide Areas.

**Why it matters.** A unit line cut mid-sentence can be misread. "Tensions are in % of 1", with " atm." cut off, reads as a different unit, while the tensions below it are drawn whole. `CLAUDE.md`'s safety standard counts a correct number shown with a wrong or missing unit as a safety failure.

**Generator check.** `PL-DKQ5` is the head for this fault, and its `generator: spent` names the check that holds it: `tests/integration/test_area_header_page_scroll.py` fails where a value is seen without its Area's header and pinned row. That check asks only that each line starts in view, so a line cut at its end passes it. This item is that gap, and its done-when closes it by making the sideways test ask that each line is wholly in view or marked as continuing.

**Direction.** The safety standard asks that a value not be shown cut where the cut part could be misread (the schematic paints a label only while whole, `PL-GWTR`). Three routes to weigh, each with a source to find first: elide a cut line with an ellipsis at the part's right edge, so the reader sees it continues; let the heading span only the part in view and wrap its lines there, which makes it taller while scrolled; or hide a line cut at its end, as the canvas does. Whether a required unit line may be shown elided is the owner's call (`PL-KBBJ`), so research the platform guides first and put the choice to the owner through the coordinator.

**Two more lines that are cut the same way** (`PL-DKQ5`'s review, 2026-11-28). A run's name in the compartment schematic is cut at its end where the part of its run in view is narrower than the name, because the name line keeps a margin rather than sliding whole, so that the compartments' names stay over their containers. The share caption beside the name is not drawn while it is cut, so it is never shown in part; whichever route this item takes should treat the caption the same way.

**The same cut at an Area's own right edge** (`PL-DKQ5`'s adversarial review, 2026-11-28). While the page is scrolled sideways, an Area's header and pinned row start at the left edge of the Area's part in view and end at the Area's right edge, but never narrower than their widest line needs. Where the Area's part in view is narrower than that, the Area's right edge cuts the end of the longest lines, beside the next Area rather than at the window's edge. Measured with the schematic in the left Area of four, the page scrolled 460 px sideways: "Tensions are in % of 1 atm." showed as "Tensi" while the runs' tensions were drawn whole below it. The route this item takes applies to this edge as well.

**Done when** `tests/integration/test_area_header_page_scroll.py`'s sideways test checks that each line is wholly in view, or shown with a visible sign that it continues, wherever a value of its Area is.

**Decision needed.** When the window's edge cuts across an Area while the page scrolls sideways, should the Area's header lines and its View's pinned row wrap to fit the part in view, or end in an ellipsis? It is the owner's call, because it decides whether a required unit line, such as the schematic's "Tensions are in % of 1 atm.", stays readable (`PL-KBBJ`). The question went to the owner through the coordinator on 2026-11-28.

1. **Wrap.** Every line stays whole. The header grows taller while the page is scrolled sideways and the part in view is narrow, so the View under it moves down.
2. **Ellipsis.** The header keeps its height. A cut line ends in "…", so the reader sees that it continues, and scrolls to read the rest of it.

**Recommendation: wrap.** Apple's Human Interface Guidelines, § "Typography" (read 2026-11-28 from `developer.apple.com`): "Avoid truncating text in scrollable regions unless people can open a separate view to read the rest of the content", and a label can avoid truncation by using "as many lines as needed". Microsoft's Windows UX guide, § "Text" (`learn.microsoft.com/windows/win32/uxguide/text-ui`, read 2026-11-28): truncated text "indicates poor layout", so "Strive for layouts and default window sizes that eliminate or reduce the amount of truncated text". Microsoft's Windows app typography page (`learn.microsoft.com/windows/apps/design/style/typography`, read 2026-11-28) prefers an ellipsis to a plain cut where text must be cut, which applies to a single word wider than the part in view. Blender's manual, § "Regions", lets a region that overflows be scrolled, and GNOME's typography page says nothing on truncation. Hiding a cut line, the third route above, has no support in any of these.

**How often a user meets it** (measured 2026-11-28, offscreen platform, the container's font). Each shipped Workspace was shown at 1024 by 768, 1280 by 720, 1280 by 800, 1366 by 768 and 1440 by 900. The window does not go narrower than 1136 px, and no shipped Workspace scrolled the page more than 1 px sideways. Only a row of Areas that a user arranges wider than the window reaches the cut.

**Gate.** The cut was present before v0.7.0's debt list froze, so the item re-enters that list (`ROADMAP.md` § "Which findings re-enter the gate"). It is not deferred: deferring a `safety` item needs a record that no user can see a wrong value now, and a unit line cut to "% of 1" can be misread.
