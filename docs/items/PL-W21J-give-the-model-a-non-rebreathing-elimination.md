---
id: PL-W21J
title: Give the model a non-rebreathing elimination mode, so washout can be validated rather than only measured
priority: P1
effort: L
status: needs-decision
classes: science, feature
feature: numerical-domain
touches: src/anesthesia_sim/core/circuit.py, src/anesthesia_sim/core/governing_equations.py, docs/MODEL.md, tests/reference/test_published_wash_in.py
added: 2026-09-06
---

**Problem.** `tests/reference/test_published_wash_in.py` now compares modelled
`F_A/F_A0` at five minutes of elimination against all four Yasuda cohorts, and
the comparison misses every one of them by +1.0 to +5.0 published SD. Most of
that is apparatus rather than physiology, measured on 2026-09-06: this model
always rebreathes, so through an elimination the inspired fraction settles near
`V_A/(V_A + FGF)` of the alveolar one - 0.29 at the highest supported flow, and
measured at 0.30 to 0.32 at five minutes - and `F_A/F_A0` has no denominator
term to divide that out, so agent coming back from the circuit is counted as
though it had come back out of the patient. Holding `F_I` at zero instead moves
sevoflurane, isoflurane and desflurane from +3.67, +4.02 and +1.02 SD to -0.25,
+0.54 and -2.40 SD.

**Why it matters.** The published protocols measured mixed expired
concentrations and reported agent recovered against agent taken up, which needs
the whole expirate collected rather than returned to the subject, so their
elimination ran at an inspired fraction at or near zero. The model cannot be
set to that at any supported fresh gas flow, so the one comparison this
repository has in the elimination direction is a regression band rather than a
validation. With a non-rebreathing mode it would be a validation, and the
result would be worth having in both outcomes: it would either put two of the
three agents inside the published spread or turn desflurane's -2.40 SD into a
real disagreement about tissue return to explain.

**Where.** `src/anesthesia_sim/core/circuit.py` and
`src/anesthesia_sim/core/governing_equations.py` for the mode itself,
`docs/MODEL.md` "Model boundary", "Assumptions" and "Known limitations" for
what it changes about the stated boundary, and
`tests/reference/test_published_wash_in.py` for the comparison it would let be
written as an agreement claim.

**Design note before starting.** A supported non-rebreathing mode is a change
to the model boundary rather than a test fixture, so it needs the project
owner's decision first: it adds a mode the interface would have to make
visible, and `CLAUDE.md` treats a hidden mode as a human-factors defect in its
own right. The cheaper alternative, worth costing against it, is a
test-only open-circuit driver that is honest about being one - it would answer
the scientific question without adding a user-visible mode, at the price of
validating something the shipped simulator cannot do.

**Done when.** The elimination comparison can be run at an inspired fraction of
zero through a supported path, `docs/MODEL.md` records what that path changes
about the model boundary, and the comparison against the four published cohorts
is restated as whatever it then turns out to be.

**Decision needed.** Does the model gain a supported non-rebreathing
elimination mode, or a test-only open-circuit driver that is honest about being
one? The first changes the stated model boundary and adds a mode the interface
has to make visible, which `CLAUDE.md` counts as a human-factors defect if
hidden; the second answers the scientific question at the price of validating
something the shipped simulator cannot do. Sized `L` and out of the current
milestone either way, so a third answer is one line of intent in `ROADMAP.md`
and no items yet.
