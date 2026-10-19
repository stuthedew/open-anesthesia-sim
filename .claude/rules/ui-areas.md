---
paths:
  - "/src/anesthesia_sim/app/**"
  - "/src/anesthesia_sim/layout/**"
  - "/src/anesthesia_sim/data/workspaces/**"
---

# Every main UI element is a View that any Area can hold

`ROADMAP.md` § "v0.6.0 - the layout is the reader's" builds this interface on
Blender's window system. The window is divided into non-overlapping, resizable
**Areas**. Each Area holds one **View**, and the arrangements are kept as
**Workspaces** that a reader switches between. The project owner ruled that
**any main UI element is built as a View that an Area can hold** (project
owner, 2026-09-16).

The system is built in two halves. `src/anesthesia_sim/layout/` holds the
layout as a plain value, with no toolkit: the tree of Areas, the operations on
it, the Workspaces and the file they are saved to. `app/area_layout.py` is the
one adapter that builds the widgets from that value. `app/view_contract.py`
states what every View implements, and `app/view_registry.py` lists the kinds
an Area can hold. The roadmap section names what v0.6.0 builds. Its list
"Explicitly out of scope for v0.6.0" names what it does not build, such as
break-out into a second window and floating Areas. Read that list before
building an operation the section does not name.

## Interchangeable, not merely movable

An Area holds *one View and nothing else*, and any View can occupy any Area.
That is what makes a layout the reader's to arrange rather than a fixed set of
slots. So a View is not merely a widget that can be picked up and put down. It
is **interchangeable with every other View**, because it presents the same
contract they all do (project owner, 2026-09-16: "modular system where each
widget ... has core common features that make them interchangeable in any
blender-style area section").

That contract is `app/view_contract.py`'s `View` protocol (`PL-TH35`). Its
module docstring states what a View is given, what it saves and what it owes
when there is nothing to draw. `docs/ARCHITECTURE.md` § "Where new code
belongs" has the route for a new View. Do not widen the contract in passing.
A member that `app/area_layout.py` never calls is deleted, and
`tests/integration/test_view_contract.py` fails on such a member.

So, for a change to a View: **do not give one View a capability in a shape
that only that View could have.** A heading, a caption, a per-View control, a
way of saying "there is nothing to show yet": ask whether the next View needs
the same thing. Then give it a name and a shape the next View could take, even
while only one View uses it.

## What a View owes the Area that holds it

The test is one question: **if a reader split, resized, closed, swapped or
replaced the Area holding this View, what would break?** Five answers recur.

1. **A View is given what it draws, and never reaches for it.** It is built
   from a `ViewContext` and drawn from each `ViewTick`.
   `ConcentrationChart.draw(frame)` is the pattern: it takes one value and
   holds no controller, no parent and no global. A View that walks up to its
   parent, or reads a module-level singleton, is bound to one layout by that
   call.
2. **State that the rest of the dashboard draws from does not live inside the
   View.** Ask who owns a value when two Areas show the same View, or when the
   View is closed and reopened. `TraceLegend` is the worked instance. It shows
   the `CompartmentSelection` that the dashboard owns, and asks for a change
   through `ViewContext.requests` rather than holding the value (`PL-VN6M`).
   A View's own drawing settings are its own, and it saves them through
   `save_state` so that they survive a split, a swap and a Workspace switch.
3. **A View can be built more than once and assumes it is not alone.**
   Anything keyed on "the" chart, "the" legend or a class-level mutable value
   breaks this.
4. **A View does not assume its size.** An Area border is a drag away from any
   width. A View declares the minimum it needs on its registry entry, and the
   container holds the Area at that size or says why it cannot (`PL-K285`).
   Fixed geometry is for a swatch whose size is the point (`_LineSwatch`),
   never for a layout.
5. **A required value never moves into something closeable.** `docs/MODEL.md`
   § "Minimum displayed outputs" divides the display into an unconditional set,
   which no Workspace may remove, and a conditional remainder. The
   unconditional set sits in its own region outside the Areas (`PL-NWTM`). A
   value on that list does not go in a View.

## Where the vocabulary is fixed

Area and Workspace are Blender's words, and this project adopted them rather
than inventing its own. The roadmap section above carries the definitions and
the operations. `docs/interface-provenance.md` records where they came from:
what was read of Blender, what this project adopts, and where it deliberately
does something else. Read it before assuming that a Blender behaviour carries
over here. Most of the differences exist because Blender's answer would be
unsafe with clinical values on screen.

**The third word is `View`, not Blender's `Editor`** (project owner,
2026-09-17, ratified - chosen over keeping `Editor`, and over `Component` and
`Widget`). A View is what occupies an Area: a graph, a table of values, a
control panel. Blender's editors mostly *edit* something. This project's Views
mostly display modelled values, and calling a read-only trace an "Editor"
implies that the reader can change it. `Widget` was unavailable, because
`QWidget` is the base class of every View. `Component` was rejected as vaguer
rather than wrong. `PL-GPYV` carries the full comparison, including Eclipse's
Perspective/View/Editor split, which matches this project on lifecycle and not
on multiplicity.

**Blender's own editors keep their name.** `docs/interface-provenance.md`
describes Blender, where `Editor` is the correct term, so nothing there is
renamed. Use Area, View and Workspace for this project's three things and no
other words, in the code, the documents and the interface alike.
