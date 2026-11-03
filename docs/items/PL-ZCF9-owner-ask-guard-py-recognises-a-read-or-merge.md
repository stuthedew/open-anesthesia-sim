---
id: PL-ZCF9
title: owner_ask_guard.py recognises a read or merge ask by its wording, and four messages that asked the owner for nothing were refused on 2026-11-02 and 2026-11-03, each answered by one more exemption
priority: P1
effort: M
status: ready
classes: defect
feature: owner-ask-refusals
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-03
payoff: messages to the owner that ask for nothing stop being refused, so threads stop filing an item for each new phrasing
not-delegable: The fix is a choice of how the guard recognises an ask, and no command written before that choice can tell a fixed guard from one with four more exemptions
root-cause-of: PL-VHMS, PL-0W6J, PL-Q0TK, PL-VNRM
generator: live - PL-YN60 put two new kinds of text under the guard on 2026-11-02, and four messages that asked for nothing were refused in the two days since
misread: Whether a sentence makes the claim a hard gate checks, when the gate recognises it by wording
reenters: PL-GPJ7
---

**Problem.** `.claude/hooks/owner_ask_guard.py` refuses a message to the owner that asks for a pull request read or merge, unless it carries the line `bin/docket arm --owner-ask` prints. It recognises an ask by lists of phrasings (`ASKS`, `_HANDOFF`, `HOLD_FOR_YOUR_READ`). Each message below asked for nothing, matched a phrasing, and was refused:

- `PL-VHMS` (closed 2026-11-02): "each/both will wait for your read", where no pull request is named.
- `PL-0W6J`: the same hold, quoted as a mention in a progress line.
- `PL-Q0TK`: work waiting on the owner's go-ahead on a decision card.
- `PL-VNRM`: "nothing below needs your read now", a withdrawal.

Each fix so far added an exemption for one phrasing. `PL-XR8B` and `PL-YGR6` were the same failure in October.

**Why this is a generator now.** `PL-5HQY` answered on 2026-11-02 that `PL-TLPH` needed no successor. Its reason was that no false refusal had been filed since `#1721` on 2026-10-24. It said the question reopens after three more such filings, and these four meet that. The burst follows `PL-YN60`, which on 2026-11-02 brought progress-checklist edits and decision cards under the guard. Each new kind of text meets the phrasing lists for the first time, so more refusals are likely.

**Why it matters.** `PL-TLPH`'s trade held that a false refusal costs one rewording. The owner ratified it on 2026-10-19, over adding more text for sessions to read. The trade left out a second cost. The refusal tells the thread to file an item, so each new phrasing also adds an item to the queue. Four arrived in two days.

**What the fix must keep.** No unrecorded read or merge ask about a pull request reaches the owner, which is `PL-TLPH`'s purpose. Narrowing how the guard recognises an ask is a session's call. Replacing the refusal with an advisory is the alternative the owner's answer was chosen over, so a fix that needs it goes back to the owner with a recommendation.

**Done when.** The four messages pass the guard as rows in `tests/unit/test_owner_ask_guard.py`, and every message those tests refuse today is still refused. The brief records why the new recognition does not need another exemption for each new phrasing. Otherwise the brief puts the trade back to the owner, with a recommendation and the count above.

**Reproduced 2026-11-03.** `refusal()`, run on `main` at `a7806459`, refuses `PL-0W6J`'s quoted message and reconstructions of the other two open members. Each member's brief has its message.

**Generator check.** A successor to `PL-GPJ7`, whose fact these four misread: the guard recognises an ask by its wording. `PL-5HQY` named `PL-GPJ7` as the head a third false refusal would re-enter.
