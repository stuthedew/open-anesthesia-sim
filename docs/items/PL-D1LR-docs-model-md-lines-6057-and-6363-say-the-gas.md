---
id: PL-D1LR
title: docs/MODEL.md lines 6057 and 6363 say the gas accumulators are displayed to six decimals of a litre (1e-6 L) and size the canonical-versus-display margin against that, but § on the agent-accounting panel (line 10154) says its amounts have shown 0.1 L since PL-TG60, so both margins are measured against a resolution the display no longer has (found by the PL-XK00 blind review, 2026-10-25)
priority: P1
effort: S
status: ready
classes: docs, science
feature: stale-source-claims
touches: docs/MODEL.md
added: 2026-10-25
payoff: docs/MODEL.md states the resolution the agent-accounting panel actually shows, and its headroom argument is made against that number
verify: ! grep -qF 'accumulators are displayed as six decimals of a litre' docs/MODEL.md && ! grep -qF 'the 1e-4 and 1e-6 of' docs/MODEL.md
reenters: PL-4FBP
---

**Problem.** `docs/MODEL.md` § "The canonical evaluation rule" says the gas
accumulators are "displayed as six decimals of a litre, which resolves 1e-6 L",
and sizes the headroom between the canonical and display paths against that.
A later paragraph in the same part of the document compares a difference with
"the 1e-4 and 1e-6 of § "Displayed precision"". But § "Displayed precision"
says the agent-accounting panel's three amounts are displayed to 0.1 L since
`PL-TG60`. So both margins are measured against a resolution the display no
longer has. Found by the `PL-XK00` blind review on 2026-10-25. The title's line
numbers date from that day; the sections named here are the anchors.

**Reproduced 2026-10-31.** `grep -n 'six decimals of a litre' docs/MODEL.md`
and `grep -n 'the 1e-4 and 1e-6 of' docs/MODEL.md` each find the sentence, and
§ "Displayed precision" states 0.1 L for the panel's amounts.

**Why it matters.** `docs/MODEL.md` is the authoritative specification, and
these sentences state a displayed precision the interface no longer has. A
reader who trusts them believes the panel resolves a microlitre of vapour. The
margin itself errs on the safe side, since 0.1 L is coarser, but the argument
for it is stated against the wrong number.

**Done when.** Both sentences state the resolution § "Displayed precision"
gives, and the headroom is re-stated against it, or the sentences say which
display still prints six decimals, if one does.

**Generator check.** `PL-4FBP`'s fact: the link between a document sentence and
the tree fact it restates, here the display's resolution. `PL-4FBP` closed on
2026-09-19, so this is an instance filed after its head closed, recorded as
`reenters: PL-4FBP` (`PL-R4Y2`'s triage, 2026-10-31).
