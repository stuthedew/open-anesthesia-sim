---
id: PL-0YR1
title: docs/MODEL.md § MAC-awake as a chart reference says the three fractions 'sit in a narrow range, so each agent carries its own value', but a narrow range argues for one shared fraction; the stated reason does not support the choice
priority: P2
effort: S
status: untriaged
feature: model-md-structure
touches: docs/MODEL.md
added: 2026-11-05
payoff: a clinician who asks why each agent keeps its own MAC-awake fraction reads the reason the sources support, not one that argues the other way
verify: ! grep -qF 'narrow range, so each agent carries' docs/MODEL.md
---

**Problem.** `docs/MODEL.md` § "MAC-awake as a chart reference" says the three fractions "sit in a narrow range, so each agent carries its own value". A narrow range argues for one shared fraction, so the stated reason does not support the choice.

**Checked 2026-11-09:** `grep -n 'narrow range' docs/MODEL.md` still finds the
sentence after the restructure, in § "MAC-awake as a chart reference" (line
7199): "The three fractions (0.31 isoflurane, 0.34 sevoflurane, 0.36
desflurane) sit in a narrow range, so each agent carries its own value rather
than one fraction covering all three." The same paragraph gives a sound reason
just before it: the fractions were found by different methods, descending for
Katoh's isoflurane and sevoflurane arms and ascending for desflurane, and the
two kinds of determination are not interchangeable.

**Why it matters.** A clinician who asks why each agent's MAC-awake band sits
where it does reads a reason that argues for the opposite choice. That makes
the stored fractions look arbitrary, although the paragraph holds a sound
reason for keeping them separate.

**Done when.** The sentence gives the reason the paragraph supports: each
agent keeps its own study's fraction because the methods differ. The narrow
spread is stated as a fact, not as the reason. The three stored fractions and
their provenance markers are unchanged.

**Generator check.** One-off: a finding from the `docs/MODEL.md`
structure-read sweep of 2026-11-05. The fact misread is the reason for one
parameter choice, and no head states it.

**Present at the Gate 3 freeze (checked 2026-11-09).** The passage this item
fixes was already in its file at `817a4d88`, the commit that froze Gate 3, so
under ROADMAP.md § "The gate is a snapshot, not a moving target" the item
joins v0.7.0's frozen list rather than being deferred by its capture date.
