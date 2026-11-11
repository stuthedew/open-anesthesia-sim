---
id: PL-XLDN
title: docs/MODEL.md § 'Where each stored value comes from' says a measurement beside a tier-3 number does not source it, 'which is the second of the three rules below', but the three rules are above it, in § 'Source hierarchy'
priority: P3
effort: S
status: blocked
classes: defect, docs
feature: model-md-structure
touches: docs/MODEL.md
blocked-by: PL-48MX
deferred-from: v0.7.0 - not present at the freeze: the sentence came with cfd4a4b61 on 2026-11-09, and every displayed value is correct
added: 2026-11-10
payoff: a clinician following the pointer to the sourcing rule finds it
---

**Problem.** docs/MODEL.md § 'Where each stored value comes from' says a measurement beside a tier-3 number does not source it, 'which is the second of the three rules below', but the three rules are above it, in § 'Source hierarchy'

**Where.** The paragraph that opens "**The reference patient's data file still
adopts no primary source for any of its eleven parameters**" ends its third
sentence with "which is the second of the three rules below". The three rules
are the list that opens "Three rules apply to an entry under `sources`:", which
comes before that paragraph, at the end of § "Source hierarchy: what may be
cited as the authority for a value". Its second bullet is the rule meant: "Do
not let a primary citation stand in for a primary value."

**Fix.** Change "below" to "above", or name the rule by its words. Naming it is
better, because a later restructure can move the list again. This is a
one-word change in a clinician-facing section, so it is filed rather than
fixed in passing.

**Found by** the reverse outline of `docs/MODEL.md` made on 2026-11-10 against
`main` at `f54250086`, and checked against the text then.

**Reproduced 2026-11-11.** `docs/MODEL.md` still reads "which is the second of the three rules below".

**Why it matters.** A clinician checking why the reference patient's values count as unsourced looks below the sentence for the rule and does not find it.

**Done when.** The sentence names the rule by its words, "Do not let a primary citation stand in for a primary value", wherever the replacement of `docs/MODEL.md` (`PL-48MX`) leaves it.

**Blocked on the replacement of `docs/MODEL.md`.** The owner decided on 2026-11-11 to split `docs/MODEL.md` by reader (`PL-P3GZ`), and `PL-48MX` replaces what is left of it with the clinician's model description. A one-word edit now would land in text that `PL-48MX` rewrites.

**Generator check.** A one-off: a pointer by position that a restructure moved. Naming the rule by its words removes the position.
