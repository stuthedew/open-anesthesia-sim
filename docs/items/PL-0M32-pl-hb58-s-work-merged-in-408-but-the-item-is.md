---
id: PL-0M32
title: PL-HB58's work merged in #408 but the item is still ready, and its verify names a test the implementation renamed
status: untriaged
added: 2026-09-06
---

**Problem.** Two separate faults, found together while cutting v0.4.6 and
worth one item because the second is why the first was not caught.

**The closure did not land with the work.** `#408` merged as `d92ba79`,
subject `PL-HB58: validate washout against the same published cohorts the
wash-in gate uses`, and the work is on `main`:
`tests/reference/test_published_wash_in.py` gained six elimination tests and
the whole file passes. `docs/items/PL-HB58-...md` on `main` still reads
`status: ready`. So `main` holds the work while the queue calls the item open -
the failure `PL-D2GW` and `PL-P5S0` recorded, which closing in the same commit
as the work exists to prevent.

**Its `verify:` command can never pass.** The item specifies
`grep -q 'def test_five_minute_elimination_ratio_matches_published_human_measurement'`.
The test that shipped is
`test_five_minute_elimination_ratio_against_published_human_measurement` -
`matches` became `against`. Nothing else differs, and the work is plainly the
work the item asked for.

**Why the second hides the first.** A `ready` item's `verify:` is *supposed* to
fail; that is the whole point of writing it before the work. So a command
failing on an open item is indistinguishable from a command that has been
invalidated by the work itself, and `bin/docket check --verify` reports the
opposite case - commands that pass unexpectedly - because that is the one it
can decide. An item finished under a renamed test therefore looks exactly like
an item nobody has started, from every direction the tooling can see.

**Consequence for the release.** v0.4.6 was cut with `PL-HB58` correctly
excluded, since it is `ready`. If the closure lands after the tag, the item
ships in v0.4.7 while its code shipped in v0.4.6 - a release whose notes do not
describe its own contents.

**Where.**

- `docs/items/PL-HB58-validate-washout-against-the-same-published.md` - the
  status, and the one word in its `verify:`.
- `subprojects/docket/` - whether anything can decide this case at all.

**This is another session's item.** It was left open rather than closed here:
the session that merged `#408` was idle with the merge outstanding, and closing
somebody else's item from outside is a second resolution of the same file.

**Done when.** `PL-HB58` is closed with a `verify:` naming the test that
exists, by whoever owns it; and either a check can tell "finished under a
different name" from "not started", or it is recorded that it cannot and why.

**The instance closed on 2026-09-06, hours after this was filed; the general
question is what remains.** `#412` closed `PL-HB58` and, in the same change,
repointed its `verify:` at the test that actually shipped -
`test_five_minute_elimination_ratio_against_published_human_measurement`, not
the `..._matches_...` this item found it naming. Checked on `main` at
`029073d`: the item reads `status: done` and the grep half of its command
resolves. So the two faults recorded above are both fixed, and neither needs
doing again.

**What is left is the reason they were invisible**, which no fix has touched. A
`ready` item's `verify:` is *supposed* to fail, so a command that fails because
the work has not started and a command that fails because the work landed under
a different name are the same observation. `bin/docket check --verify` reports
the opposite case - commands that pass unexpectedly - because that one is
decidable. This item is therefore now a **question about whether the case can
be decided at all**, not a defect report with a known fix, and it should be
retitled when triaged.

One shape worth testing: a `verify:` whose `grep` half fails while its test-run
half passes is a weak signal of exactly this state, since it means the suite is
healthy and only the named artefact is missing. That is not conclusive - it is
also what an unstarted item looks like when its file already exists - so
whether it is worth an advisory, or whether this is a case the tooling should
decline, is the judgment to make. Dropping it with that reasoning recorded is a
legitimate outcome.
