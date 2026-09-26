---
id: PL-904Y
title: Split the whole-interface visibility predicate out of PL-W54S: interface_strings answers is-this-string-in-this-widget-subtree, which stops meaning can-the-reader-see-it once a layout can close an area or move it to another window
status: blocked
feature: interface-areas
added: 2026-09-16
priority: P2
effort: M
blocked-by: PL-W9P6
classes: safety, anticipated, defect
touches: src/anesthesia_sim/app/simulation_view.py, tests/integration
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
