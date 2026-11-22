---
id: PL-GC7Z
title: The #: comment above REFERENCE_CONDITION_LABEL in src/anesthesia_sim/app/display_units.py cites docs/MODEL.md's note 'One reference condition, where the model physically has two' without the section mark, the fourth citation of that note and the one PL-97S1 did not reach
priority: P3
effort: S
status: ready
classes: defect, docs
feature: copy-editor
touches: src/anesthesia_sim/app/display_units.py
deferred-from: v0.7.0 - a new problem: the comment was written on 2026-11-13 by #2136 (44449552), which built Required-scope work (PL-RJN9, PL-HQPF), after the freeze
added: 2026-11-16
payoff: Every citation of the reference-condition note uses one form, so a reader or a search reaches the note from each of them and a rename cannot strand one.
---

**Problem.** The #: comment above REFERENCE_CONDITION_LABEL in src/anesthesia_sim/app/display_units.py cites docs/MODEL.md's note 'One reference condition, where the model physically has two' without the section mark, the fourth citation of that note and the one PL-97S1 did not reach

**Checked 2026-11-22**, at `d4e8200c`. `grep -n -A1 'Known limitations", "One reference condition' src/anesthesia_sim/app/display_units.py`
printed lines 67 and 68: `` (`docs/MODEL.md` § "Known limitations", "One
reference condition, where the model physically has two") ``. The comment is
the one above `BODY_STORES_CONDITION_LINES`, just below
`REFERENCE_CONDITION_LABEL`. `PL-97S1` (two citations of this note without the
section mark) settled the form as `docs/MODEL.md` § "One reference condition,
where the model physically has two", under § "Known limitations", and this
comment still has the old form. The comment was written on 2026-11-13 by
#2136 (`44449552`), after the Gate 3 freeze.

**Why it matters.** The note's name is the anchor a reader follows from the
code to the size of the error in the body's stored amounts. All four citations
of the note should use one form, so that a search for the note finds each of
them and a later rename of the note can be checked against all four.

**Done when.** The comment in `src/anesthesia_sim/app/display_units.py` cites
the note in the same form as the other three citations, and no citation of the
note in the tree keeps the old form.

**Generator check.** The fact is which section a citation of a `docs/MODEL.md`
note names. `PL-97S1` fixed three citations and left this one deliberately,
because no check reads a `#:` comment, and this item was filed in the commit
that closed `PL-97S1`. So it is that item's stated remainder, not a fix that
failed to hold. See also `PL-Q2DK` (a citation of a renamed `ROADMAP.md`
heading): both are citations that the document check cannot test against the
cited document's headings. No head's `misread:` states that fact.
