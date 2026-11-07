---
id: PL-8C8W
title: ROADMAP.md says a safety or science finding cannot be deferred, while its deferral section lets a frozen safety or science entry be deferred when its hazard is not live, as PL-WZVZ was
priority: P2
effort: S
status: untriaged
classes: defect, docs
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

**Put to the project owner on 2026-11-07, with a different recommendation.**
The thread finishing the roadmap restructure asked, on a decision card, whether
a safety or science problem can wait for the next release when this release
shows nothing wrong. **Recommendation (that thread's): yes, when the item's
record says, checked against the code, that no learner can see a wrong value
now.** That keeps the 2026-09-21 deferral rule and the ten safety and science
items already deferred from v0.7.0, among them `PL-8W1B`. It matches
medical-device practice: IEC 62304:2006+A1:2015 § 5.8.2 and § 5.8.3 release
software with known residual anomalies once each has been evaluated as
carrying no unacceptable risk. The recommendation above, to keep the snapshot
section's refusal as the rule, would pull those ten items into v0.7.0's list,
most of them `docs/MODEL.md` traceability work.
**Answered 2026-11-07 at 22:09 UTC: yes, if recorded and checked (project
owner, 2026-11-07, ratified, over keeping the snapshot section's refusal,
which would pull the ten deferred safety and science items into v0.7.0's
list).** A safety or science item may be deferred from the current gate when
its record says, checked against the code, that no learner can see a wrong
value now. The snapshot section's sentence that makes these two classes not
deferrable changes to say so. `PL-C8N8`, the wording of the re-entry
advisory in `tools/doc_check.py`, follows from this answer.

**Applied 2026-11-07 (`PL-GW0P`'s pull request).** § "Deferring to the next
gate" states the rule, with this answer's decision tag: a `safety` or `science`
entry may be deferred when its record says, checked against the tree, that no
learner can see a wrong value now. § "Which findings re-enter the gate" keeps
`P0` not deferrable and points the two classes at that section. The v0.7.0
paragraph on `PL-J5GC` now says a `safety` item could not take `deferred-from:`
until this item. `tools/doc_check.py`'s re-entry advisory follows in `PL-C8N8`:
a deferred `safety` or `science` entry still stays written on the frozen list,
so the advisory still names one that is deferred and not listed.

Removed from `ROADMAP.md`, because the answer made them false:

> This project's own standard does not allow those to be deferred. A gate that
> let them wait would invert the reason it exists.

(§ "Which findings re-enter the gate", of `P0`, `safety` and `science`.)

> These two classes are still not offered a deferral.

(§ "What counts", after the `anticipated` carve-out's "never by a deferral",
which stays.)
