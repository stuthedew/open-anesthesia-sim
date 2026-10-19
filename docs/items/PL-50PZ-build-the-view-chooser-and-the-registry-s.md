---
id: PL-50PZ
title: Build the View chooser and the registry's required-reachable flag, which is what makes docs/MODEL.md's accounting tier reachable from every Workspace and not removable from the application
priority: P1
effort: M
status: done
classes: safety, anticipated
feature: interface-areas
milestone: v0.5.31
touches: src/anesthesia_sim/app/, docs/MODEL.md, docs/ARCHITECTURE.md, tests/integration, tests/unit/test_view_registry.py, tests/unit/test_contrast_check.py, tools/contrast_check.py
blocked-by: PL-R1WQ, PL-WV9K
added: 2026-09-16
closed: 2026-10-18
pr: 1612
payoff: the agent accounting can be brought on screen from every Workspace through the interface alone, and a build that does not register it fails
verify: grep -q 'def test_the_accounting_can_be_brought_on_screen_in_any_area_of_any_workspace' tests/integration/test_view_chooser.py
---

**Problem.** Build the View chooser and the registry's required-reachable flag, which is what makes docs/MODEL.md's accounting tier reachable from every Workspace and not removable from the application

**Why it matters.** `docs/MODEL.md` puts the agent accounting - cumulative
delivered, cumulative exhausted, total stored, and the mass-balance residual
with its absolute error - in the one required tier a Workspace may omit: "They
must stay reachable in every layout, and must not be removable from the
application." That is the one class whose guarantee cannot be structural
presence, so it has to become an invariant of the registry and of the chooser
instead. `ROADMAP.md` § "Development rules for scientific milestones" treats
mass accounting as a release gate rather than an optional diagnostic, which is
what makes this a requirement rather than a convenience.

**Done when.** "Reachable" has a written definition in `docs/MODEL.md`; the
View registry records which kinds are required-reachable and a build lacking
one fails; the chooser offers them from any Workspace; and a test asserts that
from each shipped Workspace the accounting values can be brought on screen
through the interface alone, and that a Workspace naming none of them still
leaves them reachable.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 16.

---

## Design round 2026-09-27: recommendations

Recommendations, not decisions: the thread that records the project owner's
answer marks each `(project owner, DATE, ratified)` or replaces it. None of
these is a learner-visible fork; they are taken under the delegated call
unless the owner objects.

**Q1. The written definition of *reachable* for `docs/MODEL.md`.**
**Recommendation:** *A View kind is reachable in a Workspace when a reader
can bring it on screen from that Workspace through the interface alone, in a
bounded number of steps, without a drag or a file edit.* Two mechanisms make
it true for every kind at once: every Area's chooser lists every registered
kind, unfiltered, and `set_view` places the chosen one; and a menu and
keyboard route exists beside the pointer one (`PL-M352`). The tree is never
empty by construction (closing the last Area leaves one empty Area), so there
is always somewhere to place a View.

**Q2. The registry flag and what fails a build.** `required_reachable` on
the registry entry (`PL-R1WQ`), and a module-level
`REQUIRED_REACHABLE = ("agent_accounting",)` that tests read: the tag is
registered, its entry carries the flag and a factory, the chooser built from
each shipped Workspace lists it, `set_view` places it, and the values appear
by `PL-904Y`'s predicate. A build lacking any of those fails in CI, which is
what "not removable from the application" means here: the registry is code.

**Q3. "From any Workspace", including one naming none of them.** The
chooser reads the registry, not the Workspace, so a Workspace whose file
names no accounting Area still offers it. The test loads a fixture Workspace
of two charts, opens the chooser in one Area, chooses the accounting kind,
and asserts the values. Since the shipped defaults omit the accounting View
(`PL-KXTL`, project owner 2026-09-16), the chooser is its only route in the
shipped set, and this test is what guards the guarantee.

**Q4. Where the chooser sits.** In the container-owned Area header
(`PL-TH35` Q11), one control per Area, listing kinds by registry title;
Blender's editor-type menu occupies the same position. Its appearance is
entry 20's.

## Answers 2026-09-27

**Every recommendation above: ratified** (project owner, 2026-09-27,
ratified, over the alternative each names). The one decision the owner
specified otherwise is `PL-WV9K` Q4: layouts are saved by an explicit "Save
as default" action in the layout menu, not automatically; `PL-WV9K`
§ "Answers 2026-09-27" carries that design.

## Ready since `PL-R1WQ`, 2026-10-18

The registry is `src/anesthesia_sim/app/view_registry.py`, and the Workspace
is `PL-WV9K`'s, so both blockers are done. `required_reachable` is a new field
on `RegisteredView`, and the check that a build lacking a required kind fails
belongs beside `retirements` in that module. The chooser also owes the Area
notice two things `PL-R1WQ` left out because no menu existed: `PL-DB5G` Q2's
line "Choose a View from the menu above. The saved name is kept until you
do.", and the explicit offer of a renamed View's new tag (`PL-R1WQ` Q3).
`missing_view_text` writes the notice's body.

## Built 2026-10-18

**Re-confirmed against the tree: still true, one gap wider.** The registry
(`PL-R1WQ`) and the Workspace (`PL-WV9K`) are done, but no Area header
existed: `PL-MS34` said `PL-W9P6`'s adapter would build it, and `PL-W9P6`
shipped without one. The chooser lives in the header (Q4), so this item
builds the header too, with the chooser as its only control. The run's name
and the Area menu stay `PL-7Z84`'s and `PL-M352`'s.

**What was built.**

- `RegisteredView.required_reachable`, and `REQUIRED_REACHABLE =
  required_kinds(REGISTERED, AGENT_ACCOUNTING)` in `app/view_registry.py`.
  `required_kinds` refuses a required kind that is not registered or not
  flagged, and a flagged kind no requirement names. It runs when the module
  is imported, so a build that drops the accounting View fails on import
  (Q2). The tuple states `docs/MODEL.md`'s requirement and the flag states
  the entry, and the check holds the two to agree.
- `AreaFrame` and `ViewChooser` in `app/area_layout.py`: every Area is drawn
  as a header row, a 1px rule and its content. The chooser is a flat menu
  button whose menu lists every registered kind in registry order, the
  current one checked (`PL-RBXL`). A choice calls `LayoutModel.set_view`
  through `AreaLayout.choose_view` and emits `layout_changed`.
- `PL-DB5G` Q2's last line is now in the unknown-kind notice, and a renamed
  tag's notice offers a button showing the new tag (`PL-R1WQ` Q3), which the
  reader must press.
- The definition of reachable is in `docs/MODEL.md` § "Minimum displayed
  outputs", beside the accounting tier (Q1).
- `tests/integration/test_view_chooser.py` loads each shipped Workspace and a
  fixture of two charts into a real dashboard, and from every Area chooses
  the accounting through the chooser's menu entry. It asserts the five
  amounts are then on screen in that Area and were not before (Q3).

**Two states the chooser makes reachable, decided here as internal structure
inside the ratified approach.** The dashboard cannot yet build every
registered View once per Area: the wash-in plot and the parameter controls
have no widget of their own, and the chart panel and the accounting sidebar
exist once each, until `PL-TH35` and `PL-9LNF` land. So `view_for` may now
return None, and the Area shows "This View cannot be shown in an Area of its
own yet."; and where the caller hands back a widget another Area already
shows, the second Area in reading order shows "This View is already shown in
another Area." Both are `AreaNotice`s, so the reader meets `PL-DB5G`'s one
shape, and neither shows a value. The alternative refused was filtering the
chooser to the kinds the caller can draw. `PL-RBXL` Q2 ratified a menu of
every registered kind, and a filtered menu would change with the dashboard's
internals rather than with the registry. The wording of both notices and
the button label are placeholders (project owner's rule of 2026-10-18).

**Placeholders recorded** (styling, wording and placement, project owner,
2026-10-18): the header's horizontal padding of half `PANEL_PADDING`, the
chooser's 2px by 6px padding, the menu's `MUTED` edge, the notices' wording
and the "Show 'X'" label. The header asks for no width of its own, so a
narrow Area clips the title rather than being held wider; what an Area
needs is `PL-K285`'s.

**The pixel budget.** The header row takes one text row above the Areas,
which is the one Area header `PL-84QX` budgeted.
