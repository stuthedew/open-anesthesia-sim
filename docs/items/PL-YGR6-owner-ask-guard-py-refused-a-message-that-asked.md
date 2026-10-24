---
id: PL-YGR6
title: owner_ask_guard.py refused a message that asked for nothing: your choice on the item and armed pull request
priority: P2
effort: S
status: done
classes: defect
feature: review-hold
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
added: 2026-10-20
closed: 2026-10-24
pr: 1721
payoff: a thread's status report reaches the owner without rewording, so a refusal from the guard means a real ask again
verify: grep -q 'def test_a_report_of_a_choice_already_made' tests/unit/test_owner_ask_guard.py
reenters: PL-TLPH
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

**Reproduced 2026-10-20.** `owner_ask_guard.asked` returns a match for "Your choice on the card is recorded on the item, and auto-merge is on for #1700." The match comes from `_HANDOFF`, which lists "your choice", together with `_PULL_REQUEST` in the same sentence. "Recorded your choice on PL-9CS6; the release pull request #1700 is armed." also matches. A report of a choice already made reads the same as an invitation to choose.

**Why it matters.** A guard that refuses a status report trains sessions to reword around it. A session that rewords by habit may also reword around a real ask, which is the case the guard exists to catch.

**Done when.** Both sentences above pass the guard, a real hand-off such as "#1688 is your call" is still refused, and `tests/unit/test_owner_ask_guard.py` pins both cases.

**Generator check.** An instance of `PL-TLPH`'s fact, "whether the owner may be sent a read or merge ask about a pull request", filed after that head closed on 2026-10-19. Recorded as `reenters: PL-TLPH`.

**Fixed 2026-10-24.** The guard now leaves out a noun hand-off ("your call", "your decision", "your choice", "your go") that reports a decision already recorded. It does so in two forms. The first is the object of a recording verb, as in "recorded your choice". The second is the subject of a passive recording verb, as in "your choice on the card is recorded", with at most three words between them. The verbs are listed in `_RECORDED` in `.claude/hooks/owner_ask_guard.py`. A gap that starts a question ("your call on whether #1688 is applied") is still an ask. So is a verb followed by "when", "once", "after", "if" or "as soon". A real hand-off in the same message as a report ("Recorded your choice; #1700 is your call.") is still refused. `_SAME_SENTENCE` still spans a semicolon, because "Over to you; #1688 is ready." is an ask. `tests/unit/test_owner_ask_guard.py` pins both reported sentences from the brief and two more reports among the replies let through, and three near-reports among the asks refused.
