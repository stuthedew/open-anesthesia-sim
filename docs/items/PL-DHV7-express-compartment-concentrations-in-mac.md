---
id: PL-DHV7
title: Express compartment concentrations in MAC multiples as a display unit
priority: P1
effort: M
status: ready
classes: safety, science
feature: chart-readout
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/parameters.py, docs/MODEL.md
added: 2026-08-25
---

**Problem.** Every compartment is displayed as a percentage of an
atmosphere. MAC exists in the code only as an internal starting point -
`mac_percent` per agent in `core/parameters.py` and the agent data files,
used to open the vaporizer at 1 MAC and to bound it - and is never a unit the
user sees.

**Why it matters.** MAC multiples are the unit the reference simulator plots
in and the unit clinicians reason in, and they are what makes agents
comparable: 2% is 1 MAC of sevoflurane and about a third of a MAC of
desflurane, so a percent axis silently changes meaning when the agent
changes. It is also a hard prerequisite for the MAC-denominated bookmarks of
`ROADMAP.md` planned milestone 26, which cannot be specified in a unit the
application does not have. Independently valuable - it does not need the
branching work to justify it.

**Where.** `app/simulation_view.py` (axis, labels, and readouts),
`app/controller.py` (`SimulationSnapshot`), `docs/MODEL.md` (the
transformation and its interpretation).

**Safety notes.** The arithmetic is trivial (`concentration_percent /
mac_percent`); the interpretation is not, and that is where the work is.
1 MAC is defined for the *end-tidal/alveolar* partial pressure at one
atmosphere in a nominal 40-year-old, without adjustment for age or
co-administered agents. Expressing a *tissue* partial pressure in MAC
multiples - the reference simulator does exactly this, and it is the point of
the VRG trace - means "this compartment's partial pressure equals 0.8x the
alveolar partial pressure that would be 1 MAC", not "the patient is at
0.8 MAC of anesthetic depth". Those read the same on a label and are not the
same claim. Decide the label wording and the units of the axis together, and
do not carry a MAC readout on a compartment where the convention has not been
stated in `docs/MODEL.md`.

**Done when.** A user can read every graphed compartment in MAC multiples,
the agent's `mac_percent` and its provenance are traceable from the display,
and `docs/MODEL.md` states what a MAC multiple on a non-alveolar compartment
does and does not assert.
