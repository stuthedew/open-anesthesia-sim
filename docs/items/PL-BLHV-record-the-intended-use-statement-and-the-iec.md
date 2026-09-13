---
id: PL-BLHV
title: Record the intended-use statement and the IEC 62304 safety classification in docs/MODEL.md
priority: P2
effort: M
status: done
classes: docs, planning
milestone: v0.4.21
touches: docs/MODEL.md
added: 2026-09-02
closed: 2026-09-13
pr: 547
verify: python3 tools/doc_check.py check && grep -qF 'not intended for entering, importing, or reproducing the parameter values of' docs/MODEL.md
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
the line does not sit still: `chart_series.py` looks like chrome and decides
what a trace asserts about the run, `theme.py` looks like styling and carries agent
identification, and the genuinely non-clinical residue is small enough to
test anyway.

A split would pay only where the exempted surface is large, genuinely
non-clinical, and its verification burden actually felt - none of which holds
while the gate runs in about seventy seconds. That is a trigger to watch for,
not a reason to build one now.

**Done when.** The decision is recorded, and if the section is written,
`make doc-check` passes and the reply says which documents were swept.

## Worked 2026-09-13: parts 2 and 3 are settled, part 1 is drafted, one clause needs the owner

**Part 3's framing needs no fresh judgment — the precedent is in this same
document, and it is quotable.** `docs/MODEL.md` § "Color contrast, and the standard
this interface is held to" already makes exactly the move: "none of those instruments
binds this project — AA is chosen as the right engineering bar for a teaching tool,
not as a compliance obligation." The classification section copies that sentence's
shape, so the risk of reading as a claimed regulatory status is handled by an
in-document convention rather than by new wording.

**One claim in this brief did not survive checking, and it would have gone into a
document that cites standards.** The brief states that "IEC 62304's own convention is
that an *undocumented* classification defaults to Class C". The sources reachable here
do not say that. What they do say is the § 4.3 decision flow — death or serious injury
possible is Class C, non-serious injury Class B, no injury possible Class A — together
with Annex B.4.3's rule that where software is in the chain leading to a hazardous
situation, the probability of the software failing is set to 1 rather than estimated.
That pair supports the Class C decision at least as strongly and is checkable, so it
is what the section should cite. The "defaults to C" phrasing must not be written into
`docs/MODEL.md` as a statement about the standard.

**The FDA support is stronger than the brief has it.** FDA's published list of software
functions that are not devices includes, as a worked example, "games that simulate
various cardiac arrest scenarios to train health professionals in advanced
cardiopulmonary resuscitation (CPR) skills" — a direct analogue to this project, not a
distant one. The carve-out rests on the software not "facilitating a health
professional's assessment of a specific patient, replacing the judgment of clinical
personnel, or performing any clinical assessment".

**That last phrase is what makes the intended-use wording load-bearing rather than
decorative, and it is why the brief's proposed exclusion clause is the wrong line to
draw.** The brief proposed excluding "use with or in the presence of an actual
patient". Physical proximity is simultaneously too broad and too narrow:

- **Too broad.** It forbids a resident running the simulator on a workstation during a
  case, which is one of the better teaching moments available and carries no hazard of
  its own.
- **Too narrow.** It permits entering a real patient's weight, age and cardiac output
  from the chart at a desk, which is the thing FDA's carve-out is actually conditioned
  against and the thing `ROADMAP.md` item 30 makes reachable once covariates land.

The boundary that tracks both the hazard and the carve-out is **the patient's data,
not the patient's location**: the tool is for teaching with hypothetical or
illustrative parameters, and is not for entering or reproducing an identifiable
patient's values, nor for informing the management of a specific patient. That is a
recommendation on the direction of the statement, so it is the project owner's to
accept or replace; the section is not written until they have.

**Sources checked 2026-09-13**, and each is the current version:

- IEC 62304 § 4.3 safety classes and Annex B.4.3's probability-of-failure rule
  (secondary summaries; the standard itself is paywalled and was not reached from
  here, which the section should say rather than implying a reading of the text).
- ISO 14971:2019 § 5.2, reasonably foreseeable misuse as a defined term.
- FDA, "Examples of Software Functions That Are NOT Medical Devices"
  (https://www.fda.gov/medical-devices/device-software-functions-including-mobile-medical-applications/examples-software-functions-are-not-medical-devices),
  and "Policy for Device Software Functions and Mobile Medical Applications".

**Still open, and only this:** the scope of the exclusion clause — the data-boundary
wording recommended above, or the proximity wording the brief first proposed. Parts 2
and 3 are answered and need nothing further.

## Written 2026-09-13, on the project owner's answer: the data boundary

The owner took the recommended exclusion clause, so `docs/MODEL.md` gains
`## Intended use, and the safety class this project holds itself to`,
immediately after "Status" and before "Purpose". Four subsections:

**Intended use.** A positive statement — a teaching simulator for
volatile-agent uptake and distribution, for clinicians, trainees and students,
whose particular value is showing the compartments no monitor displays.

**The exclusion, drawn at the data.** Not intended for entering, importing or
reproducing an identifiable patient's parameter values, and not intended to
inform the management of a specific patient. The section states why the
boundary is the data rather than proximity, because the reasoning is what stops
a later reader "simplifying" it back: proximity forbids a resident running the
simulator on a workstation during a case, which carries no hazard, and permits a
run built from a real patient's weight, age and cardiac output at a desk, which
is a prediction about that patient whatever the window is labelled. Proximity
gets both cases wrong, in opposite directions.

**Class C, uniformly**, with the three arguments from the audit's withdrawn
segmentation recorded as the reasons: a lower class has nothing to exempt under
one uniform gate; Class A asserts no injury is possible, which the layer holding
the halted/paused distinction and the ISO 5360 colours cannot assert; and the
boundary would not sit still, since `src/anesthesia_sim/app/chart_series.py`
looks like chrome and decides what a trace asserts.

**Framed as an engineering bar**, quoting this document's own WCAG sentence —
"chosen as the right engineering bar for a teaching tool, not as a compliance
obligation" — verified verbatim against the source section rather than
paraphrased.

**The brief's IEC 62304 claim was corrected rather than written down.** There is
no "undocumented classification defaults to Class C" sentence in the sources
reachable from here. What the section cites instead is § 4.3's three class
definitions plus Annex B.4.3's rule that a software failure's probability is
**set to 1** rather than estimated — which is the stronger argument anyway,
because it makes the class turn on severity alone and forecloses "this would
rarely be wrong" as a case for Class B.

**And the section says where its own knowledge of the standards came from.** IEC
62304 and ISO 14971 are paywalled and were not reached from this environment;
the clause numbers and class definitions came from secondary summaries, the FDA
material from the source. The section records that distinction and tells a
reviewer the conclusion does not depend on the wording but the clause numbers do.
Writing a confident clause citation that nobody checked into the document that
specifies a safety-critical model is the failure this avoids.

**The FDA support turned out stronger than the brief had it.** The published
non-device examples include "games that simulate various cardiac arrest scenarios
to train health professionals in advanced cardiopulmonary resuscitation (CPR)
skills" — a direct analogue. More useful still, the carve-out is conditioned on
the software not facilitating assessment of a *specific patient*, which is what
makes the intended-use statement load-bearing and what independently picks the
data boundary over the proximity one.

**Verified.** The `verify:` command's `grep` fails against `origin/main`'s copy
of `docs/MODEL.md` and the whole command passes here. `make check` green.
Docs swept: `docs/MODEL.md` (edited), `README.md` (read — its own disclaimer is
the short negative form and stays correct; it now has a fuller statement to
point at, which is `PL-FDBK`'s interface question rather than this item's),
`ROADMAP.md` (read — the covariate work this section anticipates is in "Planned
milestones" and v0.4.0's out-of-scope list, both consistent).
