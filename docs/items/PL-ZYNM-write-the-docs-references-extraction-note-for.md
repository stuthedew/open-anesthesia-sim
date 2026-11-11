---
id: PL-ZYNM
title: Write the docs/references extraction note for the Gas Man Workbook's bookmark controls and workflow, read 2026-09-20
priority: P3
effort: S
status: done
classes: docs
feature: provenance
touches: docs/references
added: 2026-09-20
closed: 2026-11-11
pr: 2107
payoff: stops the next session cloning the corpus and re-reading a 199-page book to answer the same bookmark-workflow question
verify: grep -rqF 'Clicking Add will cause the playback to pause' docs/references/
---

**Problem.** Write the docs/references extraction note for the Gas Man Workbook's bookmark controls and workflow, read 2026-09-20

**Why it matters.** `docs/references/README.md` settles the obligation —
"Reading a source from the corpus therefore owes an extraction note in this
directory. Without one the corpus is consulted once per *session* instead of
once per *source*, and each later session re-reads the same PDF at full
context." The corpus was attached and the Workbook's bookmark material read on
2026-09-20 to answer a sequencing question from the project owner, and nothing
in this repository yet records what it says. The next session asking the same
question clones the corpus and re-reads a 199-page book.

`PL-Z3V5` decides what a note *contains* and owns the first worked example;
this item is the note for one source, written in whatever shape `PL-Z3V5`
settles. The facts below are recorded here so that they survive even if this
item waits.

**What was read.** Philip JH. *Workbook for Gas Man®: a simulation and teaching
tool*. Med Man Simulations, Inc.; title page 2012-05-16. Three places, via
`text/gasman_workbook/` rather than the PDFs:

- Chapter 2, "Using Bookmarks", printed pp. 22-23.
- Chapter 2, Edit menu and toolbar, printed pp. 15 and 18.
- Appendix E, "Bookmarks", printed p. 183.

**What it establishes about bookmark controls and workflow.** Tier 3 — a
program's own manual, describing what the reference implementation does, not a
measurement.

- **A bookmark is a pause time.** It "cause[s] a simulation to pause when the
  elapsed time equals the bookmark time" (p. 22). Entered as hour, minute and
  second of elapsed *simulated* time (p. 23).
- **One dialog, three operations: Add, Delete, Delete All** (p. 23). Reached
  from the Special menu and from a toolbar button (pp. 18, 22).
- **Set mid-run, the default instant is "that moment in the simulation minus
  one second"**, and the manual gives the reason: "Clicking Add will cause the
  playback to pause before any changes you make, allowing you to try different
  options on playback" (p. 23). That is the reference implementation's *fork
  staging gesture*, and it is the same choice `PL-B8MK` reached independently
  by a different argument - open the branch's definition at the keyframe
  *before* the bookmark.
- **Any instant may be bookmarked, earlier or later than the paused moment**
  (p. 23).
- **Bookmarks persist with the saved experiment** (p. 22; p. 183), which this
  project defers with planned item 9.
- **The transport is bookmark-aware.** Fast Fwd "Takes you immediately forward
  to the next Bookmark or the end of the simulation, keeping all the settings
  as they were" (Edit menu, p. 15).
- **Appendix E states the purpose in comparability terms**: bookmarks are "most
  helpful where issues of comparability arise - for example, to compare
  outcomes given alternative settings at a particular point in the course of
  anesthesia, or to compare (perhaps overlay) tension traces over a single
  induction interval for different anesthetics" (p. 183).

**The one finding worth carrying into `PL-LPLD` rather than only into a
note.** Appendix E gives a bookmark *two* functions: "a particular point in
time in the evolution of a simulation where one wishes to pause, **or a point
to which to return (pause during replay)**" (p. 183). The second needs a
user-facing replay control, which is planned item 10 and named in `ROADMAP.md`
§ "Explicitly out of scope for v0.5.0". So this project's bookmarks are
run-until markers and not return-to markers, and a learner returns to one by
forking at it (`PL-B8MK`) rather than by replaying to it. `PL-LPLD`'s brief and
its `payoff:` - "run fast to the moment they care about and return to it by
name" - do not say which of the two they mean.

**Done when.** `docs/references/` carries a note for this source recording the
above with its locators, in `PL-Z3V5`'s shape, and `docs/references/README.md`
points at it from the Workbook's entry.

**Done 2026-11-11.** The reading is a new entry in the Workbook's section of
`docs/references/README.md` § "The documents", not a separate note file.
`PL-Z3V5` settled that shape on 2026-10-26: the Workbook is one of the sources
whose readings stay inside their entry, and "a later reading of the source is
added to it". So the entry is the note, and no pointer to another file is
needed. Every quotation and page above was checked against the corpus's text
extraction (`text/gasman_workbook/01_Front_Matter_Ch1-4.txt` and
`05_Appendices_Bibliography.txt`) on 2026-11-11, and all of them hold. The
entry's route-and-depth paragraph now names Chapter 2's pp. 15, 18 and 22-23.

The entry says how this repository relates to the reading as it stands now. Its
time bookmarks halt a run, and a learner returns to one by taking a branch
there (`PL-B8MK`, and `PL-W4XQ`, which closed after this item was written). The
replay half of Appendix E's second use is still `ROADMAP.md` planned item 10.
The brief's claim that `PL-B8MK` made "the same choice" as Gas Man's
one-second default was not carried into the entry. A branch taken at a
bookmark stands at the bookmark itself, while Gas Man's default pauses one
second before it, and the entry says that instead.

The close-out copy edit of the new entry is owed. The project owner paused the
copy editor on 2026-11-11 at 00:10Z ("Pausing copy editor stuff"), and the
coordinator directed that fact records land without it. Run it on this entry
once the pause is lifted.
