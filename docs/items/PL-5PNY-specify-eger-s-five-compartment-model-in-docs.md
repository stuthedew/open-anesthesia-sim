---
id: PL-5PNY
title: Specify Eger's five-compartment model in docs/MODEL.md and docs/PARAMETERS.md, with a sourced intertissue compartment and lung store, before any code changes
priority: P1
effort: L
status: blocked
classes: science, docs
feature: patient-model
touches: docs/MODEL.md, docs/PARAMETERS.md
blocked-by: PL-64NJ
deferred-from: v0.7.0 - filed 2026-11-27 as v0.8.0's Required scope (PL-8NDZ), after Gate 3 froze. Not live: checked 2026-11-27 at 009da829, the tree has no patient age or weight input and no fifth compartment, so no displayed value is wrong until this work starts
added: 2026-11-27
payoff: the five-compartment model is specified from sources read in full before any code changes
---

**Problem.** Specify Eger's five-compartment model in docs/MODEL.md and docs/PARAMETERS.md, with a sourced intertissue compartment and lung store, before any code changes

**Why it matters.** The project's rules require equations, units, assumptions
and reference cases to be defined before the scientific core changes. The
four-compartment form overestimates uptake early and underestimates it after
30 to 45 minutes (Hendrickx and De Wolf 2008, *Modern Anesthetics*, p. 164),
and every one of Yasuda's 14 human data sets needed a fifth compartment
(Yasuda et al. 1991, *Anesth Analg* 72:316-24). `ROADMAP.md` § "v0.8.0 - the patient, on the five-compartment model", Required scope entry 1.

**What the specification fixes:**

1. The intertissue compartment is a parallel compartment at fat solubility,
   2.9 L in the reference adult (Eger and Saidman 2005, *Anesth Analg*
   100:1020-33, Table 3, p. 1024).
2. Its blood flow is a share of cardiac output, not flow added on top. In
   Yasuda's Table 5 the five compartments' flows sum to the measured total
   clearance of 3.6 L/min (p. 321).
3. Eger and Saidman's figures feed it by diffusion from the vessel-rich and
   muscle groups, while Table 3 and Yasuda give it a flow equivalent. The
   specification chooses one and records why, from the sources.
4. The split of cardiac output among the compartments is re-derived from the
   five-compartment sources. Today's 76/18/6 split is Gas Man's.
5. Lung tissue and pulmonary blood join the alveolar gas as one central store.
   Davis and Mapleson's standard man, from ICRP Reference Man, gives 464 mL of
   lung tissue and 506 mL of pulmonary blood at 70 kg (*Br J Anaesth*
   1981;53:399-405, Table I, p. 401). Adopt these or name a better source read
   in full.
6. `docs/PARAMETERS.md` gives each new value its source, page and tier.

All the papers named are in the private reference corpus, read in full.

**Done when.** `docs/MODEL.md` states the five-compartment equations, units and
assumptions, and `docs/PARAMETERS.md` gives every new value a source read in
full, with its page.

**Generator check.** None: filed by the v0.8.0 scoping round (`PL-8NDZ`) from its approved scope, not by a finding.
