---
id: PL-904Y
title: Split the whole-interface visibility predicate out of PL-W54S: interface_strings answers is-this-string-in-this-widget-subtree, which stops meaning can-the-reader-see-it once a layout can close an area or move it to another window
priority: P1
effort: M
status: done
classes: safety, anticipated, defect
feature: interface-areas
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration
added: 2026-09-16
closed: 2026-10-19
pr: 1617
payoff: the whole-interface safety tests keep meaning that the reader can see a value once an Area can be closed, hidden behind a tab or moved
verify: grep -q 'def test_a_value_hidden_from_the_reader_is_not_counted_as_shown' tests/integration/test_simulation_view.py
---

**Problem.** Split the whole-interface visibility predicate out of PL-W54S: interface_strings answers is-this-string-in-this-widget-subtree, which stops meaning can-the-reader-see-it once a layout can close an area or move it to another window

**Why it matters.** `SimulationView.interface_strings`
(`src/anesthesia_sim/app/simulation_view.py:552`) is this project's single
definition of what is on screen - its own docstring says so - and the
safety-facing whole-interface tests assert through it: that nothing says
"end-tidal" without "-equivalent", that the MAC divisor and the MAC-awake band
fraction are stated for every agent, that the use disclaimer is present. It
answers "is this string somewhere in this widget's subtree", which is the same
question as "can the reader see it" only while the dashboard is one tree with
nothing closeable.

This milestone makes the two come apart in both directions, and neither shows
up as a failure: a value in an Area the reader closed, or in a Workspace that is
not the active tab, is still in the tree and still counted; a value in an Area
that moved elsewhere drops out of the walk, so an assertion of presence starts
failing for a correct layout, or - worse, for the ones asserting *absence* -
starts passing because the string went somewhere the walk cannot reach.
`CLAUDE.md`'s compounding-friction test names the first shape exactly: a check
that gives a wrong answer silently.

**Split from `PL-W54S`** on 2026-09-16: that item is the window-obligation
decision and this is the predicate, which breaks at Area close and join rather
than at break-out and is therefore v0.6.0's rather than break-out's.

**Done when.** One predicate spans every Area and every top-level window the
application owns, distinguishes present-in-the-tree from visible-to-the-reader,
and is what the whole-interface tests assert through; `interface_strings` either
becomes it or is narrowed to the one-widget question with its callers moved.

*Scope.* `ROADMAP.md` § "v0.6.0 - the layout is the reader's" -> "Required
scope" item 17.

## Built 2026-10-19

**Checked 2026-10-19:** the brief still held, and the tree had already moved
into its first shape. Choosing another View for the chart's Area (`PL-50PZ`)
takes the chart panel out of the window. The old walk then still counted both
plots' axis titles as on screen, and it lost every label in the panel. A
variant of the new regression test fails on `origin/main` (`7b9efe01`) with
`AssertionError: assert 'Clinical references:' in {...}`.

**The predicate.** `SimulationView.interface_text` returns every string the
dashboard holds as an `InterfaceText`, with `visible` set by
`_seen_by_reader`. A widget is seen when it and every ancestor are shown, its
window is shown and not minimized, and it has an area to draw in. Of a
combo's entries, only the current one is visible. The walk covers the window
and every View the dashboard has built, including one that no Area draws now.
`interface_strings` is every held string, and `visible_strings` is the visible
ones. Both read `interface_text`, so there is one predicate.

**Which test asks which question.** A test that something is never said
asserts over `interface_strings`, because a hidden string can be shown at any
moment. A test that the reader is told something asserts over
`visible_strings`. The presence tests moved to `visible_strings`: the MAC
divisor and band for every agent, the playback rate, the band's trace, the
wash-in denominator, the control-mark wording and the use disclaimer. The
absence tests (the end-tidal hedge, no wake-up time, no application name) and
the walk-reach tests stay on `interface_strings`.

**Decided here, each the one correct option.** A widget scrolled out of view
counts as seen, because the reader reaches it by scrolling without opening or
choosing anything. Counting it as unseen would fail the presence tests for a
correct layout on a short window. A combo's other entries are not seen,
because they are not on screen until the reader opens it.

**Left to later items.** A break-out window (`ROADMAP.md` planned-milestone
item 34) has to be added to the walk when it is built, and the docstring says
so. `PL-G5SX` (tests over the real interface) asserts through this predicate.
