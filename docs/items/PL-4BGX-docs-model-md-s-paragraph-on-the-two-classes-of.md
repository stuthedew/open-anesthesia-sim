---
id: PL-4BGX
title: docs/MODEL.md's paragraph on the two classes of vaporizer is unclear and uses its own terms: it never says the maxima are dial maxima or how the classes differ, and states the altitude difference more firmly than a source the project can cite
status: untriaged
touches: docs/MODEL.md
added: 2026-11-07
---

**Problem.** docs/MODEL.md's paragraph on the two classes of vaporizer is unclear and uses its own terms: it never says the maxima are dial maxima or how the classes differ, and states the altitude difference more firmly than a source the project can cite

**Where.** `docs/MODEL.md` § "Delivery-limit and MAC parameters", the paragraph that opens "**The three maxima come from two classes of vaporizer, which this model would need to tell apart only away from sea level.**" (line 4068 on `main` on 2026-11-07).

**What the owner said.** Shown the copy editor's edit of this paragraph in `PL-F0Q2`'s debug runs, the project owner asked "“The three maxima come from two classes of vaporizer.” what does that mean?", rejected it ("Yes. Reject"), and asked for the terms to match the reference chapter (2026-11-07, 21:59Z to 22:04Z). The rejected edit is in `docs/prose-review/rejected/unclear-2026-11-07-two-classes-of-vaporizer.md`. The original has the same two gaps: "maxima" never says it means each agent's highest dial setting, and the paragraph names the two classes without saying how they work.

**A source the project can cite.** Dosch MP, Tharp D. *The Anesthesia Gas Machine*, "Processing: Vaporizers". University of Detroit Mercy, revised February 2026. https://healthprofessions.udmercy.edu/academics/na/agm/05. It classifies the Vapor 2000 and similar vaporizers as "variable bypass, flow over, temperature compensated, agent-specific, out of circuit", and says "The Tec 6 desflurane vaporizer is not a variable bypass vaporizer, it is an injector (i.e. gas-vapor blender)", "electrically heated, dual circuit injector, constant-temperature, agent specific, and out-of-circuit". On altitude it says "The effect of altitude on vaporizer performance is controversial", that some sources say variable-bypass vaporizers need no adjustment "but the Tec 6 must be dialed up beyond the desired dose at higher altitudes", and "Other sources disagree". A session cited Dorsch JA, Dorsch SE, *Understanding Anesthesia Equipment*, 5th ed., chapter 6, and the owner asked for the terms to match it, but no session could open it on 2026-11-07. The Tec 6's design is also in Johnston RV, Andrews JJ, et al., Anesth Analg 1994;79:548-52, doi:10.1213/00000539-199409000-00025.

**Recommendation.** Rewrite the paragraph for a clinician. Say that each agent's limit is the highest setting of its vaporizer's dial. Name the two designs in the source's terms: sevoflurane's and isoflurane's limits come from variable-bypass vaporizers, and desflurane's from the Tec 6, an electrically heated, dual-circuit gas-vapor blender. Keep why the model need not tell them apart (ambient pressure fixed at 760 mmHg), and state the altitude difference only as firmly as the cited source does. Check Dorsch and Dorsch's chapter 6 for its terms first, where a copy can be reached. This is a content fix to the safety-critical specification, so it takes the owner's read.
