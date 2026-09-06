---
id: PL-0M32
title: PL-HB58's work merged in #408 but the item is still ready, and its verify names a test the implementation renamed
priority: P2
effort: S
status: needs-decision
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/src/docket/verify.py, subprojects/docket/tests/test_checks.py
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

**Why it matters.** An item that reads open while its work sits on the default
branch is counted by `bin/docket gate`, offered by `bin/docket next`, and left
out of the release that actually shipped it - the queue misdescribes the
project in three places at once, and the next session can start work that is
already done. The renamed test is what makes that state indistinguishable from
an unstarted item from every direction the tooling can see, which is why the
two faults are one item.

**Since filed, and checked rather than recalled.**
`origin/claude/pl-hb58-close-out` sets
`PL-HB58` to `done` and rewrites its `verify:` to
`test_five_minute_elimination_ratio_against_published_human_measurement`, the
test that exists. So the first fault is answered on that branch and this item
is left with the second: whether anything can tell "finished under a renamed
test" from "not started". That branch merged as `#412` while this triage pass
was running, so the first fault is closed on `origin/main` and needs nothing
further here.

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

**Decision needed.** Should anything be able to tell "finished under a renamed
test" from "not started"? The two are indistinguishable by construction - an
open item's `verify:` is supposed to fail - and `docket check --verify` reports
only the inverse case, a command that passes unexpectedly. Three candidates:
record in the store's documentation that the case is undecidable and rely on
the close-out reading the command; have `docket check` flag an open item whose
`verify:` greps for a symbol no file in the tree defines, which is decidable
and would have caught exactly this; or nothing. The closure half of this item
is already answered on `origin/claude/pl-hb58-close-out`, so this question is
the whole of what is left.
