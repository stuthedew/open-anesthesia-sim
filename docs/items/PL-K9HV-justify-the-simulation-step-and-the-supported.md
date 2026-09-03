---
id: PL-K9HV
title: Justify the simulation step and the supported ranges without reference to the readout's decimal count
status: untriaged
feature: numerical-domain
touches: src/anesthesia_sim/core/uptake_system.py, src/anesthesia_sim/core/supported_ranges.py, docs/MODEL.md
added: 2026-09-03
---

**Problem.** Two backend constants are currently justified *by* a presentation
choice rather than on their own terms. `MAXIMUM_SIMULATION_STEP_S = 0.1` is
explicitly not the step at which the operator split breaks down — the comment
says that is "two orders of magnitude away" — but "the largest step at which
what the interface shows is still what the model can support", where "what the
interface shows" means the two-decimal concentration readout. The supported
input intervals in `supported_ranges.py` are drawn the same way: cardiac output
is capped because beyond it the splitting error "turns the displayed
resolution's 'uncertain by about two counts' into 91 counts, an alveolar
readout wrong in its first decimal". Both therefore inherit whatever decimal
count the readout happens to use.

The project owner's statement of intent (2026-09-03): *"some of my decimal
point decisions were fairly arbitrary. I care about display decimal points in
UI. I didn't intend to dictate back end math."* The decimal count was a
presentation judgment; it was not meant to be the premise the integrator step
and the model's supported domain are derived from.

**Why it matters.** The dependency runs the wrong way. Numerical accuracy and
the physiological domain the model is valid over should bound what may be
displayed; instead an arbitrary readout choice bounds them. Two consequences
follow, and the second is the safety-relevant one:

1. A future decision to show one decimal instead of two would, by the same
   reasoning, license a larger step and wider input intervals — a UI change
   silently relaxing the integrator and the supported domain.
2. `supported_ranges.py` reads as a statement about where the *model* is
   valid. It is not: it is a statement about where the *readout* stays
   truthful at two decimals. A reader — or a session — treating the interval
   as a validity claim about the physiology would be wrong about what the
   guard is protecting, which is exactly the "correct number, wrong context"
   failure `CLAUDE.md`'s safety standard names.

Note the legitimate half, so the fix does not overshoot: choosing a numerical
tolerance from what a user will see is a sound engineering pattern, and
refusing to display digits the method cannot support is required. What is
wrong is the direction and the documentation of it — the display choice is
presented as a derivation rather than as a chosen tolerance, and nothing else
is offered as an independent justification for either constant.

**Where.**

- `src/anesthesia_sim/core/uptake_system.py:40-62` — the comment block above
  `MAXIMUM_SIMULATION_STEP_S`, and the "Raising it is a safety-critical change
  to every displayed value" framing that follows from it.
- `src/anesthesia_sim/core/supported_ranges.py:9-39` — the module docstring's
  "Why the model declares these and not the interface" and "Widening any
  interval is a safety-critical change" paragraphs.
- `docs/MODEL.md` §§ "Supported simulation step", "Supported input ranges",
  "Displayed precision" — the three are currently a single mutually-referring
  chain and would be re-cut together.

**Done when.** `MAXIMUM_SIMULATION_STEP_S` and each interval in
`supported_ranges.py` carry a justification that stands without reference to
any decimal count — an error tolerance stated in absolute units, or the
physiological/validity domain of the underlying parameter set — and the
displayed resolution is derived *from* those, in that order. Where a tolerance
was in fact chosen with the readout in mind, `docs/MODEL.md` says so as a
chosen tolerance rather than as a derivation, and states what changes if the
readout changes (which should be: nothing in `core/`).

**Not-delegable.** Whether the current values are right is a modelling
judgment, not a refactor: settling the step and the domain on their own terms
may confirm 0.1 s and the present intervals, or may move them. Wants the
strongest model, and the project owner's decision on any value that moves.

**Depends on.** Interacts with PL-88GQ (state every displayed decimal count as
a presentation decision the owner can revise), which is the display half of
the same finding. This item is the one that must land first: PL-88GQ cannot
call the readout freely revisable while `core/` derives two constants from it.
