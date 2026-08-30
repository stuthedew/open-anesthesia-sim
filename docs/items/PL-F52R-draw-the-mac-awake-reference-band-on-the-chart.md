---
id: PL-F52R
title: Draw the MAC-awake reference band on the chart
priority: P1
effort: S
status: ready
classes: safety, science, ux
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/data/agents, docs/MODEL.md
added: 2026-08-25
---
**Problem.** A washout curve on its own has no endpoint. A learner turns the
vaporizer off, watches the alveolar trace fall, and has nothing to read it against -
so "how much longer does a three-hour case take to wake up than a twenty-minute
one" has no answer on the display, even though the model computes it.

**Why it matters.** The reference is what turns the washout curve from a shape into
a conclusion, and context-sensitive emergence is the lesson the compressed playback
(PL-SN2C) exists to make reachable. Without it the milestone delivers the ability to
watch a washout and not the ability to draw anything from it.

**Safety notes.** This is the item in the milestone closest to clinical prediction,
and the distinction has to be built in rather than disclaimed. Draw a *band* on the
chart, labelled as a population value for return of responsiveness. Never a readout
of the form "time to wake-up: 14 min": that reads as a prediction for this patient,
which the model does not support and which no amount of surrounding disclaimer
undoes. MAC-awake is also a different endpoint from MAC - responsiveness to command
rather than movement to incision - and the label has to say which.

**First step.** The value is not established and must not be taken from memory.
Source MAC-awake for each of the three agents from the primary literature, record it
in the agent data files with its citation the way `mac_percent` already is, and
check whether one fraction of MAC covers all three or whether each needs its own
value. The band follows the sources; do not draw it before they exist. Depends on
PL-DHV7 for the unit.

**Required property - which trace the band is read against.** The band must be
read against the *vessel-rich* trace, or against both alveolar and vessel-rich
with the difference between them stated. Measured on a 3-hour 1 MAC sevoflurane
case with the vaporizer turned off at 10 L/min: alveolar crosses 0.33 MAC at
3.01 min and vessel-rich at 6.72 min - 2.2x earlier.

The model has no effect-site compartment and defines F_a === F_A, so the
alveolar trace is the fastest curve on the chart and the furthest from where
responsiveness actually returns. A single band drawn across a six-trace chart
is read against whichever trace the eye reaches first, and that systematically
teaches an early wake-up - the opposite of the lesson the milestone exists to
deliver, and the direction with clinical consequence if it were carried across.

This is a distinct hazard from the one the Safety notes already guard. That
guard - never a per-patient time prediction - protects against over-reading the
number. This protects against reading a correct number against the wrong
compartment, which no amount of labelling the band as a population value
addresses.

**Done when.** Each agent's MAC-awake value is in its data file with a cited
primary source, `docs/MODEL.md` records the provenance and states what the band does
and does not assert, the chart draws it as a labelled population band with no
per-patient time prediction anywhere in the interface, and the interface makes
clear which trace the band is to be read against.
