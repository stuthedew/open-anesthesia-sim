---
id: PL-BQB6
title: Where the window's right edge cuts across an Area while the page scrolls sideways, a line of the Area's header or its View's pinned row is cut mid-sentence, such as the schematic's 'Tensions are in % of 1 atm.'
status: untriaged
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/pinned_heading.py
added: 2026-11-28
filed-pr: 2355
---

**Problem.** A window narrower than the Areas' least widths scrolls the page sideways. Where the window's right edge then cuts across an Area, a line of the Area's header or of its View's pinned row runs past that edge and is cut mid-sentence, while a short value at the Area's left stays wholly in view. The schematic's pinned row can read "Tensions are in % of 1" with " atm." cut off, which could be read as a different unit. `PL-DKQ5` made each line start at the left edge of the part in view, so a line is now always read from its start; its end can still be cut.

**What was measured** (`PL-DKQ5`, 2026-11-28, offscreen platform, the container's font). Four Areas in a row (the View under test, then three of the compartment schematic, agent cost, wash-in and concentration chart) in a window 1400 by 1000 scroll the page about 685 px sideways. Checking that every line of the header and pinned row is wholly in view wherever a value of its Area is, rather than that each line starts in view, failed for all eight registered Views: at the page's left end, the Area cut by the right edge showed a short label whole while its pinned row's "Model outputs — not measurements." or its View chooser's name was cut. Shipped Workspaces at 1366 by 768 and larger do not scroll sideways, so this takes an arranged layout of several wide Areas.

**Direction.** The safety standard asks that a value not be shown cut where the cut part could be misread (the schematic paints a label only while whole, `PL-GWTR`). Three routes to weigh, each with a source to find first: elide a cut line with an ellipsis at the part's right edge, so the reader sees it continues; let the heading span only the part in view and wrap its lines there, which makes it taller while scrolled; or hide a line cut at its end, as the canvas does. Whether a required unit line may be shown elided is the owner's call (`PL-KBBJ`), so research the platform guides first and put the choice to the owner through the coordinator.

**Two more lines that are cut the same way** (`PL-DKQ5`'s review, 2026-11-28). A run's name in the compartment schematic is cut at its end where the part of its run in view is narrower than the name, because the name line keeps a margin rather than sliding whole, so that the compartments' names stay over their containers. The share caption beside the name is not drawn while it is cut, so it is never shown in part; whichever route this item takes should treat the caption the same way.

**Done when** `tests/integration/test_area_header_page_scroll.py`'s sideways test checks that each line is wholly in view, or shown with a visible sign that it continues, wherever a value of its Area is.
