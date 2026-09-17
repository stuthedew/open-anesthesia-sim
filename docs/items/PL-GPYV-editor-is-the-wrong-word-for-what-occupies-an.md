---
id: PL-GPYV
title: Editor is the wrong word for what occupies an Area in this project: Blender's editors predominantly edit, ours predominantly display modelled values, and nothing has been built with the name yet
status: untriaged
feature: interface-areas
added: 2026-09-17
---

**Problem.** Editor is the wrong word for what occupies an Area in this project: Blender's editors predominantly edit, ours predominantly display modelled values, and nothing has been built with the name yet

**Raised by the project owner, 2026-09-17.** "I agree with adopting blender
terminology for area and workspace, but thinking editor might not be the best
term. I've been using 'widget' which again, I'm not sure is best either but
closer... Is there a better term that better encompasses that the editor/widget
item is just what you actually want displayed in the area (like a graph, or a
table of values (like exhausted gas, compartment mac values), inputs etc.?)"

**Why it matters.** `ROADMAP.md` § "v0.6.0 - the layout is the reader's" fixes
the vocabulary as Blender's "used exactly", and supersedes `PL-C842`'s original
`Pane`/`view_kind` naming to do it. `.claude/rules/ui-areas.md` § "Where the
vocabulary is fixed" carries the same. So this is a recorded decision, and
changing it touches `ROADMAP.md`, that rule, `docs/interface-provenance.md` and
`PL-1FT6`'s brief, which names `set_editor`.

**It is free now and expensive later.** Nothing has been built under the name:
`PL-1FT6` is `ready` and unstarted, and `set_editor` exists in no code. After
v0.6.0 the name is in a serialized schema a reader's saved Workspaces carry.

**Recommendation: `View`.** Measured 2026-09-17 against the tree:

- **`Widget` collides, hard.** `QWidget` appears 61 times under
  `src/anesthesia_sim/app/`, and `app/qt_widgets.py` is a module. The word
  already means "Qt widget" here, and every Area's occupant *is* one, so the
  domain term and the toolkit term would be the same word for two different
  things - across an import boundary `tools/import_boundary_check.py` exists to
  police.
- **`View` does not collide and is already the project's word.** No Qt `*View`
  class is used anywhere in `app/`; the only `View` names are this project's own
  `RunView` and `SimulationView`. `.claude/rules/ui-areas.md` rule 1 is already
  written in it - "A view is given what it draws; it never reaches for it" - and
  `PL-C842` chose `view_kind` before the roadmap renamed it.
- **`Editor` carries a false implication here.** Blender's editors mostly mutate
  something - the 3D viewport, the dope sheet, the text editor. This project's
  occupants mostly display modelled values: the concentration graph, the
  compartment table, the MAC readout, the exhausted-gas table. Only the control
  panel takes input. Calling a read-only trace display an "Editor" suggests the
  reader can change what is shown, when what they can change is the model's
  inputs.
- **`Instrument` and `Monitor` are rejected on the safety standard**, though they
  read well in the domain. Both imply *measurement*, and `CLAUDE.md` requires
  modelled values to be clearly distinguished from measured ones. A term that
  quietly asserts the wrong one of those two is the kind of defect this project
  treats as a presentation failure.
- **`Panel` is rejected** because Blender already uses it for a collapsible
  section inside a region, so borrowing it inverts a term adopted wholesale.
  `Readout` and `Display` are rejected as display-only: neither covers inputs,
  and `Display` collides with `docs/MODEL.md` § "Minimum displayed outputs".

**The cost of the recommendation, stated.** It makes the borrow two-thirds -
Area and Workspace from Blender, View not - which is the drift the "used
exactly" rule exists to prevent. The mitigation is that it stops being drift
once it is recorded as a caused divergence: `docs/interface-provenance.md`
§ "Diverged, and each divergence has a specific cause" is the section for it,
and the cause is that Blender's editors edit and this project's views display.

**Decision needed.** Whether to keep `Editor`, take `View`, or take another word.
The vocabulary is the project owner's to set; this item carries the measurement
and a recommendation, not an answer.

## What common GUI-programming terminology offers (project owner asked, 2026-09-17)

**The generic terms are all granularity-neutral, which is why none of them
settles it.** `Widget` (Qt, GTK, Flutter), `Component` (React, Vue, Angular,
Swing's `JComponent`) and `View` (UIKit, Android, MVC) all name *any* UI element:
a button is a widget, a component and a view in the respective vocabularies.
None of them carries "occupies an Area and is the thing the reader chose to put
there", which is the meaning being named here.

**The frameworks that solve this exact problem use a different set.** A
rearrangeable region occupant inside a saved arrangement is a **dock widget**
(Qt's `QDockWidget`), a **tool window** (Visual Studio, JetBrains), or a
**view** (Eclipse). Those are the real analogues of what this project is
building, and Eclipse's is the closest: its **Perspective** is Blender's
Workspace almost exactly - "a workbench page can have one or more perspectives
that define the layout of the views and editors in the page".

**Eclipse splits `View` from `Editor` on the axis this item is about, and the
split half-fits.** From the Eclipse Platform documentation:

- an editor "is typically used to edit or browse a document or input object,
  with modifications following an open-save-close lifecycle model";
- a view "is typically used to navigate a hierarchy of information, open an
  editor, or display properties for the active editor, with modifications saved
  immediately in contrast to an editor".

On **lifecycle** this project's occupants are squarely Views: there is no
document, no open-save-close, and nothing they show is edited. On
**multiplicity** they are squarely Editors - "the same editor type may be open
many times within one workbench page for different inputs, unlike views", and
Eclipse makes views single-instance unless a plug-in opts out. The project
owner's decisive case is three graphs in one Workspace, which is the behaviour
Eclipse reserves for editors.

**That split is worth recording rather than resolving by picking a side**, and it
is the strongest argument against borrowing any framework's term wholesale.
Eclipse ties multiplicity to editors because an editor is bound to an *input* -
three editors means three files. Here three graphs are bound to **one run** and
differ in *presentation*, not in input. So the case is neither of Eclipse's, and
a borrowed word would import a wrong implication either way.

**`Component`, considered on its merits** (project owner's suggestion). It beats
`Widget` here on the one decisive ground: no collision. `QComponent` does not
exist, where `QWidget` appears 61 times under `app/`. Against it: it is the
vaguest of the three generic terms about granularity, and it carries strong
web-framework connotation - props, state, a re-render model - which is a
different architecture from a Qt application and would set a reader's
expectations wrongly. It fixes the "editors do not edit" defect without
supplying the "this is an Area's content" meaning.

**The recommendation is unchanged: `View`.** It is the only candidate that is
already this project's own word, collides with nothing in the toolkit, matches
Eclipse on the axis that actually describes these objects (lifecycle), and needs
one recorded caveat rather than a rename. Second choice is `Component`, and the
cost of taking it is vagueness rather than error.
