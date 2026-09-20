---
id: PL-1X2C
title: bin/docket show names the reader's own branch as a carrier and stays silent about the other branch editing the same item
status: untriaged
feature: carrier-detection
added: 2026-09-20
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
