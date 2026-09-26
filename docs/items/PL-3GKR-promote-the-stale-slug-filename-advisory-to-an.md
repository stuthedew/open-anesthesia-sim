---
id: PL-3GKR
title: Promote the stale-slug filename advisory to an error now the count is zero, once PL-Y5JX's touches-coupling warning exists to make renaming safe
priority: P3
effort: S
status: ready
classes: infra
feature: slug-rename-on-write
touches: subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_checks.py
added: 2026-09-19
verify: grep -q 'def test_a_drifted_item_filename_is_an_error' subprojects/docket/tests/test_checks.py
---

**Problem.** Promote the stale-slug filename advisory to an error now the count is zero, once PL-Y5JX's touches-coupling warning exists to make renaming safe

**Where it comes from.** `PL-YTDN` (the pass that renamed the drifted item
files) closed on 2026-09-19 with the drift count at zero, which is the condition
its own brief named for asking this question: "Worth asking at that point
whether the check should be promoted from an advisory to an error, which is only
safe once the count is zero."

**Why it is not simply yes.** Zero is necessary and not sufficient. A hard error
would compel a session to rename a file the moment a title edit drifts it - and
nothing yet warns that another item's `touches:` names that file by full path,
so the compelled rename is exactly the silent breakage `PL-Y5JX` exists to stop.
`PL-YTDN` hit both live instances (`PL-3V6C` and `PL-77SV`, both naming
`PL-TFWR`) and found them only by hand: the re-check one-liner it inherited
scans `verify` and the body and not `touches`, and reported no coupling at all.
Promoting the check while that hole is open converts a finding a session can
weigh into an instruction it has to obey.

**So the order is `PL-Y5JX` first**, which makes a `touches` entry naming a
missing item path an error and makes the slug advisory name any item whose
`touches` declares the file it proposes to rename. With that in place a
compelled rename is a safe rename and the promotion carries no hazard.

**The case for promoting at all.** `CLAUDE.md` treats an advisory nobody acts on
as a candidate for retirement rather than promotion, so this check has exactly
two honest futures and drifting on as unowned noise is not one of them. The
advisory fired in every session for weeks with no owner, which is what made
`PL-YTDN` necessary in the first place; at zero, an error keeps it at zero for
free, and a rename is cheap when it is one file rather than nine.

**Worth deciding as part of it:** whether the error should fire on a *closed*
item's drift as well as an open one's. `PL-YTDN` renamed closed files
deliberately - findability by `ls docs/items/ | grep` is the point of the slug,
and a closed item is what a later session looks up by name - so the default
answer is yes, but a closed item nobody will edit again is also the cheapest
possible place to allow drift.

**Why it matters.** `CLAUDE.md` gives a standing advisory exactly two honest
futures - it earns its place every run, or it is retired - and drifting on as
unowned noise is neither. This one fired in every session for weeks with
nobody acting on it, which is what made `PL-YTDN`'s nine-file rename pass
necessary in the first place. At a count of zero the choice is cheap in one
direction and only in one direction: an error keeps it at zero for free,
because a rename is one file at the moment the title is edited, whereas
letting it drift again means another campaign.

The concrete loss the check stands against is findability. An item file's name
is how a session finds an item by hand - `ls docs/items/ | grep` - and how
`bin/docket stranded` prints a recovery line somebody pastes. A file carrying
the slug of a title it no longer has sends both to the wrong place, and
`origin/main` has held one before.

**Blocker cleared, checked 2026-09-19.** This brief says "the order is
`PL-Y5JX` first". `PL-Y5JX` closed on 2026-09-19 and merged as `#714`, so the
`touches`-coupling warning it asked for exists and a compelled rename is now a
safe rename. The item is `ready` rather than `blocked`.

**Done when.** The stale-slug drift is a hard failure from `bin/docket check`
rather than an advisory, `PL-Y5JX`'s coupling warning is in place ahead of it,
and a test drives a drifted file through the failure.

**Blocked, 2026-09-26.** The promotion was written and reverted on this branch
(`b5665a6d`, on `claude/pl-fable-01-ljo8z8`): `_check_filenames` appending to
`report.errors`, its docstring and `store.py`'s rewritten to say error, the
seven `test_checks.py` tests moved from `.advisories` to `.errors`, a
`test_a_drifted_item_filename_is_an_error` and a closed-item case added, and
the two drifted files renamed. Its own tests pass. `make check` then fails 17
tests in `subprojects/docket/tests/test_cli.py` (`test_check_exits_zero_on_a_clean_store`
first): the `_store` fixture writes every document as `item-N.md`, so every
store it builds now fails `check` with "1 item file carries a slug its title no
longer generates (PL-B1B1)". Writing each document under `filename_for(parse_item(document))`
instead clears those 17 and fails 20 others, because 7 sites in that file
open the fixture's files by the positional name (`items / "item-0.md"`).

**Kept on the branch:** the two renames (`PL-843V`, `PL-8543`), both closed
items edited on no open branch, so the drift count on `origin/main` is zero
once it merges. **Recommendation:** migrate `test_cli.py` first - a fixture
that writes the natural name and returns the paths it wrote, with the 7
positional reads moved onto it - as its own commit under this id, then land the
promotion exactly as `b5665a6d` wrote it. Left at `ready` and yielded rather
than `blocked`, since nothing outside this item holds it.

**Worked.** Only the two renames stand: `PL-843V` and `PL-8543`, moved with
`git mv` to the names `docket` writes, after a scan of every remote branch
found neither file edited. The promotion itself is described under
**Blocked** above, with the commit that holds a copy of it.
