---
id: PL-5HQY
title: bin/docket inflow names PL-TLPH (owner_ask_guard.py's hold on a read or merge ask) re-entered by PL-YV90, PL-XR8B and PL-YGR6 since 2026-10-20, with no successor head and no no-successor answer: decide which is owed, and whether the false refusals are PL-GPJ7's fact (a gate that recognises a claim by its wording)
priority: P2
effort: S
status: done
classes: housekeeping
feature: generator-heads
touches: docs/items
added: 2026-11-01
closed: 2026-11-02
pr: 1928
payoff: bin/docket inflow stops asking every session whether the owner-ask guard's fix held, because the answer and its reason are recorded
verify: grep -q '^\*\*Answer' docs/items/PL-5HQY*.md
no-successor: PL-TLPH
---

**Problem.** bin/docket inflow names PL-TLPH (owner_ask_guard.py's hold on a read or merge ask) re-entered by PL-YV90, PL-XR8B and PL-YGR6 since 2026-10-20, with no successor head and no no-successor answer: decide which is owed, and whether the false refusals are PL-GPJ7's fact (a gate that recognises a claim by its wording)

**Evidence.** `bin/docket inflow`, run on 2026-11-01, prints this head under
"Re-entered by three or more filings, a generator whose fix did not hold". It
prints no successor and no `no-successor:` answer for it. No open item named
the head before this one. All three re-entering items are closed. `PL-FM15`
is the model for the answer.

**Why it matters.** `bin/docket inflow` prints this line on every run until an
item answers it, so each session that reads the report is asked the same
question again. The line names the guard that stops a bare read or merge ask
from reaching the owner. If that guard's fix did not hold, a successor head is
owed, and it ranks as a generator. If the fix held, a `no-successor:` answer
with its reason stops the question from returning.

**Read at triage, 2026-11-01.** These are facts from the four item files, not
the answer. `PL-TLPH`'s section "What it does not reach" left the
coordinator's `post_message` out on purpose and named `PL-YV90` as the item for
that gap. `PL-XR8B` closed on 2026-10-20 under `#1688`, which is `PL-TLPH`'s
own pull request. `PL-YGR6` closed on 2026-10-24 under `#1721`. `PL-XR8B` and
`PL-YGR6` were both messages that asked for nothing. The hand-off pattern
`_HANDOFF` in `.claude/hooks/owner_ask_guard.py` refused each one because of
its wording.

**Done when.** This brief records the answer, with its reason, in a paragraph
that opens `**Answer`, as `PL-FM15` does. Either this item sets
`no-successor: PL-TLPH`, or the answer names a successor head that records
`root-cause-of:`, `generator:`, `misread:` and `reenters: PL-TLPH`. The answer
also says whether `PL-XR8B` and `PL-YGR6` share `PL-GPJ7`'s fact. Afterwards
`bin/docket inflow` no longer lists `PL-TLPH` under "a generator whose fix did
not hold".

**Generator check.** One-off. This item records a decision about `PL-TLPH`'s
line and does not misread a fact itself.

**Answer: no successor head is owed for `PL-TLPH`, and the two false refusals
do share `PL-GPJ7`'s fact, by a trade the owner ratified.** This is a
session's decision, taken under Order item 66 of the v0.7.0 project ("Fix
generator-heads, drift and stale source claim features", project owner,
2026-11-02), so ordinary evidence reopens it. The field
`no-successor: PL-TLPH` records it. The line opens again once three more
filings re-enter `PL-TLPH` after 2026-11-01. Read on `main` at `cdf9a8fdf`.

**What `PL-TLPH` fixed, and whether any re-entry shows that fix failing.**
`PL-TLPH`'s `misread:` is whether the owner may be sent a read or merge ask
about a pull request. Its fix refuses such an ask at the moment it goes out,
unless the message carries the line `bin/docket arm --owner-ask` prints. None
of the three re-entries is an unrecorded ask that reached the owner.

- `PL-YV90` (the coordinator's posts were not checked) is a part of
  `PL-TLPH`'s own fix that was not done yet. `PL-TLPH`'s section "What it does
  not reach" left the coordinator's `post_message` out on purpose and named
  `PL-YV90` for it. `#1721` wired the partial check on 2026-10-24. It is the
  same shape as `PL-LNFG` under `PL-4FBP` in `PL-FM15`'s answer.
- `PL-XR8B` (2026-10-19, a hand-off word in quote marks) and `PL-YGR6`
  (2026-10-20, "your choice is recorded") are the opposite failure: the hook
  refused a message that asked for nothing. Each cost one rewording, and each
  was narrowed with test rows, in `#1688` and `#1721`.

**Whether the false refusals are `PL-GPJ7`'s fact: yes.** `PL-GPJ7`'s
`misread:` is whether a sentence makes the claim a hard gate checks, when the
gate recognises it by wording. `owner_ask_guard.py` is a hard gate, and
`ASKS` recognises an ask by its wording. Both refusals came from `_HANDOFF`,
the hand-off words "over to you" and "your choice". The hook was built on
2026-10-19, three weeks after `PL-GPJ7` closed, so `PL-GPJ7`'s fix never
reached it.

`PL-GPJ7`'s remedy does not apply here, and that was decided, not missed. It
had two parts: recognise the claim by explicit syntax, and demote what needs
wording to an advisory. An ask to the owner is free prose, so it has no
explicit syntax to recognise. And the advisory route is the one that failed
three times before `PL-TLPH`: `PL-9KHK`, `PL-DKBG` and `PL-9JHM` each changed
text a session reads, and a session still sent a bare ask. So `PL-TLPH`
chose a wording list that leans toward refusing, and wrote the trade into the
hook's docstring: a false refusal costs a rewording, and a missed ask costs
the owner's attention. The owner agreed to that fix on 2026-10-19 ("Agree
with your rec", ratified, over more text for a session to read). The
hand-off pattern was added the same day, after the owner asked why "Over to
you for #1688" had passed. So this gate is a ratified exception to
`CLAUDE.md`'s rule that reserves hard failure for exact rules. It is not a
new instance of the gap `PL-GPJ7` closed.

**Why no successor head.** A successor would fix a mechanism that still
produces items. The false refusals came from one pattern, both in its first
two days. No false refusal has been filed since `#1721` narrowed it on
2026-10-24. Two members with a ratified trade behind them are not a generator under
triage's three-instance rule. The refusal tells a refused session to file an
item when its message was not an ask, so a third false refusal would reach the
queue. It would then re-enter `PL-GPJ7`'s line and reopen this question with a
count behind it.

**Found while answering, and filed, not answered here.** The hook's
`TEXT_FIELDS`, and the matcher in `.claude/settings.json`, name the tools
`mcp__hearthbot__reply`, `update_message` and `ask_decision`. A thread on
2026-11-02 has `post_message`, `edit_message` and `request_decision` instead.
So a thread's reply now gets only the coordinator's partial check, and an
edited message or a decision card gets none. That is a new defect in
`PL-TLPH`'s fix rather than one of the three re-entries, and its own item
records it, with `reenters: PL-TLPH`.
