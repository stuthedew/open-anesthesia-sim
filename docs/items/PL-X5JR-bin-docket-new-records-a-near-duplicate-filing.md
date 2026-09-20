---
id: PL-X5JR
title: bin/docket new records a near-duplicate filing onto the open item it matched, and an item carrying three or more recurrences is surfaced as a generator-tier promotion candidate rather than promoted by the heuristic itself
priority: P2
effort: M
status: ready
classes: infra
feature: recurrence-signal
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/model.py, subprojects/docket/src/docket/plan.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests, subprojects/docket/README.md
blocked-by: PL-TZ7T
added: 2026-09-20
payoff: turns a cost the store already pays - one defect diagnosed five times - into the evidence that ranks it, without a session having to notice and assert the claim by hand
verify: grep -q 'def test_a_third_recurrence_surfaces_a_promotion_candidate' subprojects/docket/tests/test_plan.py
---

**Problem.** `bin/docket new` records a near-duplicate filing onto the open item
it matched, and an item carrying three or more recurrences is surfaced as a
generator-tier promotion candidate rather than promoted by the heuristic itself.

**Decision (project owner, 2026-09-20, ratified**, over the mechanism they first
described - counting repeat filings and raising the item's `priority:`.) The
count feeds the **generator tier** rather than the band, and it surfaces a
promotion candidate rather than promoting one.

**Why it matters.** A re-filing is not only waste. It is evidence that the
defect *fired again* - a session hit it, had no idea an item existed, and paid
the diagnosis a second time. `CLAUDE.md`'s generator rule already ranks on
exactly that property: "every session it stands through pays it again." What is
missing is that the evidence has to be **asserted** by a session that happens to
notice. That is precisely what failed on the suppression-check cluster:
`PL-STC4`'s brief documents the duplication three separate times in its own
prose - naming `PL-BHBZ`, then `PL-4FD2`, then `PL-TZ7T` as the mechanism - and
nothing was promoted until 2026-09-20, when a session read the cluster by hand.
Five captures of one defect, and the store held every fact needed to rank it.

**Why `priority:` cannot carry it, which is the half the first sketch got
wrong.** `docket check` pins `P1` to `safety` and `science`, and `CLAUDE.md`
forbids promoting process work into that band to move it up the order. The
2026-09-19 check-sequencing decision in `docs/WORKING_NOTES.md` hit this wall
directly and had to move three items by *sequencing* instead, changing no
priority. So an automatic priority bump is unavailable to any workflow defect -
which is every item this counter would ever fire on. The generator tier is the
lever that exists, it sits above every band but `P0`, and it already means the
thing a recurrence count measures.

**Why it surfaces rather than promotes.** `subprojects/docket/README.md` calls
`root-cause-of:` "the one place in the store where a typo would buy a
promotion", which is why `docket check` holds every id in it to naming a real
item and holds the list to three. Letting a title-similarity heuristic write
that field, or rank as though it had, reintroduces exactly the hazard the
validation exists to close - on a match that is a judgment about prose. So the
count is recorded as fact, and a reader decides. A session confirming the
cluster writes `root-cause-of:` the way it does today; the counter's job is to
make sure the cluster is *seen*.

**Shape.**

- A `recurrences:` list field on an item, each entry a date and the id of the
  capture that matched it - so the claim stays auditable and a later session can
  read both briefs rather than trust a score.
- `bin/docket new` writes the entry onto the matched open item when it warns,
  and files the new item anyway. The capture rule may not be made conditional on
  a similarity score (`PL-TZ7T`), so this never refuses.
- `docket next` and the session-start digest surface an open item at three or
  more recurrences as a promotion candidate, naming the recurring ids. Three
  keeps one threshold in the project rather than two - it is the generator
  rule's own number.
- `docket check` holds each entry to naming a real item, as it does for
  `root-cause-of:`.

**Depends on `PL-TZ7T`** for the detection half - the `touches`-narrowed,
title-ranked candidate search whose key that item's brief now records, measured.

**Done when** filing a capture that matches an open item leaves a dated,
id-bearing entry on that item, and the third such entry makes the item visible
as a promotion candidate without changing its band or writing `root-cause-of:`.
