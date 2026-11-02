---
id: PL-5HQY
title: bin/docket inflow names PL-TLPH (owner_ask_guard.py's hold on a read or merge ask) re-entered by PL-YV90, PL-XR8B and PL-YGR6 since 2026-10-20, with no successor head and no no-successor answer: decide which is owed, and whether the false refusals are PL-GPJ7's fact (a gate that recognises a claim by its wording)
priority: P2
effort: S
status: ready
classes: housekeeping
feature: generator-heads
touches: docs/items
added: 2026-11-01
payoff: bin/docket inflow stops asking every session whether the owner-ask guard's fix held, because the answer and its reason are recorded
verify: grep -q '^\*\*Answer' docs/items/PL-5HQY*.md
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
