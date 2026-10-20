---
id: PL-YGR6
title: owner_ask_guard.py refused a message that asked for nothing: your choice on the item and armed pull request
status: untriaged
added: 2026-10-20
---

**Problem.** owner_ask_guard.py refused a message that asked for nothing: your choice on the item and armed pull request

On 2026-10-20, during the v0.6.0 cut (`PL-9CS6`), the hook refused a thread
reply that only reported a status. The reply told the owner that the choice he
made on a card was recorded on the item and that auto-merge was on for the
release pull request (`#1700`). It asked him for nothing. The guard seems to
treat "your choice", "the item" and an armed pull request in one message as a
read or merge ask. The session reworded the reply to get past it. A guard that
refuses a status report trains sessions to reword around it, so check which
words it keys on and narrow the match to a message that actually asks.
