---
id: PL-D4GS
title: Eight item files carry a slug their title no longer generates, which PL-3833's new advisory reports and no item owns
status: untriaged
added: 2026-09-13
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
