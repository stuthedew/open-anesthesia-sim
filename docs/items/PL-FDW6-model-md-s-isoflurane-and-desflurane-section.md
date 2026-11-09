---
id: PL-FDW6
title: MODEL.md's isoflurane and desflurane section says any weighted average of Yasuda's brain, heart, liver and kidney values lands away from sevoflurane's stored 1.1, but their equal-weight mean is 1.0975; it also says storing Yasuda's figures would move three displayed time constants, though seven of the nine stored values would change
priority: P2
effort: S
status: done
classes: docs
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-07
closed: 2026-11-07
pr: 2054
payoff: the isoflurane and desflurane section says the three agents share one set of equations, and its claims about weighting and time constants match its own table
verify: grep -qF 'Because the equations are shared, lower solubility' docs/MODEL.md && ! grep -qF 'would move three displayed time constants' docs/MODEL.md
---

**Problem.** MODEL.md's isoflurane and desflurane section says any weighted average of Yasuda's brain, heart, liver and kidney values lands away from sevoflurane's stored 1.1, but their equal-weight mean is 1.0975; it also says storing Yasuda's figures would move three displayed time constants, though seven of the nine stored values would change

**Where it was found.** The copy editor raised both as queries while `PL-F0Q2` tested it on this section as it stood before `#2049`, and `main` still has both sentences. In § "v0.2.0: isoflurane and desflurane", the vessel-rich bullet says "Any weighted average of the four would land away from the stored figure", yet sevoflurane's four values (1.15, 1.21, 1.25, 0.78) span the stored 1.1, and their equal-weight mean, 1.0975, rounds to it. The *Declined* paragraph says that storing Yasuda's figures "would move three displayed time constants", but the table shows seven of the nine stored values differing from Yasuda's means, such as isoflurane muscle at 4.5 against 4.40. The section should say which weighting it means and which time constants are displayed, or correct the claims. The copy editor also asked whether "Only the partition coefficients differ" means to exclude each agent's stored MAC, which the same section mentions.

**The section's opening sentence reads as if there were sevoflurane equations.** It says "Isoflurane and desflurane use the same equations, compartments and reference adult patient as sevoflurane." The project owner read it on 2026-11-07 (16:54 UTC) as implying a set of "sevo equations", and asked for it to say so plainly if the equations are generic. They are. § "Status" says every supported agent shares one set of equations, and nothing under `core/` branches on the agent. The wording comes from release history: v0.1.0 modeled sevoflurane only, and v0.2.0 added the other two. The copy editor kept the sentence, correctly, because the shared set is not stated in this section and a copy edit adds no fact. The recommended wording below also settles the copy editor's query about "Only the partition coefficients differ":

> Sevoflurane, isoflurane and desflurane share one set of equations, compartments and reference adult patient (§ "Governing equations"). An agent enters those equations only through its four partition coefficients: one blood:gas and three tissue:gas. Its other stored values, such as its MAC and its vaporizer's maximum, set a control or convert a displayed amount, and the equations do not use them (§ "Delivery-limit and MAC parameters", § "Agent amount").

The paragraph's later sentence "With the same equations, lower solubility only makes the agent equilibrate faster" then becomes "Because the equations are shared, lower solubility only makes the agent equilibrate faster." § "Purpose" keeps "v0.2.0 added isoflurane and desflurane as selectable agents, using the same equations", where release history is the subject.

**Fixed 2026-11-07 in pull request 2054** (at the coordinator's request, relaying
the owner's 20:09 UTC question). The opening now uses the recommended wording
above, and the later sentence reads "Because the equations are shared". The pull
request also corrects the two claims:

- The vessel-rich bullet now says the equal-weight mean, 1.0975, also rounds to
  sevoflurane's stored 1.1, so sevoflurane's figure alone does not show which
  value was stored. It adds that isoflurane's and desflurane's stored values
  equal Yasuda's brain values to the stored precision, as the table shows. This
  repository has no heart, liver or kidney values for those two agents, so the
  old claim about every weighting was not restated.
- The *Declined* paragraph now says storing Yasuda's figures would change seven
  of the nine values, and the time constant of each compartment they belong to.
  Three changes are large (the same +4.5%, −8.3% and −7.7%), and the other four
  move by 3.1% or less (isoflurane muscle 4.40/4.5, desflurane muscle 0.94/0.97,
  sevoflurane muscle 2.38/2.4, isoflurane vessel-rich 2.09/2.1). A tissue time
  constant is proportional to its tissue:gas coefficient when the blood:gas
  value is unchanged.

**Generator check.** One-off: the opening's wording came from release history (v0.1.0 modelled sevoflurane only), and the two claims were each a single misstatement.
