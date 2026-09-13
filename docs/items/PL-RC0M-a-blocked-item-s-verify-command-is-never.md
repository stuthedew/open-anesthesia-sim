---
id: PL-RC0M
title: "A blocked item's verify: command is never replayed, so it can rot unnoticed and redden whichever pull request unblocks it"
priority: P2
effort: S
status: done
classes: defect, infra
feature: dev-tooling
touches: subprojects/docket/src/docket/verify.py, subprojects/docket/src/docket/checks.py, subprojects/docket/tests/test_verify.py
added: 2026-09-06
closed: 2026-09-13
verify: uv run pytest subprojects/docket/tests/test_verify.py subprojects/docket/tests/test_checks.py -q -k blocked && python3 -c "import pathlib; t=pathlib.Path('subprojects/docket/src/docket/verify.py').read_text(); raise SystemExit(0 if 'SCOPED_ONLY_STATUSES' in t else 1)"
---

**Problem.** `already_passing` replays the commands of items at `ready` or
`needs-decision` - `LANDED_STATUSES` in
`subprojects/docket/src/docket/verify.py`. A `blocked` item's command is never
run, so nothing notices when it stops discriminating, and the finding arrives
at the worst moment: the pull request that unblocks the item is the one that
goes red.

**The instance, 2026-09-06.** `PL-N092`'s command was
`doc_check check && ! grep -q '…' README.md`, written 2026-09-01 while
`README.md` existed. `PL-WB5K` deleted that file on 2026-09-05. `grep` on a
missing file exits 2, which `!` inverts to success, so from that moment the
command passed on a tree where none of the work had been done - the "would
ACCEPT a branch that did none of it" case `docket check` calls an error. It sat
that way for a day, invisible, because the item was `blocked` on `PL-XYRN`.
Unblocking it put it in scope and CI failed on the next push.

**Why it matters.** The rot is silent while it lasts and its cost lands on
somebody else's change. Worse, the item most likely to be unblocked is the one
somebody is about to work, so the failure arrives exactly when a session is
trying to start - and the natural reading of a red `docket check` on a
one-line status edit is that the status edit was wrong.

It is also the narrow case where the store's own guard is blind rather than
wrong, which is the shape `CLAUDE.md` reserves the "silent wrong answer" test
for: `docket check` reports the store sound while holding a command that proves
nothing.

**Where.** `subprojects/docket/src/docket/verify.py`, `LANDED_STATUSES` and
`already_passing`'s candidate filter; `subprojects/docket/src/docket/checks.py`
for how a finding about a blocked item should be worded.

**Decision needed — ANSWERED 2026-09-13, see below.** What the `verify:` replay is for — whether it guards every
open item's command, or only the commands of items a session could act on now.
The three options below follow from that, and none is obviously right.

**Options, none obviously right.**

1. **Add `blocked` to `LANDED_STATUSES`.** One line, and it costs: the replay
   is the most expensive thing `docket check` does, and this widens the pool
   permanently to buy a finding about work nobody can start. The
   whole-store sweep on `push` to `main` is where that cost would land, which
   `PL-SDHR` just made the only place it is paid.
2. **Replay a blocked item only when its own status changes**, which the diff
   already knows - `changed_items` is exactly this set, and `PL-SDHR` wired it
   in. That catches the case at the moment it matters and costs nothing on any
   other run, but it is a special case in a filter that currently has none.
3. **Leave it**, and treat a red CI on an unblocking commit as the mechanism
   reporting correctly, one push late. The cost is one wasted cycle per
   occurrence and a confusing first reading.

**Recommended: 2**, on the argument that the trigger is already computed and
the finding is worth having at the moment a session is about to pick the item
up. But it is a real design call about what the replay is for, so this is a
decision rather than a task.

**Done when.** Either a blocked item's command is checked at the moment its
status changes, or the decision is recorded that the rot is acceptable and why.

**Found while working `PL-N092`'s unblocking, 2026-09-06.**

**Answered 2026-09-13 (project owner): option 2.** The replay guards the
commands of items a session could act on now, *plus* any item a branch has
actually edited — which is where a blocked item's command becomes both cheap
and timely to ask about.

**What was built.** `SCOPED_ONLY_STATUSES = ("blocked",)` in
`subprojects/docket/src/docket/verify.py`, added to the candidate statuses only
when `scoped_to` is not `None`. So the whole-store sweep on `push` to `main` is
unchanged and costs exactly what it did, while a `pull_request` run — already
narrowed to `changed_items` by `PL-SDHR` — asks about a blocked item the branch
touched. `already_passing` reports the answer in a new `LandedReport.blocked`,
the subset of `passing` whose items are at one of those statuses.

**`checks.py` words it as one reading rather than two, which is the half the
item flagged and the half that matters to a session.** The standing message
offers "either the work landed — close it — or the command does not
discriminate". For an item nobody can start the first branch is impossible, so
that sentence would send a session at a status edit when what is broken is the
command. Blocked items get their own error naming the single reading, are
removed from the two-reading finding's list and its `N of M` count, and are not
told a second time by the `shared` clause, which says something the blocked
sentence has already said outright.

**Tests.** Five in `test_verify.py` — the sweep leaves a blocked item alone, a
scoped run asks about one the branch changed, a scoped run still ignores one
outside its scope, a blocked item whose command correctly fails is not a
finding, and `blocked` is always a subset of `passing`. Three in
`test_checks.py` for the wording, the de-duplication and the count. Verified by
mutation: dropping the `scoped_to is not None` guard, so blocked items join the
sweep, fails `test_a_blocked_item_is_left_out_of_the_whole_store_sweep`.

**Why not the other two.** Option 1 widens the most expensive thing `docket
check` does, permanently, to buy findings about work nobody can start — and
`PL-SDHR` had just narrowed that same cost. Option 3 leaves a guard that
reports the store sound while holding a command that proves nothing, which is
`CLAUDE.md`'s silent-wrong-answer test and the reason this was taken first of
the four decisions in its batch.

**What this does not catch, stated so it is not rediscovered as a defect.** The
`PL-N092` instance itself would still not have been caught on the day it broke:
`PL-WB5K` deleted `README.md` without touching `PL-N092`'s file, so no branch
was in scope for it until the unblocking one. What the fix buys is every branch
that does edit a blocked item — filling `touches`, editing the brief, blocking
it in the first place — finding the rot then, rather than the unblocking pull
request wearing it. Catching the deletion case needs the sweep, which is
option 1 and is rejected on cost.
