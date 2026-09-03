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

**Decision needed.** Whether to record it, and in what terms. Three parts,
of which only the first is still open:

1. A positive intended-use statement naming teaching and excluding use with
   or in the presence of an actual patient.
2. **Class C, uniformly, for the whole application.**
3. The whole thing framed as a self-imposed engineering bar rather than a
   regulatory status - the same move `docs/MODEL.md` already makes for
   WCAG 2.2 AA, "chosen as the right engineering bar for a teaching tool,
   not as a compliance obligation". Claiming a class as a regulatory status
   would imply a quality system this project does not have, so the framing
   needs the owner's judgment more than the letter does.

**The segmentation the audit first recommended is withdrawn (project owner,
2026-09-03).** It proposed Class C for `core/` and the readout path with
Class A for the app chrome, under IEC 62304 sections 4.3 and 5.3.5. The
question that retired it: what does a lower class buy a project whose gate is
already uniform?

Nothing, and it costs three things. The class letter governs how much process
and documentation a quality system demands - Class A exists to *exempt*
low-risk items from detailed design, unit verification and integration
testing - so with no quality system and `make check` applying one bar to the
whole tree, the exemption has nothing to exempt. The practices are already
Class C everywhere; declaring that is free, while declaring A for part of it
would be a claim to defend rather than a saving to collect.

The costs are specific. Class A means *no injury is possible*, and
`CLAUDE.md` holds that presentation correctness **is** safety - "the correct
number with the wrong units, label, patient context, stale state, model
name/version, or provenance is still a safety failure" - which is a direct
contradiction for the layer holding the halted-versus-paused distinction, the
displayed-precision constant, the ISO 5360 agent colours, and the decimation
`docs/MODEL.md` requires to preserve extremes. It would also draw a second
boundary across the one this project already has, which runs between the
product and the workflow apparatus and puts `app/` on the product side. And
the line does not sit still: `chart_downsampling.py` looks like chrome and is
safety-relevant, `theme.py` looks like styling and carries agent
identification, and the genuinely non-clinical residue is small enough to
test anyway.

A split would pay only where the exempted surface is large, genuinely
non-clinical, and its verification burden actually felt - none of which holds
while the gate runs in about seventy seconds. That is a trigger to watch for,
not a reason to build one now.

**Done when.** The decision is recorded, and if the section is written,
`make doc-check` passes and the reply says which documents were swept.
