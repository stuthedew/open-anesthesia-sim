---
id: PL-B875
title: docs/MODEL.md still says the operator split is kept and that no planned work wants an exact step, which the 2026-09-03 re-scope reversed
priority: P2
effort: S
status: done
classes: defect, docs
feature: model-spec-accuracy
touches: docs/MODEL.md
added: 2026-09-03
closed: 2026-09-03
pr: 268
verify: python3 tools/doc_check.py check && grep -qF 'This decision was superseded on 2026-09-03' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "Selected method (as implemented)" carries, at
lines 603-616, the 2026-08-30 decision and the reasoning that has since been
reversed:

> **The split is kept nonetheless** (project owner, 2026-08-30). [...] What an
> exact step would buy is therefore the removal of the applicability-domain
> bound under "Supported simulation step" below, not the correction of a wrong
> value — and **no planned work wants that**. [...] Revisit only if some future
> requirement genuinely wants a larger step.

`ROADMAP.md`'s v0.4.1 row and planned-milestone item 29 reversed exactly this
on 2026-09-03: the split *is* replaced, by `PL-GS5X`, and the requirement that
wants it is readability rather than step size. So the specification's own
statement of the plan contradicts the roadmap's, and the specification is the
document a reader of the model reaches first.

**Why it matters.** `PL-GS5X` will rewrite the section, and its brief already
requires that the rewrite "record that the decision changed and on what new
ground, rather than quietly reversing". But `PL-GS5X` is a whole release away —
v0.4.0 has thirteen open items ahead of it — and for that entire span
`docs/MODEL.md` tells a reader that an exact step is not planned. That is the
stale-documentation failure `CLAUDE.md` classes as a safety issue rather than
tidiness: the sentence is about the numerical method, which is the part of the
model a reader is most likely to take on trust.

`tools/doc_check.py` cannot catch it. The citation is not dangling, no prose
value has drifted from a data file, and the release-train check reads the
version table rather than this paragraph. Only a reader comparing two documents
sees it, which is what makes it worth an item.

**Where.** `docs/MODEL.md` § "Selected method (as implemented)", the paragraph
beginning "**The split is kept nonetheless**" (lines 603-616 at capture).
`ROADMAP.md` planned-milestone item 29 and the v0.4.1 timeline row carry the
superseding decision; `PL-6GS0` is the item the paragraph's measurements sit in.

**Scope.** An interim amendment, not the rewrite. Three or four sentences saying
the decision was superseded on 2026-09-03, naming `PL-GS5X` and the ground it
was superseded on (a reviewer should be able to follow `core/` without a lookup
table, which the split's five sub-steps prevent), and leaving the measurements
and the applicability-domain reasoning intact — they are still true of the
shipped method. `PL-GS5X` still owns the full rewrite.

**Done when.** § "Selected method (as implemented)" no longer asserts that the
split is kept or that no planned work wants an exact step; the superseding
decision is named with its date and its item; and `make check` passes.

**Found.** Session auditing which open items the v0.4.1 `core/` pass would
invalidate, 2026-09-03.

**Closed 2026-09-03** (project owner asked for the interim fix rather than
waiting for `PL-GS5X`). § "Selected method (as implemented)" now carries the
supersession where the superseded decision sits, in four edits and no more:

- the subsection heading reads "The exact alternative, and why it replaces this
  one" rather than "why it is not taken";
- the 2026-08-30 decision is kept, with its reasoning, and marked as holding on
  its own terms - the error bounds are why the split is sound to ship until it
  is replaced, which is a live statement rather than a historical one;
- a new paragraph records the 2026-09-03 supersession and the ground, which the
  original decision did not weigh: readability, not accuracy. It names item 29's
  bar, the three specific ways the split fails it - three of five sub-steps are
  objects of the splitting scheme rather than of the physiology, the alveolar
  balance's two terms sit in different sub-steps separated by a third, and the
  pulmonary uptake rate specified under "Alveolar gas" is never formed - and
  points at `PL-GS5X` and `PL-X9KD`;
- one sentence states that until those land this section describes what ships
  and its bounds are the live ones, and marks itself as the interim correction.

The measurements, the applicability-domain reasoning and the determinism
argument for the fixed 0.1 s step are untouched, as scoped. `PL-GS5X` still owns
the rewrite.

**Verified** by the command in the front matter, run before the work and
watched fail: `doc_check` passed and the `grep` did not, exit 1. Exit 0 after.

**Found alongside, and left alone:** § "Status" still says the model is "still
in force in v0.2.3, the current released baseline", which is v0.3.2. That is
`PL-C1KK`, already open, and folding it in here would have widened a scoped
interim fix into a second one.
