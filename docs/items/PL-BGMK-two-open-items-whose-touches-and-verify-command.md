---
id: PL-BGMK
title: Two open items whose touches and verify: command overlap are never compared, so PL-1YDK and PL-8PT6 were filed and worked as one finding twice and only docket check --verify on main caught it
priority: P2
effort: M
status: done
classes: defect, infra
feature: open-item-overlap-detection
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py, subprojects/docket/src/docket/config.py, docket.toml, subprojects/docket/README.md, docs/items/PL-5GBV-two-items-were-filed-three-days-apart-for-one.md
added: 2026-09-13
closed: 2026-09-30
pr: 1232
verify: grep -q 'def test_a_discriminating_clause_shared_behind_a_health_clause_is_rejected' subprojects/docket/tests/test_checks.py
falsifies: record the same `verify:` command
---

**Problem.** Two open items whose touches and verify: command overlap are never compared, so PL-1YDK and PL-8PT6 were filed and worked as one finding twice and only docket check --verify on main caught it

**Why it matters.** `PL-1YDK` and `PL-8PT6` were filed separately, triaged
separately and worked separately on one finding. Nothing in the store compared
them, and what eventually noticed was `bin/docket check --verify` on `main` -
after both had merged, which is the most expensive moment available. Two
sessions had already been spent, and the merge that reddened `main` is what
made it visible at all.

The store holds the evidence that would have caught it. `touches` is declared
on almost every open item and `concurrency.py` already builds a graph from it;
`verify:` is a command string, and two items proposing the same command are
proposing the same work by definition. Neither is read for this, so the only
thing standing between the queue and a duplicate is whether one session happens
to recognise another session's title.

**Decision needed.** Whether an overlap signal can be made specific enough to
be worth having, and what it fires on. `touches` alone is far too broad - Gate
1's science half all declares `docs/MODEL.md`, so a pairwise comparison would
report dozens of pairs on every run, and `CLAUDE.md` retires a check that fires
every run without changing a decision. The narrow reading is `verify:`: two
open items whose commands are equal, or whose `grep` halves name the same test,
are near-certainly one finding, and that is rare enough to be an error rather
than an advisory. Whether `touches` adds anything on top of it - as a second
condition rather than a first - is the part to measure before building.

Name the number first, per `.claude/rules/expert-review.md`: count how many
open pairs each candidate rule reports against this store today, and what
fraction of them are real duplicates. A rule reporting more than a handful has
failed regardless of how sound it looks.

**Done when.** The question is answered against that count, and either a check
lands carrying the rule that survived it, or the item closes recording that no
rule was specific enough and what the count was.

**Grouped as `feature: open-item-overlap-detection`** (`PL-JKML`'s duplicate
sweep, 2026-09-20, confirmed on independent refutation). `PL-5GBV` and
`PL-BGMK` are two halves of one problem: nothing in this project ever compares
**two items that are already open**. `PL-5GBV` is what that costs downstream -
two items for one defect both reaching `ready` and both entering the frozen
v0.5.0 gate, so the gate counted the same work twice - and `PL-BGMK` is the
comparison that would have caught it, over overlapping `touches` and `verify:`.
Fixing either alone leaves the other standing: a comparison nobody runs at gate
freeze does not stop double-counting, and a gate that de-duplicates does not
stop two sessions working one finding.

**Deliberately not named for the filing-time warning.** `PL-TZ7T` and
`PL-X5JR` cover a *new capture* checked against the store as it is filed. This
group is the other direction - two items already in the store, neither of them
new - which nothing in the recurrence-signal design reaches.

**Re-confirmed 2026-09-30: changed shape.** The narrow reading above - two
open items whose commands are equal - had already landed as
`_check_shared_verify` in `#882` (`PL-J3WK`, `PL-PBP5`), keyed on the whole
`verify:` string. It would not have caught this item's own pair: `PL-1YDK`
recorded `git check-ignore -q subprojects/docket/uv.lock` and `PL-8PT6` the
same clause behind `python3 tools/doc_check.py check`. So the question left
was which key, and the count below answers it.

**Measured 2026-09-30.** Over the 308 open items (47,278 pairs, 198 with a
`verify:`, 304 with `touches`), and for recall over the 21 duplicate pairs the
store records - `PL-TZ7T`'s clusters, `PL-JKML`'s settled rows, `PL-5GBV`'s
pair and this item's - with each item's fields as they stand now:

| rule | open pairs reported today | recorded pairs caught (of 21) |
| --- | --- | --- |
| exact `verify:` string (the check as landed) | 0 | 1 |
| shared clause, health clauses left out | 0 | 2 |
| shared clause, health clauses counted | 497 | 2 |
| same test named by the `grep` half | 0 | 0 |
| same `grep` pattern | 0 | 1 |
| shared `touches` path, identical / covering | 2,863 / 5,140 | 15 |
| shared `touches` and title over `DISPLAY_FLOOR` (the filing-time key) | 31 | 12 |

The 497 pairs share exactly four clauses, every one a health check:
`python3 tools/doc_check.py check` (31 open items), `uv run pytest
tests/unit/test_doc_check.py` (7), `bin/docket check` (5) and a whole-file run
of `test_checks.py` (2). Over the 62 live `recurrences:` pairs the same shape
holds: every `verify:`-keyed rule catches 0, shared `touches` 50, `touches`
with title 46. And 5 of the 21 recorded pairs carry no `verify:` on one side,
because a dropped duplicate usually never reached triage - a structural
ceiling on any key read from that field.

**Decided, by this session, as an apparatus-internal choice.** The
shared-clause key is built: `_check_shared_verify` now keys on each command's
discriminating clauses, with the health half spelled in a new `health_clauses`
setting beside `collected_test_paths` and the selector-less pytest runs those
trees cover left out by the reading `_redundant_pytest_clause` already gives.
It reports 0 pairs on this store today and catches the founding pair, as a
hard error, so it never fires without changing a decision. Refused on the
count: the `grep`-half test-name key (0 of 21); `touches` as a second
condition on the clause key (both clause catches already share a path, so it
filters nothing and could only lose); any `touches`-first rule (thousands);
and the filing-time key run store-wide as a check - 31 pairs every run, all
already read by `PL-JKML`'s sweep of 400, which confirmed 5. That key is a
sweep to repeat by hand when the queue has grown, not a check, and
`bin/docket new` already runs it at the moment the second item arrives.
`PL-D188`/`PL-JL2M`, `PL-5GBV`'s pair, shares neither a path nor a clause, so
no key over fields reaches it; that half of the feature stays with `PL-5GBV`.
