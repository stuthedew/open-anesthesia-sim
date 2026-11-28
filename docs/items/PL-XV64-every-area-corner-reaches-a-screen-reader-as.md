---
id: PL-XV64
title: Every Area corner reaches a screen reader as 'Area corner', every Area border as 'Area border', and the plot controls of two Areas that show the same kind of View share their names, so a screen-reader user cannot tell which Area a control acts on
priority: P3
effort: S
status: ready
classes: defect
feature: interface-areas
touches: src/anesthesia_sim/app/area_layout.py, src/anesthesia_sim/app/views.py, tests/integration/test_keyboard_focus.py, src/anesthesia_sim/app/view_contract.py, src/anesthesia_sim/app/qt_chart.py, src/anesthesia_sim/app/qt_agent_price.py, src/anesthesia_sim/app/qt_widgets.py, docs/INTERFACE.md, tests/integration/test_layout_adapter.py, tests/integration/test_view_contract.py
deferred-from: v0.7.0 - found after the freeze, not safety or science, and no user sees a wrong value from it: the Area menu each corner opens names its Area, so the release waits only on the owner test drive (filed 2026-11-28)
added: 2026-11-28
payoff: a screen-reader user who reaches an Area corner or border hears which Area it acts on
---

**Problem.** Every Area corner reaches a screen reader as "Area corner" and
every Area border as "Area border", so a screen-reader user cannot tell which
Area a corner or border acts on.

A third case has the same cause. `PL-YSFX` names each plot's controls with its
View's title, such as "Time base, Concentrations". The Area menu's "Split left
and right" and "Split top and bottom" fill the new half with the same kind of
View (`AreaLayout.operations`), and each half keeps its own time base and axis
top. So after one split of the Concentrations Area, a screen reader hears two
"Time base, Concentrations" selectors, two "Axis top, Concentrations"
selectors and two pairs of arrow buttons, and cannot tell which plot the next
key press moves. A split Wash-in, Agent cost or Bookmarks Area repeats its
names in the same way. `PL-YSFX`'s test that no two controls share a name
cannot see it, because it builds each kind of View once.

**Why it matters.** The W3C's ARIA Authoring Practices Guide asks for "unique
names for elements with the same role unless the elements are actually
identical" (in its section "Composing Effective and User-friendly Accessible Names",
https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/, read
2026-11-28). With every kind of View on screen, 32 corners and 7 borders that
the keyboard reaches are each told to a screen reader by the same name. Each
corner's description says what the Area menu does, but not which Area it is
for. I suggest P3, because the Area menu a corner opens names its Area.

**Approach.** Give each Area one name for a screen reader: its View's title,
and, where two Areas show the same kind of View, which of them it is. Name
each corner with its Area's name and its place, each border with the two
Areas it divides, and each plot control with its Area's name instead of its
View's title, all through `dashboard_frame.control_name`, so the names still
start with the label shown. The names change when a View is swapped and when
an Area is split, joined or closed. How to tell two Areas of one kind apart in
words is this item's design work: research how screen-reader guidance and
simulation programs name repeated panes before choosing.

**Decided 2026-11-28: the names, from three sources.** This is a choice of
wording, so it is taken from the sources rather than put to the owner.

1. The W3C's ARIA Authoring Practices Guide, "Window Splitter" pattern
   (https://www.w3.org/WAI/ARIA/apg/patterns/windowsplitter, read
   2026-11-28): "The splitter also has an accessible name that matches the
   name of the primary pane." The primary pane is the one whose size the
   splitter's value represents.
2. The same guide's "Providing Accessible Names and Descriptions", section
   "Composing Effective and User-friendly Accessible Names"
   (https://www.w3.org/WAI/ARIA/apg/practices/names-and-descriptions/, read
   2026-11-28): "Create unique names for elements with the same role unless
   the elements are actually identical", "Put the most distinguishing and
   important words first", and "Be concise".
3. VS Code, the nearest desktop program found that splits one window into
   panes of one kind and names each pane for a screen reader. Its source on
   its main branch, read 2026-11-28, names an editor group "Editor Group {0}"
   with the group's index plus one
   (`src/vs/workbench/browser/parts/editor/editorGroupView.ts`, `ariaLabel`).
   `editorPart.ts` numbers the groups in the order they appear in the grid,
   a depth-first walk of the split tree (`GroupsOrder.GRID_APPEARANCE`), and
   numbers them again whenever a group is added, removed or moved, or a
   saved layout is applied (`notifyGroupIndexChange`).

Gas Man draws one window with no split panes, so it has no precedent here.
Blender's manual page on Areas
(https://docs.blender.org/manual/en/latest/interface/window_system/areas.html,
read 2026-11-28) says how a corner or a border is dragged, and nothing about
what a screen reader is told.

So the names are these:

1. **An Area's name** is its View's title as the View chooser shows it. Where
   two or more Areas in the window show the same kind of View, each adds its
   number among them, counted in reading order through the split tree, as
   VS Code numbers its editor groups: "Concentrations 1" and "Concentrations
   2". The numbers are worked out again after every split, join, swap, close
   and change of View.
2. **Each plot control** adds its Area's name in place of its View's title,
   such as "Time base, Concentrations 2". Its name still starts with the
   label shown, which SC 2.5.3 asks for.
3. **Each border** adds the name of the pane before it, to its left or above
   it, which is the primary pane in the guide's sense: "Area border,
   Concentrations". A pane that holds several Areas is named by its Areas in
   reading order: "Area border, Parameters and Bookmarks". The words "Area
   border" stay first, because Qt reports a border with the role Grip, and
   that role does not say that the border resizes Areas. This names one
   pane where the approach above named both Areas, because the guide names a
   splitter by its primary pane alone.
4. **Each corner** adds its Area's name and its place: "Area corner,
   Concentrations 2, top left". The four corners of one Area are not
   identical, because a drag from each joins toward different neighbours.

**How it is built.** `AreaLayout._build` rebuilds every frame and splitter on
each change, and keeps each View that stays. So `_build` works out every
Area's name from the model's tree, names each frame's corners and each
splitter's handles, and then gives each View its Area's name through a new
member of the View contract (`view_contract.View.name_controls`). A View
with no plot controls does nothing with it. All names are written through
`dashboard_frame.control_name`.

**Done when.** The two entries of `SHARED_PURPOSES` in
`tests/integration/test_keyboard_focus.py` are gone, and the test that reads
it still passes, with every kind of View on screen and again after the Area
menu splits an Area of each kind that draws against an axis.

**Generator check.** An instance of the open head `PL-9XGQ` (the
screen-reader walk checks only that each control has a name), whose misread
fact is what a screen reader is told about each element: its role, and a name
unique in its window. The walk that head widens is the test this item
extends, and its brief already names this item among the cases it waits on.

**Built 2026-11-28.** `area_layout._area_names` works out each Area's name
from the tree on every `_build`, as a `view_contract.AreaName`, which refuses
an empty title and a number less than 1. `AreaFrame.name_area` names the
Area's View chooser, its scroll box and its four corners, and `_widget_for`
names each splitter handle after the Areas before it. A pane of three or more
Areas is listed with a comma before the "and", as the Google developer
documentation style guide asks in "Serial commas"
(https://developers.google.com/style/commas, read 2026-11-28). The View
contract's new member is `name_controls(area)` rather than `name_area`,
because a View names its own controls with the Area's name and not the Area.

Walking every control a screen reader reaches after a split of each plot Area
found four more names that repeat, beyond those the brief listed. They are
the View chooser and the scroll box of each half, the concentration chart's
legend box and its six check boxes, and the wash-in legend's scroll box. All
are now named with the Area. The legend's boxes add the Area's name only while
two Areas show the chart, through `AreaName.among_copies`, because no other
kind of View shows a legend.

`PL-R1M6` merged during this work and gave each plot and each run's
schematic a name for a screen reader. Two halves of a split plot then gave
two pictures one name, because each name says only what its picture shows.
So `DescribedGraphic.name_among_copies` adds the Area's name to a picture's
name while another Area shows the same kind of View, and the split test
checks that each of the six pictures ends with its own Area's name.

The brief said a split Agent cost or Bookmarks Area repeats its names too.
Splitting every kind found that the copies of the Parameters, Agent
accounting, Branch and Bookmarks Views, and the Agent cost View's unit
selector and its offer to discard refused entries, act on state that all
copies share. So each pair is identical in the Authoring Practices Guide's
sense, as its example of two links to the same place is, and each keeps one
name. The Agent cost View's price form is the exception, because each copy
keeps the agent picked and the price typed in it. Its fields and buttons now
add the Area's name while two Areas show the View (`PriceEntry.name_for`).

Both blind reviews found three things. A border named only by the pane
before it, such as "Area border, Concentrations and Wash-in", reads as the
border between those Areas. So each border now says where it lies against
that pane: "Area border, below Concentrations and Wash-in", and "Area border,
right of Parameters". The Area menu's "Join with" and "Swap with" entries
named each Area by its bare title, so two neighbours of one kind gave two
entries with one label. They now use the Area's name. Both reviews also said
that the legend's boxes and the axis top act on state every chart shares, so
naming them with one half suggests a setting of that half alone. They keep
the Area's name, because the name tells a screen-reader user which plot a
control sits beside, as its place tells a sighted user, and a sighted user
who changes either in one half sees both halves change too.
`docs/INTERFACE.md` now says so, where it had said that every control acting
on shared state keeps one name.

Against the code before the change (a worktree at `48942cbc` with only
`tests/integration/test_keyboard_focus.py` copied in, and that worktree's
`src/` first on `PYTHONPATH`), 6 of the selected tests fail. The shared-name
test fails with "Left contains 2 more items, first extra item: ('Client',
'Area corner')" for each View once, and with 24 more items, the first ('Button',
'Show a later part of the run, Concentrations'), after the split. The split
test fails with "'Time base, Concentrations' != 'Time base, Concentrations
1'", and the price form test with "'Agent, price' != 'Agent, price, Agent
cost 1'". The four tests in `tests/integration/test_layout_adapter.py` need
`AreaName`, which the change adds, so the keyboard tests are their variant.

**How it was found.** Building `PL-YSFX`, 2026-11-28: its test that no two
reachable controls share a name found the corners and borders beside the run
and plot controls it fixed. Both independent reviews of `PL-YSFX`'s change
found the split case, 2026-11-28.

