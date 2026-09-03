---
id: PL-DHV7
title: Express compartment concentrations in MAC multiples as a display unit
priority: P1
effort: M
status: ready
classes: safety, science
feature: teachable-case
touches: src/anesthesia_sim/app/simulation_view.py, src/anesthesia_sim/app/formatting.py, src/anesthesia_sim/app/controller.py, src/anesthesia_sim/core/parameters.py, src/anesthesia_sim/data/agents/sevoflurane.json, src/anesthesia_sim/data/agents/isoflurane.json, src/anesthesia_sim/data/agents/desflurane.json, docs/MODEL.md, tests/unit/test_formatting.py
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

**Do this after PL-WB0X stage 1** (split `simulation_view.py`; extract
`app/formatting.py`). This item rewrites every formatter and adds a second unit
to `docs/MODEL.md`'s "Displayed precision" derivation. Those formatters are
currently private static methods on a 1082-line Flet view class, so the change
is hard to test in isolation and hard to cite from the specification. Extracting
them first is an `S` item and makes this one safer; see PL-WB0X's Sequencing
section.

**Done when.** A user can read every graphed compartment in MAC multiples,
the agent's `mac_percent` and its provenance are traceable from the display,
and `docs/MODEL.md` states what a MAC multiple on a non-alveolar compartment
does and does not assert.

**What v0.4.1 does to this (added 2026-09-03).** Two things, one of which is
worth designing around.

`PL-X9KD` re-derives `docs/MODEL.md` § "Displayed precision" from scratch after
`PL-GS5X` removes the splitting error, and this item extends that same section
with a second unit. So **express the MAC resolution as a function of the percent
resolution rather than deriving it independently** - MAC multiples are percent
divided by the agent's `mac_percent`, so a single stated percent resolution
determines both, and `PL-X9KD`'s re-derivation then propagates to both units for
free. Deriving the MAC count separately means re-deriving two things one release
later instead of one. (The unit conversion is not information-preserving across
agents - 0.01 percentage points is 0.005 MAC for sevoflurane and 0.0017 for
desflurane - so what to *display* is still a presentation decision; the point is
that its input should be one number, not two.)

Second, the formatters here read `snapshot.circuit_concentration_fraction`,
`alveolar_concentration_fraction` and `mixed_venous_concentration_fraction`
(`app/controller.py:22-27` on `SimulationHistorySample` and `:44-49` on
`SimulationSnapshot`), all three of which `PL-9SH6` renames to the shared
`_partial_pressure_fraction` form - as are the six accessor functions
`PL-WB0X` extracted into `app/chart_series.py:76-96`. Mechanical, but it means
this item's diff is re-touched by the rename pass.

`mac_percent` itself (`core/parameters.py`) is not touched by v0.4.1.

**`mac_percent`'s provenance tier changes when this lands (added 2026-09-03).**
Today `mac_percent` is a starting-value convenience: it opens the vaporizer at
1 MAC and bounds it, so an error in it moves only where the dial starts. This
item makes it the divisor of every displayed compartment value and both chart
axes, which is a clinically meaningful transformation under `CLAUDE.md`'s
safety-critical standard. The stored values are tier 3 - the flat adult MACs
De Wolf et al. state they used in Gas Man, adopted because the reference adult
has no age parameter - and all three data files carry a `note` that ends
"Used as the controller's starting delivered-concentration default (1 MAC),
not a governing-equation parameter." That clause becomes false the moment a
readout divides by it, so the three notes are part of this item's diff.

The size of the gap is not negligible, and it falls in the direction that
matters most here. Against Mapleson's age-40 meta-analytic MAC (Br J Anaesth
1996;76:179-85, doi:10.1093/bja/76.2.179 - the tier 1 source the data files
already cite through Nickalls and Mapleson), the stored values are:

| Agent | Stored `mac_percent` | Mapleson age-40 | Displayed MAC reads |
| --- | --- | --- | --- |
| Sevoflurane | 2.0% | 1.80% | 10% low |
| Desflurane | 6.0% | 6.6% | 10% high |
| Isoflurane | 1.2% | 1.17% | 2.5% low |

So a sevoflurane-versus-desflurane comparison in MAC multiples - the exact
comparison this item exists to make honest - is skewed by about 22% between
the two agents purely by the choice of MAC source.

**Decided: keep the Gas Man values and state the deviation** (project owner,
2026-09-03). `mac_percent` stays 2.0 / 6.0 / 1.2. Three reasons, and the first
is dispositive on its own: v0.4.0 changes no parameter, and editing
`mac_percent` would move the vaporizer's 1 MAC starting dial, so re-sourcing it
needs a scope exception this milestone has no reason to take. Second, those are
the round numbers quoted at the bedside, which is worth something in a display
whose purpose is teaching. Third, the ~22% cross-agent skew reverses no
qualitative teaching point - 2% is about 1 MAC of sevoflurane and about a third
of a MAC of desflurane on either source - so making the limitation visible
satisfies `CLAUDE.md`'s "make uncertainty and model limitations visible" better
than silently substituting a different denominator would.

So this item owes three things rather than a parameter change:

- the three data-file notes lose the clause "not a governing-equation
  parameter", which stops being true, and gain what the value is now used for;
- `docs/MODEL.md` states the denominator, its tier, and that it differs from
  the age-40 meta-analytic reference by up to 10% per agent and about 22%
  between sevoflurane and desflurane, so a cross-agent comparison in MAC
  carries that much source-choice error before any model error;
- the display names the agent and the source of the denominator it divided by.

The tier upgrade itself is not dropped, only placed: it is a parameter change,
so it belongs to v0.4.1 or Gate 1, whichever reaches it first. Do not adopt the
age-related iso-MAC form (Nickalls and Mapleson, Br J Anaesth 2003;91:170-4,
doi:10.1093/bja/aeg132) in either place - that needs an age parameter the
reference adult does not have, and inventing one is a modelling change, not a
display one.

The displayed MAC denominator names its agent and its
source at the point of display, per the "traceable from the display"
requirement above.
