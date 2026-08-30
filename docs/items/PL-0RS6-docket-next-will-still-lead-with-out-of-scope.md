---
id: PL-0RS6
title: docket next will still lead with out-of-scope work after PL-1TPM, because marking does not reorder
priority: P2
effort: S
status: done
closed: 2026-08-30
pr: 92
commit: dc7de31
classes: defect, infra
verify: uv run pytest subprojects/docket/tests/test_plan.py -k in_scope
feature: planning-cadence
touches: subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_plan.py
added: 2026-08-30
---

**Problem.** `PL-1TPM` makes `docket next` *mark* a suggestion whose id appears
in a milestone section the current step has not reached. It deliberately does
not reorder. So after it lands, `docket next` still ranks strictly by band and
still puts an out-of-scope P1 at position 1 - now with a suffix saying so.
Measured on 2026-08-30, its top three were PL-9Y42, PL-0MLQ and PL-F52R, all
P1 product work, while the beat was the workflow gate.

**Why it matters.** The owner's loop is meant to be: read the digest, say
"work the next gate item". That works, because the beat and `CLAUDE.md`'s
ordering rule both point at the gate. But `docket next` is the command whose
name promises the answer, and a reader who runs it - or skims its first line -
is handed work the current step excludes. `PL-1TPM` fixes the *fact* being
missing; the ordering still argues against the plan.

**Where.** `subprojects/docket/src/docket/plan.py`, the ranking, after
`PL-1TPM` supplies the in-scope/out-of-scope fact.

**Why this is not just PL-1TPM's job.** That item weighed marking against
*suppressing* and chose marking, because "is this really out of scope?" is a
judgment and a hidden item would be a verdict the tool cannot support. That
reasoning is right and this does not reopen it. Preferring in-scope work in the
ordering is a third option it did not consider: strictly weaker than
suppressing, since everything stays visible and the marking still carries the
fact, and strictly more useful than marking alone, since the first line stops
disagreeing with the beat.

**Decided: absolute, not a tie-breaker.** The choice is between putting all
in-scope work above all out-of-scope work, and preferring in-scope work only
within a band, the way the feature-underway preference already works. The
band-first precedent argues for the tie-breaker, but `PL-20ZR` settles it: the
priority field cannot express the phase, because `docket check` pins
`safety`/`science` items to P1 and the top band is therefore product work by
construction. A tie-breaker inside a band inherits exactly that limitation and
would change nothing in the case this item exists for. `P0` stays above
everything, unchanged - a hotfix outranks the phase.

**Done when.** `docket next`'s first suggestion is work the current step
includes whenever such work is ready, out-of-scope items remain visible and
marked rather than hidden, and a test covers the case where the only ready
work is out of scope - which must still be offered, with its marking.
