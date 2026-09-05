---
id: PL-T67Y
title: README's status section describes neither the playback rate nor the chart time base, the two v0.4.0 capabilities it never gained a paragraph for
status: untriaged
added: 2026-09-05
---

**Problem.** `README.md`'s status section has kept pace with most of v0.4.0 —
the MAC display unit, the fixed 0 to 3 ×MAC vertical range, per-compartment
trace selection, the $`F_A/F_I`$ plot, the agent-change confirmation — and
carries nothing at all about two of the milestone's three headline changes:

- **the playback rate** (`PL-SN2C`), which is what makes a case whose muscle
  and fat compartments have time constants of 135 min and 42 h watchable in a
  sitting; and
- **the chart's case-length time base** (`PL-SSBP`), the selectable window
  width from 15 minutes to 12 hours plus a fit-the-run default.

The paragraph at "Fresh gas flow, delivered concentration, alveolar
ventilation, and cardiac output can all be changed live during a run" is also
now incomplete in the way `docs/MODEL.md` § "Runtime controls" was before
`PL-RCTQ` fixed it: three interface controls change live too and none of them
reaches model state.

**Why it matters.** These are not omissions of detail. The milestone's own
stated end state is "a learner runs one case from induction to emergence — in
compressed time they can sit through, in the unit clinicians reason in, on a
time base that spans a case". The README describes the unit and neither of the
other two, so it describes a simulator that cannot do the thing the release was
for. A reader deciding whether this project is worth their time is the reader
this costs.

The playback rate is additionally a **mode**, and `docs/MODEL.md` § "Interface
boundary" requires it on screen at every rate for that reason. A README that
never mentions it leaves a reader to meet a 60× clock without having been told
one exists.

**Where.** `README.md` § "Current status". `docs/MODEL.md` § "Interface
boundary" (the playback-rate paragraph) and § "The chart's time base" carry the
substance to draw on; neither should be restated at length in the README.

**Blocked by the README freeze.** `.claude/rules/readme-hold.md` holds
`README.md` until the project owner lifts it. Found while sweeping
`docs/MODEL.md` for `PL-RCTQ` and left alone, as that rule requires.

**Probably a input to `PL-N092` rather than an edit of its own.** `PL-N092`
(rewrite README as a human-readable introduction) is the item that decides what
the status section is for, and it is likely to restructure this material rather
than accept two more paragraphs of it. Treat this as the list of what the
rewrite must not lose. That rewrite is itself waiting on a public-readiness
decision, so if the freeze lifts well before the rewrite becomes workable,
adding two sentences is a reasonable interim.

**Done when.** A reader of `README.md` alone learns that a run can be played
faster than real time and that the chart's window is a selectable span, or
`PL-N092` lands having covered both. `make doc-check` passes.
