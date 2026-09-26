---
id: PL-1BS2
title: The session-start digest's Releasable line reads readiness without the interrupted-cut resume, so during an unfinished cut it reports the short remainder with nothing saying why
priority: P2
effort: S
status: done
classes: defect, infra
feature: release-process
touches: subprojects/docket/src/docket/cli.py, subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py
added: 2026-09-13
closed: 2026-09-25
pr: 1032
verify: grep -rq 'def test_the_digest_names_an_interrupted_cut_behind_the_releasable_line' subprojects/docket/tests/ && uv run pytest subprojects/docket/tests/test_cli.py -q
---

**Problem.** The session-start digest's Releasable line reads readiness without the interrupted-cut resume, so during an unfinished cut it reports the short remainder with nothing saying why

**Why it matters, and why the missing argument is not the bug.**
`release.py`'s `readiness()` takes `resuming` and its docstring says only
`cmd_release` supplies it, deliberately: "every other caller is asking what is
shippable *now*, and an interrupted cut's stamps are not that question." That
contract is right, and a session that starts here by threading `resuming` into
the digest has fixed the wrong half. The defect is the second half of the
title - the line reports the remainder with nothing saying why.

During an unfinished cut the already-stamped items drop out of `shippable`, so
`Releasable: N finished item(s) since <version>` counts only what the stopped
run never reached. The number is wrong in the direction that hides work rather
than inventing it, which is the harder direction to notice: a twenty-item cut
interrupted after fifteen reads as five, and every session opened in the
meantime sees a small, ordinary-looking release offer. `PL-1MKQ` is the same
state seen from `bin/docket check`, which does report it. The digest is what a
session reads *first*, and it is the one reading that stays silent.

**Done when.** The digest's `Releasable:` line names an interrupted cut where
one is open - the version being resumed, and that its notes were never written
- instead of presenting the remainder as an ordinary offer, with
`readiness()`'s contract left as it is. `bin/docket status` answers the same
way, and a test covers a store holding items stamped for a version whose notes
file is absent.

**Worked.** `readiness()` is untouched: `cli._interrupted` reads
`unrecorded_milestones` beside it for the digest and `status`, taking the
newest as `cmd_release`'s resume does, at the cost of reading `docs/releases/`
once (68 notes files, 2.9 ms measured). One sentence,
`render._interrupted_cut`, serves both the digest's `Releasable:` line and
`status`'s `Unreleased:` line, so the two say the same words. It counts the
stamped items from the store and gives the total the resume would ship, stamped
plus remainder.

Also decided here: the sentence replaces the whole offer, including the
"already being cut on" advice, since the unfinished cut in this checkout is
what to finish first; and it prints whether or not the remainder is worth
cutting, so a cut that stamped everything, which printed no line at all, is
named too. `_cuts`'s walk still runs under its `is_worth_cutting` gate where
the sentence replaces the offer, unused; narrowing that gate was left alone
rather than widened into this item. Tests, in
`subprojects/docket/tests/test_cli.py`: the digest and `status` over a cut
stopped inside its stamp loop (six items, two stamped, through a new
`_cut_stopped_after` helper built on `_interruptible_repo` and
`_interrupt_after`), and the digest over one stopped after its bump, with
nothing left unstamped.
