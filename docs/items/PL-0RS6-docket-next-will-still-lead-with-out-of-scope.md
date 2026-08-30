---
id: PL-0RS6
title: docket next will still lead with out-of-scope work after PL-1TPM, because marking does not reorder
status: untriaged
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

**Worth deciding.** Whether the preference is absolute (all in-scope work above
all out-of-scope work) or a tie-breaker inside a band, the way the
feature-underway preference already works. The band-first precedent argues for
the tie-breaker; the fact that the current phase is deliberately *not* the top
band argues for absolute. `PL-20ZR`'s finding is the relevant one: the priority
field cannot express the phase, so a tie-breaker inside a band cannot either.

**Done when.** `docket next`'s first suggestion is work the current step
includes whenever such work is ready, out-of-scope items remain visible and
marked rather than hidden, and a test covers the case where the only ready
work is out of scope - which must still be offered, with its marking.
