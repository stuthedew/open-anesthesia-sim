---
id: PL-FJGY
title: docs/MODEL.md says tier 2 may never be the authority for a stored value, and venous_pool_volume_l adopts a tier-2 source
priority: P1
effort: S
status: done
classes: science, docs
feature: model-spec-accuracy
touches: docs/MODEL.md, src/anesthesia_sim/data
added: 2026-09-07
closed: 2026-09-07
verify: python3 tools/doc_check.py check && grep -qF 'A lower tier may be adopted, but never silently.' docs/MODEL.md && ! grep -rqF 'does not admit tier 2 as the authority' src/anesthesia_sim/data
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


**Decided 2026-09-07 by the project owner: reading (2), fix the wording rather
than the practice.** Built in the same session.

`docs/MODEL.md` § "Source hierarchy" now carries a fourth block, **"A lower
tier may be adopted, but never silently"**, which states what a stored value
whose authority is not a primary measurement owes a reader: the tier on the
entry itself, why no tier-1 source was adopted, and — where a lower tier is
adopted *in preference to* an available primary rather than for want of one —
the date and whose decision it was. `venous_pool_volume_l` is named as the
worked example. The block says in terms that this is a higher bar than a
tier-1 citation clears and is not a licence to prefer the convenient number:
the reason has to be that no primary measurement of the quantity in the
population exists or is reachable, never that finding one is work.

The three absolutes that the practice contradicted were rewritten rather than
deleted, so the preference for tier 1 survives:

- the section's opening sentence, which said only tier 1 may be named as the
  authority, now says only tier 1 may be named *on its own strength*;
- the tier-2 bullet's "never the authority for a stored value" is now "not the
  authority on its own strength ... adoptable only on the recorded decision
  below";
- the Lowe and Ernst paragraph, which said opening the book could change
  nothing unless it turned out to have measured, now adds that a book that
  collected could still be adopted on the record.

**The Mapleson passage needed the most care and its answer did not change.**
§ "Why the Mapleson values are nonetheless not adopted here" opened "Three
reasons, and the first is this document's own rule" — a rule that no longer
forbids the adoption outright. It now says that adopting Mapleson would take a
recorded decision, and that the two remaining reasons are why this one went the
other way: the lineage-mixing that a Mapleson divisor over a Gas Man trajectory
would produce, and confidence limits wide enough that no MAC source makes the
cross-agent comparison exact. Both were always the load-bearing reasons; the
first was the one doing no work.

**Seven restatements in the data files went with it**, because a note asserting
a rule the document no longer states is the same defect one step out: four
instances of "does not admit tier 2 as the authority for a stored value" (the
three agents' Nickalls and Mapleson entries and the reference patient's Wahba
entry) and three of "admits only tier 1 as the authority for a stored value"
(the three agents' Mapleson entries). Each now says the hierarchy admits a
tier-2 source only on a recorded decision, and that none has been taken for
that parameter — or, for the three MAC entries, that it was decided the other
way on 2026-09-04.

**Two restatements were deliberately left standing.** `ROADMAP.md`'s v0.3.2
row says that release's hierarchy admitted "only the first" tier as the
authority, which was true of v0.3.2; a release note is a record of what
shipped, and editing one to match a later decision falsifies it. And the
tier-**3** counterpart of this same absolute is stated in
`.claude/rules/expert-review.md`, `.claude/rules/sources-and-docstrings.md` and
`docs/consultant-brief.md` — all outside this item's `touches`, two of them
resident instructions — and is the wider problem, since tier 3 is the tier this
project actually adopts. `PL-X19T` carries it.

**No stored value changed and nothing was promoted.** The four data files
declare exactly the tiers and adoptions they declared before this item;
`venous_pool_volume_l` was already `"tier": "secondary", "adopted": true`. What
changed is that the standard now describes what the files do.

**Found.** `PL-1JDD` (make the source tier machine-readable so doc_check can
decide it), 2026-09-07. Making the tier and the adoption machine-readable is
what put the rule and the practice on one line; `PL-8ZJQ` is the adoption the
rule contradicted.
