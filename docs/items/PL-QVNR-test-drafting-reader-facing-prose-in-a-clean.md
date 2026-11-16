---
id: PL-QVNR
title: Test drafting reader-facing prose in a clean process from a list of facts, as a fix on the writing side of PL-J1ZM
priority: P2
effort: M
status: dropped
classes: infra
feature: copy-editor
touches: .claude/rules/plain-writing.md
added: 2026-11-10
closed: 2026-11-14
reason: Its method compares a drafted passage with the copy editor's edit using the blind judge and the meaning check, which PL-GL45 removed on the owner's choice of 2026-11-14, and the owner stopped the work on PL-J1ZM, whose fix it tested, on the same day.
payoff: the owner learns whether prose written from a fact list in a clean process needs less repair than prose a session writes itself
verify: grep -qE '^[*][*]Measured 20' docs/items/PL-QVNR-*.md
---

**Problem.** Test drafting reader-facing prose in a clean process from a list of facts, as a fix on the writing side of PL-J1ZM

**Why it matters.** The copy editor repairs prose after a session has
written it. `PL-J1ZM` (sessions over-explain in every kind of text) records
why the prose arrives long: each writing rule adds something a text must
carry, and the session that writes it knows the whole history of the change
and puts that in. The copy editor runs in a clean process with none of that
history. The same separation may work one step earlier. A session would list
the facts the reader needs, and a clean process that knows only those facts,
the reader and the writing rule would write the passage.

The owner refused showing approved examples to writers on 2026-11-04
(`PL-J1ZM`), and this test shows the writer none.

**How to do it.** Take passages that sessions wrote and the copy editor then
rewrote, from the saved runs. For each, list its facts from the text before
the edit. Have a clean process write the passage from that list. Give the
blind judge (`tools/prose_judge.py`) that version against the copy editor's
edit, and run the meaning check on both against the fact list.

**Done when.** This item records the result in a paragraph that opens
"**Measured 20**" with the date, and says whether a drafting step is worth
proposing to the owner.

**Generator check.** A one-off. It tests a fix for the live generator
`PL-J1ZM`, so the pause on new workflow mechanisms does not hold it.
