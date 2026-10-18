---
id: PL-05M4
title: The inert splitter handles keep the host's surface under a dark appearance, because a disabled widget draws from the Disabled colour group this project leaves to the platform
priority: P3
effort: S
status: done
classes: ux
feature: chrome-colour-audit
milestone: v0.5.29
touches: docs/MODEL.md
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; classed by PL-14QR's 2026-09-22 triage pass
added: 2026-09-22
closed: 2026-10-18
pr: 1602
payoff: docs/MODEL.md stops telling a reader that the Area borders show the host's dark surface, which they no longer do
verify: ! grep -q 'the inert splitter handles keep the host' docs/MODEL.md
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

**Why it matters, and what it costs.** On a machine set to Dark, the dashboard's section handles
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

**Decision needed.** Which of the three routes above, and when. Triaged
2026-09-22 (`PL-14QR`, triage) to `needs-decision` rather than answered, because the choice is
between a colour a learner sees on a dark host and a rule that holds elsewhere
in the interface. The recommendation above - route 3 now, route 2 inside
planned-milestone item 34 - is this brief's, and still waits on the project
owner.

**Decided 2026-10-18 in the product decision batch's design round: route 3
now, and route 2 arrives with `PL-W9P6`.** The recommendation above was
conditional on planned-milestone item 34 being scoped. It now is: `ROADMAP.md`
§ "v0.6.0 - the layout is the reader's", Required scope entry 2, is `PL-W9P6`
(the layout adapter), and that entry says it is "where v0.4.26's inert
handles go live". A live handle is enabled, so it draws from the declared
`Active` group, and the dark bar goes away with no change to the `Disabled`
group. Route 1 was refused for the reason given above: a declared disabled
surface under the platform's disabled text grey is a trap for any control
added later. This is an obvious call, so it was decided here rather than put
to the project owner.

[superseded 2026-10-18] So this item is blocked on `PL-W9P6`. What is left after it is small. Invert
the handle half of
`tests/integration/test_dark_appearance.py::test_declaring_the_application_leaves_its_disabled_colours_to_the_platform`
so it holds a light handle under a dark host. Then remove the known limit
from `docs/MODEL.md` § "Color contrast, and the standard this interface is
held to". The close-out's docs sweep will also find the sentence in
`.claude/rules/ui-color.md` that names this item. If `PL-W9P6`'s own build makes those changes, close this item as done
under that pull request.

**`PL-W9P6` built, 2026-10-18.** The handles are live and enabled, so the gap
between two Areas shows the page's `BACKGROUND` under a dark host. The handle
half of the dark-appearance test is inverted: the Disabled-group test now uses
a disabled widget of its own, and
`test_the_border_between_two_areas_shows_the_page_rather_than_the_host` holds
the fix. The sentence in `.claude/rules/ui-color.md` is updated. What is left
is the known-limit sentence in `docs/MODEL.md` § "Color contrast, and the
standard this interface is held to", which another thread holds this week.
Removing it closes this item.

## Re-confirmed 2026-10-18: gone, and the sentence fixed

`PL-W9P6` (`#1592`) made the splitter handles live, so they are enabled and no
longer draw from the `Disabled` colour group.
`test_the_border_between_two_areas_shows_the_page_rather_than_the_host` in
`tests/integration/test_dark_appearance.py` holds that the border shows the
page's `BACKGROUND` under a dark host. Route 2 above happened as part of item
34, as the recommendation expected. What was left was the `docs/MODEL.md`
sentence, which now says the handles used to keep the host's surface and no
longer do. Fixed in `PL-W54S`'s pull request.
