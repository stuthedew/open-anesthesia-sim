---
id: PL-1X2C
title: bin/docket show names the reader's own branch as a carrier and stays silent about the other branch editing the same item
priority: P2
effort: S
status: ready
classes: defect, infra
feature: carrier-detection
touches: subprojects/docket/src/docket/render.py, subprojects/docket/src/docket/vcs.py, subprojects/docket/tests/test_cli.py
added: 2026-09-20
payoff: the one guard that fires when the owner names an item points at the branch that will collide instead of at the reader's own
verify: grep -q 'def test_the_carrier_line_names_the_other_branch_not_the_readers_own' subprojects/docket/tests/test_cli.py
---

**Problem.** bin/docket show names the reader's own branch as a carrier and stays silent about the other branch editing the same item

**Why it matters.** `bin/docket show <id>` is the one guard a session has when
the project owner *names* an item, which is the path that skips `bin/docket
next` entirely. It answered the question wrongly in the only case it has been
observed in: it named the reader's own branch, which the reader already knows
about, and said nothing about the other branch that had committed to the same
item file three and a half minutes earlier.

**Observed 2026-09-20, with both refs fetched.** Two sessions promoted
`PL-B8MK` independently. `claude/amazing-wozniak-yz3dgv` committed `8cb9ae0`
at 17:26:01 (`PL-PQC7, PL-D9K3 Close the unblock print, and promote PL-B8MK
with it`); `claude/cool-carson-63exhu` committed `7c152f1` at 17:29:33. Run on
the second branch after `git fetch origin`, with the first branch's ref
present in the clone, `bin/docket show PL-B8MK` printed:

```
Its file is already edited on claude/cool-carson-63exhu (last commit today).
Not work in flight - PL-B8MK is startable - but a second edit to the
same file collides at merge, so land the smaller change first.
```

That is the reader's own branch. The advice under it - "land the smaller change
first" - is addressed to somebody who does not exist, and the branch that
*should* have been named is missing from the line. The collision was found
instead through `bin/docket stranded`, which surfaced `PL-D9K3` on the other
branch, and only because that pass happened to be run.

**Where to look.** Whatever computes the `Its file is already edited on
<branch>` line (`PL-N1JK`'s addition) appears to select one carrier rather than
all of them, and appears not to exclude the current branch. Both would be worth
fixing and the second is the one that makes the line actively misleading: a
session's own branch is the least useful thing it can name, and naming it reads
as "somebody else is here" to a reader skimming.

**Not the same finding as the `PL-N1JK` gap itself.** That the line exists at
all, and that a queue-only diff does not raise the in-flight mark, are both
deliberate and documented. This is about the line being wrong when it does
fire.

**Done when.** `bin/docket show <id>` names the branches other than the
reader's own that carry an edit to the item's file, names all of them rather
than one, and says nothing where the only carrier is the branch the reader is
standing on - with a test under `subprojects/docket/tests/test_cli.py` driving
a store whose item file is edited on two branches, one of them the current one.

**Blocked.** 2026-09-26, on the slam-dunk run's `claude/pl-batch-03-viadw6`.
Still real on `origin/main` at `a01d64a6`, but not doable in the files this item
declares:

1. The carrier is chosen in `subprojects/docket/src/docket/claims.py`, not in
   `vcs.py`. Since `PL-NST2` (`#988`) the edit read is `claims._editing`,
   inside `claims.holdings`: it builds `FlightReport.editing`, keeps the first
   branch per item (`edited.setdefault(key, ...)`), and is never handed the
   checked-out branch, which `holdings` already reads as `here` for
   `Hold.mine`. `vcs.py` now holds only the `QueueEdit` type, which needs no
   change.
2. `cmd_show` in `subprojects/docket/src/docket/cli.py` takes one edit with
   `next((e for e in flight.editing if e.item_id == item.identifier), None)`, so
   even a report carrying every carrier would print one.

Both halves of **Done when** (every other carrier named, the reader's own left
out) therefore need `claims.py` and `cli.py`, and neither is in `touches`.

**Decision needed: widen `touches` to the files the fix now lives in?**
`subprojects/docket/src/docket/claims.py, subprojects/docket/src/docket/cli.py,
subprojects/docket/src/docket/render.py, subprojects/docket/tests/test_cli.py`,
dropping `vcs.py`, with the brief otherwise as written.

**Recommendation:** yes. The defect is unchanged and only moved with its code,
so the item stays `S` and delegable once `touches` matches, and a triage pass
can make that edit without reopening the brief.

`PL-M1C4`, captured by slam-dunk batch 2 the same night, records this finding
as an untriaged item of its own; one answer here settles both.
