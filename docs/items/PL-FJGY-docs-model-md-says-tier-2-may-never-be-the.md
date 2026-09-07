---
id: PL-FJGY
title: docs/MODEL.md says tier 2 may never be the authority for a stored value, and venous_pool_volume_l adopts a tier-2 source
status: untriaged
added: 2026-09-07
---

**Problem.** docs/MODEL.md says tier 2 may never be the authority for a stored value, and venous_pool_volume_l adopts a tier-2 source

**Decision needed.** Whether `docs/MODEL.md` § "Source hierarchy" admits a
tier-2 source as the authority for a stored value when the adoption is
recorded and reasoned, or whether `venous_pool_volume_l` is an exception the
section should name as one.

**Problem, in the document's own words.** § "Source hierarchy" states that of
the three tiers "only the first may be named as the authority for a stored
value", and of tier 2 that it is "never the authority for a stored value: the
rounding and the selection between disagreeing measurements happened somewhere
the reader cannot see". § "Why the Mapleson values are nonetheless not adopted
here" leans on exactly that rule as its first reason.

The same document then records that `venous_pool_volume_l` = 1.222 L is Davis
and Mapleson 1981, "**adopted on 2026-09-07, on the project owner's
decision**" (`PL-8ZJQ`), and states in the same paragraph why the paper is
tier 2: "Their Appendix derives it from ICRP (1975) blood distribution rather
than measuring it, which is what keeps it tier 2." So a tier-2 source is the
declared authority for a stored value, in a document that says twice that none
may be.

**Why the contradiction was invisible until now.** Both halves are prose, and
they sit about 400 lines apart. `PL-1JDD` made the claim machine-readable -
that entry now carries `"tier": "secondary", "adopted": true` - which is what
put the two facts on one line.

**Why the checker does not enforce the rule, and should not without an
answer.** `check_source_tiers` requires a recorded gap where no primary source
is adopted; it does not forbid adopting a lower tier, and could not: all twelve
partition coefficients adopt De Wolf et al., which is tier 3, deliberately and
disclosed. Enforcing "only tier 1 may be adopted" would fail every data file in
the repository on its first run. The hierarchy's first sentence is an
aspiration the project explicitly does not yet meet - which is a legitimate
state, and is what the `provenance_gap` strings now record - so what needs
deciding is the *wording*, not the practice.

**Three readings, and a recommendation.** (1) The rule is absolute and the
adoption was an error - unlikely, since the reasoning recorded with it is
sound and the value it replaced was sourced by nothing at all. (2) The rule
means "may not be the authority *silently*", and a recorded, reasoned,
dated adoption of a lower tier is admissible - which is what the project
actually does, three times over. (3) The rule stands and this is a named
exception. Recommend (2), written as a fourth paragraph in § "Source
hierarchy" stating what a lower-tier adoption owes a reader: the tier, the
reason no tier-1 source was available, and the date and decision. That is
what all four data files already carry, so it documents the practice rather
than changing it - and it removes the sentence `PL-8ZJQ`'s successor would
otherwise have to contradict again.

**Found.** `PL-1JDD`, 2026-09-07, on making the tier and the adoption
machine-readable.
