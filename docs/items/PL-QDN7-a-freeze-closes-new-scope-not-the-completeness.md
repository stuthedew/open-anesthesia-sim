---
id: PL-QDN7
title: A freeze closes new scope, not the completeness of a fix, and the finishing item is paired
priority: P2
effort: S
status: ready
classes: docs, infra
feature: planning-cadence
touches: ROADMAP.md, CLAUDE.md
added: 2026-08-30
verify: python3 tools/doc_check.py check && bin/docket wave
---

**Problem.** `ROADMAP.md`'s v0.2.8 section said "Nothing is added to this
list", and read the freeze as closing the list to everything discovered after
it. That is not what a freeze is for, and it contradicted "The gate is a
snapshot, not a moving target" in the same file, which already says a finding
that continues or completes an item inside the frozen list belongs to the same
list.

The project owner stated the intent on 2026-08-30: a freeze closes new
*behavior and features*, not the completeness of a fix. If a newly discovered
item is needed to properly fix something already on the list, it comes in.

**Why it matters.** The wrong reading was about to be acted on. `PL-XCYB` (a
provenance check must refuse to answer in a shallow checkout) was captured,
excluded from v0.2.8 by that paragraph, and the session handed `PL-ZQ9C` was
told to build around it - which would have shipped `PL-ZQ9C`'s provenance check
knowing it reports sound provenance as broken in the checkout most sessions
run in. Keeping the list at seventeen would have preserved its length at the
cost of its purpose.

**Where.** `ROADMAP.md`: the v0.2.8 section's freeze paragraph and the opening
of "The gate is a snapshot, not a moving target"; `CLAUDE.md`'s queue rules.

**Worked.** Both edited in the session that raised it. The v0.2.8 paragraph now
states what the freeze closes (new scope) and what it does not (what an entry
already on the list needs in order to be done), records that its previous
wording was wrong, and names `PL-XCYB` as the one entry admitted under the
rule - with `PL-68XK` named as the case the rule does *not* admit, since it
predates the freeze and is a separate capability. "The gate is a snapshot" now
opens by stating the intent plainly, so a session reads it before the mechanics.

The owner added a second half the same day: an entry admitted this way is
worked *with* the entry it completes, not after it. Splitting them reintroduces
what admitting the finding prevented - the first ships half-fixed while the
thing that finishes it waits in the queue. Recorded in the same two passages,
and as a bullet in `CLAUDE.md`'s queue rules, since that is what a session reads
before it reaches the roadmap.

`bin/docket wave` reports 18 entries of 18.

**Done when.** Met: a session reading either passage gets the intent before the
mechanics, the two passages agree, and the pairing half is stated where a
session reads it before the roadmap.
