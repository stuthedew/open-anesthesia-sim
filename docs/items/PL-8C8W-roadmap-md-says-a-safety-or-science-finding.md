---
id: PL-8C8W
title: ROADMAP.md says a safety or science finding cannot be deferred, while its deferral section lets a frozen safety or science entry be deferred when its hazard is not live, as PL-WZVZ was
status: untriaged
feature: roadmap-structure
touches: ROADMAP.md, tools/doc_check.py
added: 2026-11-07
---

**Problem.** `ROADMAP.md` says in one place that a `safety` or `science` item can
never be deferred, and in another that a frozen one can be.

§ "Which findings re-enter the gate":

> Two further exceptions re-enter the current gate regardless of presence:
> anything at `P0`, and anything classed `safety` or `science`. This project's
> own standard does not allow those to be deferred.

§ "Deferring to the next gate":

> A `safety`- or `science`-classed entry may take this route only when its
> deferral also records that its hazard is **not live**.

v0.7.0, on `PL-J5GC`: "It was first given `deferred-from:`, which a `safety`
item cannot take." `tools/doc_check.py`'s re-entry advisory agrees with the first
reading and refuses a `deferred-from:` on such an item. `PL-WZVZ`, the one frozen
`safety` entry deferred so far, is also classed `anticipated`, so § "What counts"
already exempts it by its own carve-out.

**Found by** `PL-P0C5` (slice 2 of the roadmap restructure), 2026-11-07. The
restructure moved the "not live" sentence into the new deferral section, beside
the rule it appears to contradict.

**Why it matters.** A session holding a frozen `safety` entry whose hazard is not
live cannot tell from the roadmap whether deferring it is allowed. The check says
no, unless the item is `anticipated`.

**Done when.** `ROADMAP.md` states once whether, and when, a `safety` or
`science` item may be deferred. The snapshot section, the deferral section, the
v0.7.0 `PL-J5GC` paragraph and `tools/doc_check.py` all agree with it.

**Recommendation (this session's, not yet put to the project owner).** Treat the
deferral section's "not live" route as the `anticipated` carve-out seen from the
frozen list, since a hazard that is not live is what `anticipated` records. Then
replace that sentence with a pointer to § "What counts", and leave the snapshot
section's refusal as the rule.

**Generator check.** The cause is a rule stated in more than one place, with
the copies drifting apart. That is the cause the `roadmap-structure` feature
removes, so the feature is the fix and no new generator head is recorded.
