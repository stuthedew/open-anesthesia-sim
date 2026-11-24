---
id: PL-Y12B
title: Record the owner's answer of 2026-11-24 that Projects threads stay in the effort trial at about 1.75 times their usage, which PL-C38D's build did not carry
priority: P3
effort: S
status: ready
classes: housekeeping
feature: effort-trial
touches: docs/items/PL-C38D-bring-projects-threads-into-the-effort-trial.md
added: 2026-11-24
payoff: a later session reads that the owner kept threads in the effort trial knowing its usage cost, and does not ask him again
verify: grep -qF 'Agree with best practice changes' docs/items/PL-C38D-bring-projects-threads-into-the-effort-trial.md
---

**Problem.** Record the owner's answer of 2026-11-24 that Projects threads stay in the effort trial at about 1.75 times their usage, which PL-C38D's build did not carry

**What happened.** The owner chose on a card to bring Projects threads into
the effort trial (`PL-C38D`). After that, this thread told him that threads in
the trial run half their work at `xhigh`. On Anthropic's published benchmark,
a solved task costs $0.30 at `high` and $0.75 at `xhigh` (*Optimizing for cost
and intelligence*,
https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence,
read 2026-11-24), so threads would use about 1.75 times what they use now. The
card had not carried that cost, so the thread asked again whether to keep
threads in the trial or stop it, and recommended keeping it. The owner
answered "Agree with best practice changes" at 20:04 UTC, which the
coordinator relayed as keeping threads in the trial. `PL-C38D` closed in
#2321 before the answer arrived, so its brief does not record it.

**Generator check.** One-off. The fact is the owner's answer to a question
asked after the item that it belongs to had closed, and the item's brief is
its record.

**Done when.** `PL-C38D`'s brief records the answer, with what it was chosen
over.
