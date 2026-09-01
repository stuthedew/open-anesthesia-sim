---
id: PL-HDY6
title: The scope reader counts any id a milestone section names, so docket next marks an id the section names to exclude as in scope
priority: P2
effort: S
status: ready
classes: defect, infra
feature: planning-cadence
touches: subprojects/docket/src/docket/roadmap.py, subprojects/docket/src/docket/plan.py, subprojects/docket/tests/test_roadmap.py, subprojects/docket/tests/test_plan.py
added: 2026-09-01
verify: uv run pytest subprojects/docket/tests/test_roadmap.py subprojects/docket/tests/test_plan.py -k exclusion
---

**Problem.** `Scope.placement` calls an item `in-scope` when the current
milestone's section names its id anywhere between that heading and the next
one (`_section_ids` in `roadmap.py`). Naming is the whole test, so a section
that names an id in order to say it is *not* an entry marks it as one.

There is exactly one such id today, and it is the worst possible case because
the exclusion is written out at length. `ROADMAP.md`'s v0.2.8 section says:

> `PL-68XK` (check that a recorded commit hash resolves) is a different case
> and is *not* admitted by this rule: it predates the freeze and was excluded
> from the approved list deliberately.

`bin/docket next` on `origin/main` at 7ee92ea answers:

    2. P2 PL-68XK Check that a recorded commit hash resolves, now that it is
       the optional half of provenance (S, ready)
      In scope for v0.2.8 — the workflow works, the step the project is on.

So the ranking places it second, above three genuine entries, with a reason
that states the opposite of the paragraph it was read from. Measured the same
day: the section names 39 ids and records 36 entries; the three extra are
`PL-68XK` and the two closed items the section names to say they are *not*
entries either (`PL-J3ZK`, `PL-20ZR`).

**Why it matters.** The reason string is the part a session acts on. A session
asking what to work on is told this item clears the current gate, starts it
believing the beat is served, and the gate does not move - which is the same
failure `PL-1TPM` and `PL-0RS6` closed from the other direction, where
out-of-scope work led the list unmarked. It also compounds with the way this
project records exclusions: the v0.2.8 section explains four of them in prose,
so the more carefully a decision is written down, the more ids the reader
mis-places.

**Where.** `subprojects/docket/src/docket/roadmap.py` - `_section_ids` and
`Scope.placement`; the reason strings in `plan.py` around line 240.

**Approach, and the trap in it.** Preferring the gate subsection's entries over
the section's prose is the obvious fix and is wrong on its own: v0.4.0 names
nine open ids as its *own* Required scope rather than as gate entries, and
those are genuinely in that milestone's scope. Measured 2026-09-01: v0.4.0
names 30 ids and records 21 gate entries, and the nine-id difference is real
scope, not prose. So the rule has to admit both a gate entry and a
Required-scope id while rejecting a mention, which the current parse cannot
tell apart.

Two candidates, neither free. Read only the section's *list* structures - gate
entries and the Required-scope bullets - and ignore ids in paragraphs, which
is decidable but silently drops any scope recorded as prose. Or keep the
current reading and let a section mark an exclusion explicitly, which is a
convention a writer has to remember and `doc_check` would have to hold.

**Done when.** An id a milestone section names only to exclude it is not
reported `in-scope`, an id named as a gate entry or as Required scope still
is, and a test covers `PL-68XK`'s paragraph specifically.

**Admitted to v0.2.8's frozen list, 2026-09-01, under the scope test,** at the
project owner's agreement, on the same reading as the four admitted earlier
that day. It is a defect in the queue's ranking - one of the six pieces of
machinery the release's goal names - and unlike those four it is misdirecting
`docket next` on `main` right now rather than costing a correction later.
