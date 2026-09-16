---
paths:
  - "/src/anesthesia_sim/app/**"
---

# Every main UI element becomes an area-type widget

`ROADMAP.md` planned-milestone item 34 takes Blender's window system as the
model for this interface: the window subdivided into non-overlapping resizable
**Areas**, each holding one **Editor**, grouped into **Workspaces** switched as
tabs. That item builds the system. This file is what the rest of `app/` owes it
in the meantime, because the owner has ruled that **any main UI element going
forward is built understanding it will ultimately be converted into an
area-type widget** (project owner, 2026-09-16).

That is a constraint on code written *now*, not a licence to build the area
system early. Item 34 is placed, its ordering is decided, and it validates
against two views that already exist. Do not build splitting, joining, docking,
workspace tabs or layout persistence ahead of it.

## Interchangeable, not merely movable

An area holds *one editor and nothing else*, and any editor can occupy any area
— that is what makes a layout the reader's to arrange rather than a fixed set of
slots. So the target is not a widget that can be picked up and put down: it is a
widget that is **interchangeable with every other main view**, because it
presents the same contract they all do (project owner, 2026-09-16: "modular
system where each widget ... has core common features that make them
interchangeable in any blender-style area section").

That contract is not designed yet and is not yours to invent mid-change —
`ROADMAP.md` item 34 builds the area system and item 36 catalogues the editors,
and the roadmap already records why the layout comes first: a view's contract is
whatever the area system requires of its contents, so a contract written against
today's fixed layout is rewritten. `PL-TH35` is where it gets defined.

What that means for a change landing before then: **do not add a capability to
one view in a shape only that view could have.** A heading, a caption, a
per-view control, a way of saying "there is nothing to show yet" — ask whether
the next view needs the same thing, and give it a name and a shape the next view
could take, even while only one view uses it. A feature that is interchangeable
in principle costs nothing extra now; one built into a single widget's internals
has to be found and lifted back out later.

## What it asks of a view you write today

The test is one question: **if this widget were lifted into an area a reader can
split, resize, close or replace, what would break?** Five answers recur, and
each is cheap now and expensive later.

1. **A view is given what it draws; it never reaches for it.** `ChartFrame` is
   the pattern — `ConcentrationChart.draw(frame)` takes one value and holds no
   controller, no parent and no global. A view that walks up to its parent, or
   reads a module-level singleton, is bound to one layout by that call.
2. **State a layout could duplicate or relocate does not live inside the
   widget.** Ask who owns it when two areas show the same editor, or when the
   editor is closed and reopened. `TraceLegend` owning compartment visibility
   is the standing counter-example (`PL-VN6M`); a view holds its own scroll
   position, not the selection the rest of the dashboard draws from.
3. **A view is instantiable more than once and assumes it is not alone.**
   `RunView` already is. Anything keyed on "the" chart, "the" legend or a
   class-level mutable is not.
4. **A view does not assume its size.** An area border is a drag away from any
   width. Fixed geometry is for a swatch whose size is the point
   (`_LineSwatch`), never for a layout.
5. **A required value never moves into something closeable.** `docs/MODEL.md`
   § "Minimum displayed outputs" divides the display into an unconditional set
   no workspace may remove and a conditional remainder; the unconditional set
   sits outside the area system. A value on that list does not go in an area.

## Where the vocabulary is fixed

Area, Editor and Workspace are Blender's words and this project adopted them
rather than inventing its own — `ROADMAP.md` item 34 carries the definitions,
the docking operations and the two precedents copied from the source, and
`docs/interface-provenance.md` carries where they came from: what was read of
Blender, what this project adopts, and the four places it deliberately does
something else. Read that before assuming a Blender behaviour carries here —
three of the four divergences exist because Blender's answer would be unsafe
with clinical values on screen. Use those
three words for those three things and no others, so the code and the roadmap
do not drift into separate vocabularies before the system is built.
