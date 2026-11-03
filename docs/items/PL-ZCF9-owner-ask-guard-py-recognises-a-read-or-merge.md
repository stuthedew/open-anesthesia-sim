---
id: PL-ZCF9
title: owner_ask_guard.py recognises a read or merge ask by its wording, and four messages that asked the owner for nothing were refused on 2026-11-02 and 2026-11-03, each answered by one more exemption
priority: P1
effort: M
status: done
classes: defect
feature: owner-ask-refusals
touches: .claude/hooks/owner_ask_guard.py, tests/unit/test_owner_ask_guard.py
deferred-from: v0.7.0 - workflow tooling outside the schematic release
added: 2026-11-03
closed: 2026-11-03
pr: 1973
payoff: messages to the owner that ask for nothing stop being refused, so threads stop filing an item for each new phrasing
not-delegable: The fix is a choice of how the guard recognises an ask, and no command written before that choice can tell a fixed guard from one with four more exemptions
root-cause-of: PL-VHMS, PL-0W6J, PL-Q0TK, PL-VNRM
generator: spent - each of the four contexts behind the six false refusals is now a rule that reads every phrase ASKS finds, so a new phrasing in one of them passes unchanged; a refusal in a new kind of context re-enters PL-GPJ7
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

**Answer, 2026-11-03: the guard now finds an ask phrase and then decides from its context whether the sentence asserts it, so a new phrasing in a known context needs no new exemption.** `ASKS` still lists the phrasings of an ask. A new function, `unasserted`, reads the context of every phrase found, by four rules that each apply to every pattern in `ASKS`:

1. **Quoted.** The phrase lies wholly inside quote marks or a code span that names no pull request (`PL-XR8B`, `PL-0W6J`). A quotation that names one can be a thread's bare ask relayed, so it is still refused.
2. **About a decision card.** The phrase's clause names a card and no pull request (`PL-Q0TK`). The card is a `request_decision` call, which the hook reads itself.
3. **Negated.** "not", "n't", "never", "without" or "no longer" stands just before the phrase, or its clause opens with "nothing", "none", "neither" or "no" (`PL-VNRM`). An exception later in the sentence that names a pull request, such as "except #1950", makes it an ask again.
4. **Foretold.** "each" or "both" and a modal stand just before the phrase, in a sentence that names no pull request. This is `PL-VHMS`'s rule, which read only the hold before and now reads every pattern.

`PL-YGR6`'s rule for a reported decision stays inside `_HANDOFF`, because only a noun hand-off such as "your choice" can be reported as recorded.

**Why no exemption is needed per phrasing.** Each earlier fix exempted one phrasing in one pattern: a quote mark only before a hand-off, a future only before a hold. The next phrasing in the same context was refused again, which is how four arrived in two days after `PL-YN60`. Each rule now reads the context of any phrase that `ASKS` finds. The tests show this with phrasings no thread has sent: for each rule, other phrasings in the same context pass, and rows just outside the rule's edge are still refused. ConText, the standard method in clinical text processing for telling an asserted finding from a negated, hypothetical, historical or other-person one, splits the problem the same way (Harkema, Dowling, Thornblade and Chapman, J Biomed Inform 2009;42(5):839-851, doi:10.1016/j.jbi.2009.05.002). It extends NegEx, which handles negation alone (Chapman et al., J Biomed Inform 2001;34(5):301-310, doi:10.1006/jbin.2001.1029). What still needs a change is a new kind of context, which needs a new rule. A false refusal of a kind none of the four rules covers re-enters `PL-GPJ7`, and three of them reopen this head's question.

**Measured against real messages, 2026-11-03.** A subagent collected every sentence or checklist line containing an ask word ("your read", "your review", "your call", "merge it" and 20 more) from the project chat and all 43 threads active since 2026-10-28: 110 sentences. The guard on `main` at `7f93ea9c` and this one agree on 109. Both refuse the same 45, each an ask for a read or a merge, and both pass the same 64. The one that differs is "I'm starting the change so checked rewrites merge without waiting on your read.", posted in the project chat on 2026-11-02. It asks for nothing, `main` refuses it, and this guard passes it by the negation rule; it is now a test row. So in a week of real traffic the narrowing let no real ask through. The four refused messages are not in that sample, since a refused message was reworded before it was posted.

**What it keeps.** All 33 messages the tests refused before are still refused, and 15 rows were added at the rules' edges. The refusal stays hard, so the trade the owner ratified on 2026-10-19 (`PL-TLPH`) is unchanged and nothing goes back to the owner. Each rule is narrow, so a doubtful case is refused: a clause ends at any comma, at most three words may come between a negative subject and the phrase, and a quotation that names a pull request is not a mention.
