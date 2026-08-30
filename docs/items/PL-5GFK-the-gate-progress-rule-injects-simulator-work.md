---
id: PL-5GFK
title: The gate-progress rule injects simulator work into every process-work session, which PL-36SC did not reach
priority: P2
effort: S
status: done
classes: defect
feature: worker-instructions
milestone: v0.2.7
touches: CLAUDE.md
added: 2026-08-30
closed: 2026-08-30
commit: 948ca35
verify: python3 tools/doc_check.py check
not-delegable: the change rewrites a rule in CLAUDE.md that every session then follows; whether the scoped rule fires in the right sessions is a judgment about instruction prose, which no check decides
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

**Decided at triage, confirmed by the project owner (2026-08-30).** The
trigger is membership: the rule fires when the item just closed is one the
gate contains, and is silent otherwise. That is the cheaper of the two and
the one that cannot be forgotten, and it needs no tool change — `bin/docket
wave` prints the gate's open entries by id and `bin/docket gate` recomputes
the split, so the test is answerable at the moment the rule fires. The edit
is therefore a scope line on the existing bullet, in the same shape `PL-36SC`
used, rather than a new command.

**Also corrected in the same bullet.** It closed with "`PL-9CNQ` exists to
make this computed rather than transcribed; until it lands, this is done by
hand". `PL-9CNQ` (a `docket gate` command, so the frozen debt list is computed
rather than transcribed) landed in `0eaa17f` and shipped in v0.2.6, so the
sentence instructed every session to transcribe by hand a list the tool now
prints. Replaced with the two commands, which is also what makes the
membership test above decidable.

**Done when.** Closing a process item that the gate does not contain does not
produce a report on the gate, and the rule still fires when a gate item
closes.
