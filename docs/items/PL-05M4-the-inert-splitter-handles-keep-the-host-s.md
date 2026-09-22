---
id: PL-05M4
title: The inert splitter handles keep the host's surface under a dark appearance, because a disabled widget draws from the Disabled colour group this project leaves to the platform
status: untriaged
feature: chrome-colour-audit
touches: src/anesthesia_sim/app/qt_widgets.py, tests/integration/test_dark_appearance.py, docs/MODEL.md
added: 2026-09-22
---

**Problem.** The inert splitter handles keep the host's surface under a dark appearance, because a disabled widget draws from the Disabled colour group this project leaves to the platform

**Found while implementing `PL-KRZW`** (the application-palette declaration),
and measured rather than inferred: after `declare_application_colours` the
page's scroll bar goes from 94.3% of its pixels darker than mid-grey to none,
and the splitter handle stays at the host's `#323232` exactly as it was.
`tests/integration/test_dark_appearance.py::test_declaring_the_application_leaves_its_disabled_colours_to_the_platform`
asserts both halves, so this is characterised rather than lurking.

**Why it happens.** `qt_widgets.freeze_splitter_handles` disables every handle,
so a splitter's sections cannot yet be dragged (`inert_splitter`, `PL-25KS`). A
disabled widget draws from the `Disabled` colour group, and all three colour
mechanisms in this interface leave that group exactly as the platform supplied
it - which is what `.claude/rules/ui-color.md` requires and what
`check_authored_disabled_colours_are_measured` enforces. So the handles are
host-coloured by the rule that keeps the rest of the interface honest, not by
an omission in `PL-KRZW`.

**What it costs.** On a machine set to Dark, the dashboard's section handles
are dark bars in an otherwise light window. They carry no text and no clinical
value, so this is an appearance defect rather than a legibility or safety one
- which is why it was filed rather than fixed inside `PL-KRZW`.

**The three routes, none of them obviously right, which is why this is an
item and not a fix.**

1. **Declare the `Disabled` group for the surface roles only** (`Window`,
   `Button`, `Base`) and leave the text roles to the platform. Smallest change.
   The hazard is the one the placeholder already demonstrated in `PL-RKRY`: a
   platform's disabled *text* grey is chosen against a platform's disabled
   *surface*, so putting a light surface under a light-grey label is the
   half-fix that makes a later control worse than leaving it alone. Nothing in
   the interface would be hurt today - the only disabled things are the
   handles, the three transport buttons (whose label `transport_button_stylesheet`
   declares) and the agent selector (hidden by the same expression) - but it
   is a standing trap for a control added later.
2. **Stop disabling the handles**, and make them non-draggable another way - a
   zero-range or event-filtered handle that stays enabled. Keeps the `Disabled`
   group untouched, and `ROADMAP.md` planned-milestone item 34 (the Blender-style
   area system) will want draggable handles anyway, so this may be obviated.
3. **Leave it.** The cost is cosmetic and confined to dark hosts.

**Recommendation: 3 until item 34 is scoped, then 2 as part of it.** Route 1
buys a handle colour at the price of a rule that is load-bearing elsewhere.

**Done when** the project owner has picked a route; if 1 or 2, it is built and
`test_dark_appearance.py`'s handle assertion is inverted to hold the fix;
`docs/MODEL.md` § "Color contrast, and the standard this interface is held to"
is updated either way, since it currently records this as a known limit.
