---
id: PL-BLHV
title: Record the intended-use statement and the IEC 62304 safety classification in docs/MODEL.md
status: needs-decision
priority: P2
effort: M
classes: docs, planning
touches: docs/MODEL.md
added: 2026-09-02
---

**Problem.** `docs/MODEL.md` says what this application is *not* - "not a
clinical prediction, dosing tool, patient monitor, or medical device" - and
never says what it *is*, in the form both ISO 14971 and IEC 62304 start
from. No software safety classification is recorded either.

**Why it matters.** The project owner has stated the expectation that the
tool will be used against direction to inform real decisions, and
`ROADMAP.md` item 30 makes patient covariates a core teaching component. Two
consequences follow. IEC 62304's own convention is that an *undocumented*
classification defaults to Class C, so writing one down is strictly better
than leaving it implicit whatever letter it lands on. And the compartments
this project exists to display - vessel-rich, muscle, fat, mixed venous -
are the ones no monitor shows, so the "a real monitor is always available"
argument that would lower the class does not cover them.

Device status is not the question: FDA's published examples of software
functions that are *not* devices include software intended for health care
professionals as educational tools for medical training, and that exclusion
turns on intended use rather than on which physiologic parameters the
software accepts.

**Where.** `docs/MODEL.md`, a new section near "Status".

**Decision needed.** Whether to record it, and in what terms. The audit
recommended: a positive intended-use statement naming teaching and excluding
use with or in the presence of an actual patient; Class C practices for
`core/` and the readout path with Class A for the app chrome, using
IEC 62304 section 4.3 and 5.3.5 segmentation; and the whole thing framed as
a self-imposed engineering bar rather than a regulatory status - the same
move `docs/MODEL.md` already makes for WCAG 2.2 AA, "chosen as the right
engineering bar for a teaching tool, not as a compliance obligation".

Claiming a class as a regulatory status would imply a quality system this
project does not have, so the framing is the part that needs the owner's
judgment rather than the letter.

**Done when.** The decision is recorded, and if the section is written,
`make doc-check` passes and the reply says which documents were swept.
