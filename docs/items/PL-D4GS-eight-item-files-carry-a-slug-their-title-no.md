---
id: PL-D4GS
title: Eight item files carry a slug their title no longer generates, which PL-3833's new advisory reports and no item owns
status: dropped
closed: 2026-09-13
added: 2026-09-13
priority: P3
effort: S
classes: defect, infra
feature: dev-tooling
touches: docs/items/
reason: Duplicate of PL-YTDN, filed independently the same day; its three unique contributions were folded into PL-YTDN before this was dropped
---

**Problem.** Eight item files carry a slug their title no longer generates, which PL-3833's new advisory reports and no item owns

**Observed 2026-09-13**, on the `make check` run that cut v0.4.15 - the first
release to carry `PL-3833`'s filename-drift advisory, which is what reports
them:

```
8 item files carry a slug their title no longer generates (PL-0VFF, PL-5N7T,
PL-6194, PL-68XK, PL-K9HV, PL-TTMF, PL-XQRK, PL-ZX12); rename with `git mv` to
the name `docket` would write, and check first that no open branch is editing
the file - a rename against someone else's edit conflicts
```

**Why this is an item rather than a line in somebody's close-out.** The
advisory is correct and its remedy is deliberately not scripted: `PL-3833`
made it an advisory because choosing whether to rename, and checking who else
holds the file, needs judgment a tool does not have. That is the right design
and it has a consequence - the advisory has no owner, so it fires on every
`make check` in every session and none of them is the session whose job it is.
`CLAUDE.md` calls an advisory nobody acts on a candidate for retirement rather
than promotion, and this one is three days old, so the answer is to give it an
owner once rather than to let it earn that reputation.

**The ordering constraint is the whole difficulty.** A rename conflicts against
any branch editing the file, and at least one of the eight was being worked as
this was written (`PL-ZX12`, in a session titled for the stale-name batch of
Gate 1). So this is not a sweep to run start to finish: it is `bin/docket
stranded`/`flight` first, then `git mv` only the files no live branch holds,
then re-run `make check` and leave the rest named in the close-out for the next
pass.

**Check before starting** whether `PL-LBR6` has landed - `bin/docket record`
renames a drifted file as a side effect of writing a `pr:`, so some of the
eight may have been renamed by a command that was asked to do something else,
and the two items should not fight over the same files.

**Done when.** Every item file whose slug no longer matches its title has
either been renamed or is named in this item with the branch that holds it, and
`make check`'s advisory is empty or lists only the held ones.

**Why it matters.** Kept rather than deleted so the finding is not raised a
third time: the filename-drift advisory is ownerless by design and attracts a
fresh capture from every session that meets it, which is two in one day.

**Dropped 2026-09-13 as a duplicate of `PL-YTDN`** (rename the item files whose
slug no longer matches their title), which was filed earlier the same day and
carries the measurement this one does not: 0 of the drifted files are
referenced by path in any other item's `verify:` or brief, against 34 items
that do hardcode some item path, plus the one-liner to re-run that check
because the store moves.

What this brief had and that one did not is folded into `PL-YTDN` rather than
lost: the corrected count of eight and why it moved, the dependency on
`PL-LBR6`, and the ordering constraint that a rename conflicts against any
branch holding the file, so the pass renames what is free and names the rest.

**Done when.** Nothing - dropped. `PL-YTDN` carries the work.
