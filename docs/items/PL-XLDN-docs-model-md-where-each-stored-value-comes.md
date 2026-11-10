---
id: PL-XLDN
title: docs/MODEL.md § 'Where each stored value comes from' says a measurement beside a tier-3 number does not source it, 'which is the second of the three rules below', but the three rules are above it, in § 'Source hierarchy'
status: untriaged
feature: model-md-structure
added: 2026-11-10
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
