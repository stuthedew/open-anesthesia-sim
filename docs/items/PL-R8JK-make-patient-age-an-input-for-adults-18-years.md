---
id: PL-R8JK
title: Make patient age an input for adults, 18 years and older, refusing any age outside its sourced range with a notice that names the limit and the value
priority: P1
effort: M
status: ready
classes: feature, safety
feature: patient-model
touches: src/anesthesia_sim/core, src/anesthesia_sim/data, src/anesthesia_sim/app, docs/MODEL.md, docs/INTERFACE.md, tests
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: a user sets the patient's age, from 18 years, and an age outside the sourced range is refused with a notice that says why
---

**Problem.** Make patient age an input for adults, 18 years and older, refusing any age outside its sourced range with a notice that names the limit and the value

**Why it matters.** `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 6. Age is the input that moves
MAC: about 6% per decade for every agent (Mapleson 1996, *Br J Anaesth*
76:179-85, p. 181).

**The range.** The lower limit is 18 years (project owner, 2026-11-27,
ratified, over children from 1 year on an adult body scaled by weight).
Mapleson's equation holds from 1 year (p. 181), and restricting his data to 18
and over barely changed the fit (p. 180). The body model is an adult's, and
young children's shares of body mass and cardiac output differ substantially
(Davis and Mapleson 1981, *Br J Anaesth* 53:399-405, p. 402). The upper limit
is the oldest age in Mapleson's data, read from his Table 1. The default is
40 years, the age the stored MAC belongs to.

**Done when.** A user can set an age within the range; an age outside it is
refused with a notice that names the limit, the value entered, and what to
enter instead; and the refusal is tested at both limits.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
