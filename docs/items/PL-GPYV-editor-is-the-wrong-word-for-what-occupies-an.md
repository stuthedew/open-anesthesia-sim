---
id: PL-GPYV
title: Editor is the wrong word for what occupies an Area in this project: Blender's editors predominantly edit, ours predominantly display modelled values, and nothing has been built with the name yet
priority: P2
effort: S
status: done
classes: planning
feature: interface-areas
milestone: v0.4.28
touches: docs/items, ROADMAP.md, docs/WORKING_NOTES.md, src/anesthesia_sim/app
added: 2026-09-17
closed: 2026-09-17
pr: 661
verify: python3 tools/doc_check.py check && ! grep -rlE 'set_editor|\bEditor\b' docs/items/ --exclude='PL-FTP5-*' --exclude='PL-C842-*' --exclude='PL-H620-*' --exclude='PL-GPYV-*' --exclude='PL-FXBS-*'
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

**The decision was the project owner's to make**, and it is recorded below. The
vocabulary is theirs to set; this item carried the measurement and a
recommendation.

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


## Decided 2026-09-17: `View`

**The project owner agreed with the recommendation** (ratified - chosen over
keeping `Editor`, and over `Component` and `Widget`). This **reverses** the
2026-09-16 decision recorded in `ROADMAP.md` planned item 36, which took
Blender's `Editor` as the project's term and explicitly retired *views* and
*widgets*. The reversal is deliberate and the earlier sentence has been
rewritten rather than deleted, so the record shows both.

Recorded in three places, which is what makes it effective:
`.claude/rules/ui-areas.md` § "Where the vocabulary is fixed", `ROADMAP.md`
§ "v0.6.0 - the layout is the reader's" and planned item 36, and
`docs/interface-provenance.md` § "Diverged, and each divergence has a specific
cause". `ROADMAP.md` and that rule are swept; `PL-1FT6`'s `set_editor` is now
`set_view`.

**The sweep, and its one judgment.** 33 item files under `docs/items/` said
Editor in this project's sense. They were a mechanical sweep with one judgment
in it, which is why this was an item rather than a `sed`: **anything quoting or
describing Blender keeps Blender's word**, as does every citation of a
`docs/interface-provenance.md` section title - that document describes Blender
and is deliberately not renamed. `PL-C842` needed no change to its vocabulary:
it wrote `view_kind` and `set_view` before the 2026-09-16 rename.

**That judgment is now recorded as a file list, not as prose** (project owner,
2026-09-17). Five item files legitimately keep Blender's word and are excluded
from this item's `verify:` command: `PL-FTP5` (the Blender study record),
`PL-C842` (the Blender read behind the container decision), `PL-H620` (the item
that adopted Blender's vocabulary, quoting the manual's own definitions table),
`PL-GPYV` (this item, whose brief must name `set_editor` to record the rename)
and `PL-FXBS` (the verify-command finding, whose title must name it too).
Everything else was swept.

**The old `verify:` could never pass, and `PL-FXBS` has the measurement.**
`! grep -rl 'set_editor' docs/items/` asks the store to prove a string absent
from itself, and the `verify:` line stating it lives in `docs/items/` - so it
was falsified by five lines of this item's own file, four of them the record of
the rename this item is required to keep. Replaced with a pattern matching
`set_editor` and the capitalized noun `Editor`, excluding the five files above.
Checked against `origin/main`: it fails there, naming the 17 files this sweep
changed, and passes here.

**Three corrections the sweep found, all from the 2026-09-16 rename having been
run as a blind `sed`:**

- `ROADMAP.md` carried six occurrences of "an **View**" - the article left
  behind when `Editor` became `View`. Fixed.
- `ROADMAP.md` still carried `set_editor` twice, in Required scope entry 1 and
  in the deferred-docking list, though this item's own brief recorded the
  roadmap as swept.
- `docs/WORKING_NOTES.md` and one comment in
  `src/anesthesia_sim/app/run_view.py` still named this project's object
  `editor`; the comment cited `.claude/rules/ui-areas.md`, which had already
  been renamed, and used *view* twice and *editor* once for the same thing.

Four quotations of project text that had itself been renamed were updated so
they match their sources again: `PL-L6QR` and `PL-BNYF` quote `ROADMAP.md`
item 34, `PL-9LNF` quotes `.claude/rules/ui-areas.md` test 2, and `PL-YHWG`
quotes item 34's scope line.

**Done when.** No item file under `docs/items/` uses `Editor` for this
project's own objects outside the five excluded above, `set_editor` appears
nowhere but in the two items recording the rename, and every remaining
`Editor` in the tree either describes Blender or cites a
`docs/interface-provenance.md` section title by name. `ROADMAP.md`,
`.claude/rules/ui-areas.md`, `docs/interface-provenance.md`, `PL-1FT6` and
`PL-MQHN` were already done.

**Shipped release notes are not swept**, and that is deliberate rather than an
omission. `docs/releases/v0.4.26.md` names the `Editor` contract in two entries
because that was the contract's name on the day it shipped;
`subprojects/docket/src/docket/release.py` calls the notes "the half that is
permanent", and `checks._check_release_notes` matches ids rather than titles,
so nothing depends on rewriting them. Rewriting a shipped release's prose to
match a vocabulary decided afterwards would falsify the record - most sharply
for `PL-H620`, whose entry records the owner *choosing* Blender's word.
