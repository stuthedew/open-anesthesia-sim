---
id: PL-BXD5
title: tools/new_prose.py's CONTEXT_ROWS = 4, the lines of code printed around each docstring or comment for the copy editor, has no recorded reason: PL-PRCS set it in 20eb2fd29 and neither the commit nor the item says why 4, or what fewer or more rows would cost or catch
priority: P3
effort: S
status: ready
classes: docs
feature: reader-first-prose
touches: tools/new_prose.py
added: 2026-11-04
payoff: a session changing how much code the copy editor sees knows what four rows buy and what a different number would cost
verify: ! grep -qF 'recorded no reason for that number' tools/new_prose.py
---

**Problem.** tools/new_prose.py's CONTEXT_ROWS = 4, the lines of code printed around each docstring or comment for the copy editor, has no recorded reason: PL-PRCS set it in 20eb2fd29 and neither the commit nor the item says why 4, or what fewer or more rows would cost or catch

**Checked 2026-11-04.** `git log -S 'CONTEXT_ROWS = 4'` finds only `20eb2fd29` (`PL-PRCS`). The comment above the constant already says what the rows are for and that more rows lengthen the file the copy editor reads. It ends "`PL-PRCS` set it at 4 and recorded no reason for that number (`PL-22T5`)".

**Why it matters.** A session that changes how much code the copy editor sees cannot tell whether four rows are enough to show what a docstring's "it" points at, or whether fewer would do. The plain-writing rule asks each chosen value for its reason from a record, and this one has none.

**Done when.** The comment above `CONTEXT_ROWS` gives the reason for the number from a record: a measurement on the copy editor's test set or on a branch's units, or a stated choice with what fewer or more rows would cost. The sentence saying that no reason was recorded is gone.

**Generator check.** A one-off. The fact is why this constant is 4. The plain-writing rule's instruction to file an item when a trace finds no reason is what filed it, which is that rule working as intended. No other open item reports a missing reason.
