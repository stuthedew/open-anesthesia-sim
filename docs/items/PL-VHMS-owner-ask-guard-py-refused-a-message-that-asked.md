---
id: PL-VHMS
title: owner_ask_guard.py refused a message that asked for nothing: wait for your read
status: untriaged
added: 2026-11-02
---

**Problem.** On 2026-11-02 `.claude/hooks/owner_ask_guard.py` refused a thread
reply that said "Because each one changes MODEL.md, each will wait for your
read". The sentence stated a fact about what would happen and asked the owner
for nothing in that reply. The guard read "wait for your read" as an ask for a
generic read, which `owner-ask-not-generic-read` forbids. The reply was reworded
to pass.

**Why it matters.** A false refusal costs a reword each time, and teaches a
session to avoid stating that a pull request will hold for the owner's read,
which the owner needs to know.

**How.** Read the guard's pattern for a read ask and narrow it to a request
form, such as an imperative or a question addressed to the owner, so a
statement in the future tense passes. Add the refused sentence as a test case
that must pass.

**Done when.** The guard passes the sentence above and still refuses the asks
its tests already list.
