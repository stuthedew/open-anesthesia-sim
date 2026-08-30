---
id: PL-5GFK
title: The gate-progress rule injects simulator work into every process-work session, which PL-36SC did not reach
status: untriaged
feature: worker-instructions
touches: CLAUDE.md
added: 2026-08-30
classes: defect
---

**Problem.** `CLAUDE.md`'s "Report gate progress after every completed item"
requires a session closing *any* item to report where the debt gate stands —
how many entries are done, what the remaining ones are, glossed and grouped.
The gate's remaining entries are all simulator work. So a session that closes
a tooling item ends by listing eight core-model items the owner was not asking
about.

`PL-36SC` scoped the release offer and the `what next` ranking to sessions
actually answering "what next". It did not touch this bullet, which is the
third and least obvious channel by which product work arrives in a process
discussion — and the one that fires most often, because it is triggered by
completing an item rather than by the shape of the question.

**Why it matters.** The owner raised the pattern directly (2026-08-30): "you
keep recommending project work when I am trying to get process workflow
finalized." Two of the three sources are now scoped; this one is not, so the
behaviour continues at reduced volume, which is the worst outcome — the rule
looks fixed and is not.

The rule itself is right for the case it was written for. `PL-9CNQ` filed it
because the owner is tracking how far the current gate has to run, and a
session that closes a gate item and says nothing leaves that invisible. The
fix is a scope line, not a deletion — the same shape `PL-36SC` used.

**Worth deciding.** Whether the trigger should be "the item just closed was
*in* the gate" (decidable — `docket gate` already computes membership, so this
could be a tool answer rather than an instruction) or "the session is about
the milestone". The first is cheaper and cannot be forgotten.

**Done when.** Closing a process item that the gate does not contain does not
produce a report on the gate, and the rule still fires when a gate item
closes.
