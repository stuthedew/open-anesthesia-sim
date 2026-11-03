---
id: PL-Q0TK
title: owner_ask_guard.py refused a progress checklist that said a code edit was waiting on the owner's go-ahead on a decision card, though it asked for no pull request read or merge (PL-L08H thread, 2026-11-02)
priority: P2
effort: S
status: ready
classes: defect
feature: owner-ask-refusals
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-02
payoff: a thread can tell the owner that work waits on their decision card without the guard refusing it
verify: grep -q 'def test_a_go_ahead_on_a_decision_card_passes' tests/unit/test_owner_ask_guard.py
reenters: PL-GPJ7
---

**Problem.** owner_ask_guard.py refused a progress checklist that said a code edit was waiting on the owner's go-ahead on a decision card, though it asked for no pull request read or merge (PL-L08H thread, 2026-11-02)

**Where this came from.** The thread working `PL-L08H` posted a progress checklist on 2026-11-02. One line said a code edit was waiting on the owner's go-ahead on a decision card. It asked for no pull request read and no merge, and the guard refused it. The item does not quote the line.

**Why it matters.** Each false refusal costs the sending thread a rewording. The refusal also tells the thread to file an item, so each new phrasing adds one to the queue. Four messages that asked the owner for nothing were refused on 2026-11-02 and 2026-11-03. `PL-ZCF9` records them as one mechanism.

**Reproduced 2026-11-03.** The item does not quote the message, so this is a reconstruction: "PL-L08H: the code edit is waiting on your go-ahead on the decision card; PR #1950 stays a draft until then". The pull request number is made up. `refusal()` refuses it and names "waiting on your go-ahead" as the ask.

**Done when.** A message that says work waits on the owner's answer on a decision card, and asks for no pull request read or merge, passes the guard as a row in `tests/unit/test_owner_ask_guard.py`. A message that asks the owner to read or merge a pull request is still refused.

**Generator check.** The fact is `PL-GPJ7`'s: whether a sentence makes the claim a hard gate checks, when the gate recognises it by wording. This item is a member of `PL-ZCF9`, the successor head filed in the same triage pass (`reenters: PL-GPJ7`).
