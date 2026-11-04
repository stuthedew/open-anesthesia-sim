---
id: PL-0W6J
title: owner_ask_guard.py refused a progress checklist that quoted the hold it now lets through: wait for your read, inside quote marks in a sentence naming a PR
priority: P2
effort: S
status: done
classes: defect
feature: owner-ask-refusals
milestone: v0.6.15
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-02
closed: 2026-11-03
pr: 1973
payoff: a progress line that quotes the hold it reports on reaches the owner without a rewording
verify: grep -q 'def test_a_quoted_hold_in_a_progress_line_passes' tests/unit/test_owner_ask_guard.py
reenters: PL-GPJ7
---

**Problem.** owner_ask_guard.py refused a progress checklist that quoted the hold it now lets through: wait for your read, inside quote marks in a sentence naming a PR

**Where this came from.** On 2026-11-02 the thread building `PL-VHMS` posted a
progress checklist line: `PL-VHMS: guard lets "each/both will wait for your
read" through when no PR is named; tests pass`. The guard refused it. The hold
sat inside quote marks, as a mention, and the sentence named a pull request
("PR"), so the `PL-VHMS` exemption did not apply. `PL-XR8B` already skips a
hand-off just after a quote mark, but `HOLD_FOR_YOUR_READ` has no such
lookbehind. The line was reworded. Whether a quoted hold should be skipped the
same way is the question.

**Why it matters.** Each false refusal costs the sending thread a rewording. The refusal also tells the thread to file an item, so each new phrasing adds one to the queue. Four messages that asked the owner for nothing were refused on 2026-11-02 and 2026-11-03. `PL-ZCF9` records them as one mechanism.

**Reproduced 2026-11-03.** `refusal()` in `.claude/hooks/owner_ask_guard.py`, run on `main` at `a7806459` with the message quoted above, refuses it and names "wait for your read" as the ask.

**Done when.** The message quoted above passes the guard as a row in `tests/unit/test_owner_ask_guard.py`. An unquoted "wait for your read" in a message that names a pull request is still refused.

**Generator check.** The fact is `PL-GPJ7`'s: whether a sentence makes the claim a hard gate checks, when the gate recognises it by wording. This item is a member of `PL-ZCF9`, the successor head filed in the same triage pass (`reenters: PL-GPJ7`).

**Fixed under `PL-ZCF9`, 2026-11-03.** The message above now passes the guard by the quotation rule: the hold lies wholly inside quote marks that name no pull request. Its row is in `tests/unit/test_owner_ask_guard.py`, beside other phrasings in the same context and the rows just outside the rule that are still refused. `PL-ZCF9`'s brief says why the fix covers the context rather than this one phrasing.
