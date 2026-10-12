---
id: PL-0HLS
title: PL-TZ7T's mechanism is producing again: four captures filed since it closed on 2026-09-20 fell through gaps in its one key, a shared declared touches path - stale touches after a file move (PL-6SV4), a clean-tree capture (PL-9VPH), the store directory counted as a shared path (PL-SV0D), an untriaged candidate declaring none (PL-TS7L)
priority: P1
effort: M
status: done
classes: defect
feature: recurrence-signal
touches: subprojects/docket/src/docket/duplicates.py, subprojects/docket/tests/test_duplicates.py, .claude/skills/docket/modes/capture.md, subprojects/docket/src/docket/store.py, subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/README.md, subprojects/docket/tests/test_cli.py
deferred-from: v0.6.0 - captured after the freeze (e6cdfd93, 2026-09-21), and not safety or science; recorded as a generator head by PL-4097, 2026-10-12
added: 2026-10-12
closed: 2026-10-12
pr: 1463
payoff: a capture made before triage is shown the open item that already describes it, so a defect is diagnosed once rather than twice, and three open defects in the duplicate search close in one design instead of three patches that undo each other
verify: grep -q 'def test_an_untriaged_capture_meets_an_untriaged_item' subprojects/docket/tests/test_duplicates.py
root-cause-of: PL-6SV4, PL-9VPH, PL-SV0D, PL-TS7L
generator: spent - the key reads every subject a capture and an open item in one checkout can both name, a path outside the store, an item's file or the feature, and records only on a path or an item, so what it misses now is a sibling branch's capture or a paraphrase sharing no subject, which no key reads; the bound in the brief names what reopens it
misread: Whether an open item already describes the mechanism a new capture names
reenters: PL-TZ7T
---

**Problem.** PL-TZ7T's mechanism is producing again: four captures filed since it closed on 2026-09-20 fell through gaps in its one key, a shared declared touches path - stale touches after a file move (PL-6SV4), a clean-tree capture (PL-9VPH), the store directory counted as a shared path (PL-SV0D), an untriaged candidate declaring none (PL-TS7L)

**Why it is one mechanism.** `PL-TZ7T` closed on 2026-09-20 with one key for
whether an open item already describes a capture: a shared declared `touches`
path selects, title similarity orders, and a capture declaring none takes its
paths from the working tree (`PL-THLT`). `subprojects/docket/src/docket/duplicates.py`
has not changed since (`git log`, newest `a4cc4b09`, 2026-09-20). Each member
is a place that key is absent or wrong, and each one's **Generator check.**
names `PL-TZ7T`'s fact:

- `PL-6SV4` (2026-09-22, dropped as a duplicate of `PL-VYK1`): the older item's
  `touches` still named the file its section lived in before a move.
- `PL-9VPH` (2026-09-23): a capture made on a clean tree, which `capture.md`'s
  housekeeping recipe prescribes, has no paths, so the search never runs.
- `PL-SV0D` (2026-10-01): the store directory, which every capturing branch
  changes, counts as a shared path, and recorded `PL-DHGC` as a recurrence of
  `PL-JLBD`.
- `PL-TS7L` (2026-10-03): an open item declaring no `touches` is never a
  candidate, and capture leaves `touches` unset until triage, so same-day
  duplicates (`PL-YZ17`, `PL-5F76`) never meet.

Each filing counted at most two post-close instances, one short of the three
that read as a fix that did not hold, because each found only the instances its
own path or title led to. `PL-4097` read all four from their `reenters:`
records on 2026-10-12.

**Why it matters.** A missed duplicate costs a second brief and a triage pass
to drop or split it. 16 items filed from 2026-09-21 to 2026-10-05 were dropped
as duplicates (a grep of dropped items' `reason:` for "duplicate", 2026-10-12),
some caught by the search itself and at least four filed on a sibling branch
before either merged (`PL-9RJM`, `PL-H2V3`, `PL-XQY6`, `PL-P813`). And the
members' fixes conflict if taken one at a time: `PL-9VPH`'s makes a housekeeping
capture match on `docs/items`, the one path `PL-SV0D` asks the matcher to stop
counting. So one design has to decide what the store directory is worth as a
key, and what selects where either side has no path.

**Done when.** One key design in `duplicates.py`, measured against
`PL-TZ7T`'s 13 known pairs before it is chosen, pairs each member's instance -
`PL-YZ17` with `PL-5F76` (both untriaged, no `touches`), `PL-4CPP` with
`PL-BYN2` (a clean-tree capture), `PL-6SV4` with `PL-VYK1` (stale `touches`) -
and records no recurrence where the only shared path is the store directory
(`PL-DHGC`, `PL-JLBD`), each pinned by a test in
`subprojects/docket/tests/test_duplicates.py`, the untriaged pair's as
`test_an_untriaged_capture_meets_an_untriaged_item`. The open members close
with it. The head closes `spent` with a written bound for what no key can
see - a capture on a sibling branch before either merges, a paraphrase sharing
no path - naming what reopens it, as `PL-61FT`'s bound does, so its next miss
is an item at its own rank rather than another head.

**Generator check.** A head: `PL-TZ7T`'s fact, whether an open item already
describes the mechanism a new capture names, re-entered by the four filings
above after that head closed. Recorded by `PL-4097`'s design round.

**Built 2026-10-12, in `#1463`.** One key in
`subprojects/docket/src/docket/duplicates.py`, and the open members close with
it. A subject both declarations name selects, and the title still only orders
what a subject selected. A subject is one of three things:

- a path outside the store, declared or read off the working tree;
- one item's file, compared by its id through `store.declared_item_file`,
  which moved there from `checks` so the two readers share one. A capture names
  an item by its file in the working tree or by the item's id in its title,
  and the title's ids are matched only to the item files candidates declare;
- the feature, which a capture carries before triage writes `touches`, and
  which survives a file move.

The store directory is none of them. Open items declaring no `touches` are
candidates. A filing is recorded as a recurrence on a shared path or item and
never on the feature alone, since two items one feature groups were grouped on
purpose. `bin/docket new` passes the capture's `--feature` and the store as its
invocation resolved it, and prints what each candidate shares.

**Measured before it was chosen**, through docket's own parser, with each
capture's fields as it was filed:

| measure | path-only key | this key |
| --- | --- | --- |
| `PL-TZ7T`'s 13 known pairs at `4c282700^`, in the top three either way round | 7 | 7 |
| the three missed instances, each against the store its later filing met | 0 | 3 |
| `PL-DHGC` recorded on `PL-JLBD` | yes | no |
| open items at `22a0b364` shown a candidate, probed with their own fields | 40 of 304 (13%) | 57 of 304 (19%) |

Two variants were measured and refused. Reading ids from both titles is
`PL-85NT`'s refuted referent key: at `22a0b364` it showed a candidate for 47
probes against the path-only 40, and for 16 titles probed with nothing else to
search on, where reading the capture's title alone adds none to the 40 and
shows none of the 16. Recording on the feature
was refused on the 18 probes the feature alone gave a candidate: every one a
sibling its feature was written to group - one prose cut across `src/` and
`tests/`, a check beside its instances, two readers of one fact - and none a
second filing.

**Recurrences.** Of the 152 entries at `a90dd746`, 70 withdrawn, 127 replay
against the store their capture met, and the store directory alone had
selected six of those, besides `PL-DHGC`'s. This key records none of the two
withdrawn as wrong (`PL-02C4` on `PL-04KR`, `PL-DHGC` on `PL-JLBD`), and shows
four on their shared feature without recording them: consecutive release tags
(`PL-08D4` on `PL-LRP2`, `PL-HZWB` on `PL-08D4`), a census and its mechanism
sweep (`PL-1BGP` on `PL-PLSJ`), and two container repairs (`PL-7TH9` on
`PL-QKXZ`). `PL-P3GV` it still records on a path, onto `PL-R808`, which shares
three of its paths and outranks `PL-LF2C`.

**Every duplicate dropped since the path-only key shipped.** 27 items dropped
as duplicates closed from 2026-09-20 to `22a0b364`. Replayed with the later
filing's fields as added and its commit's changed files standing in for its
working tree, 23 met an open partner in their own store: the path-only key
shows 11 of them and this key 12, `PL-6SV4`'s pair the twelfth. Of the 11
neither shows, 8 share no subject with their partner, and 3 share one with
titles below `DISPLAY_FLOOR` - `PL-3JP0`/`PL-6580` at 0.05, `PL-R77L`/`PL-GXPP`
at 0.11, `PL-TZ7T`/`PL-TH7P` at 0.12 - all three filed before 2026-09-20. Of
the other 4, one branch filed both of one pair, and three met a partner already
closed.

**The bound, and what reopens it** (2026-10-12, as `PL-61FT`'s is):

- **What the search promises.** A capture is shown an open item in its own
  checkout's store that shares a subject with it - a path outside the store,
  an item's file, the feature - and whose title clears `DISPLAY_FLOOR`, among
  the first `LIMIT`; and a filing is recorded as a recurrence on a shared path
  or item only. A pair inside that promise that was not shown is a defect in
  `duplicates.py`, filed and worked at its own rank.
- **What no key can see.** A capture on a sibling branch before either merges:
  the search reads the store this checkout holds, and the other filing reaches
  it only through a merge (`PL-9RJM`, `PL-H2V3`, `PL-XQY6`, `PL-P813`). And a
  paraphrase sharing no subject: two titles of one problem with no path outside
  the store, no item and no feature in common, where title words alone are the
  refuted key (`PL-TZ7T`, `PL-85NT`) - 8 of the 23 replayed above. A duplicate
  dropped for either is not a member of this head, and its `reason:` cites
  this bound.
- **What it chose not to see.** A pair sharing a subject whose titles fall at
  or below the floor, and a filing whose partner is already closed: the floor
  and the open-items rule are what keep the recurring-by-design titles off
  every capture. Their cost is measured above - 3 below the floor, none filed
  since 2026-09-20, and 3 closed partners.
- **What reopens it.** Three duplicates within a quarter that shared a subject
  with an open item in their own store and were not shown, whether inside the
  promise or below the floor, which would say the subjects or the floor are
  drawn too tight. The replay above finds none filed since 2026-09-20. A
  sibling-branch or no-subject miss never counts toward it, since no key reads
  one.
- **The members.** `PL-9VPH`, `PL-SV0D` and `PL-TS7L` close with this pull
  request, each pinned by a test in `subprojects/docket/tests/test_duplicates.py`.
  `PL-6SV4` stays dropped as `PL-VYK1`'s duplicate; its pair is pinned by
  `test_a_shared_feature_survives_a_file_move`.
