---
id: PL-LK62
title: Told read only, a session left its own auto-merge armed and offered a hold instead of disarming it, so PR 1213 merged against the instruction
priority: P2
effort: S
status: done
classes: defect
touches: CLAUDE.md
added: 2026-09-27
closed: 2026-09-27
pr: 1217
payoff: a session told read only stops its own pending merges unasked, so the owner never has to confirm a hold to prevent one
verify: grep -q 'Read only means read only' CLAUDE.md
---

**Problem.** Told read only, a session left its own auto-merge armed and offered a hold instead of disarming it, so PR 1213 merged against the instruction

**Why it matters.** PL-QRBB's capture pull request, `#1213`, was open with
auto-merge armed when the project owner answered "Read only for now". The
session read that as "do not build it", left the merge it had armed to run,
and offered "reply hold and I'll turn off auto-merge" instead of turning it
off. It merged minutes later. The owner, 2026-09-27: "Read only means read
only. I shouldn't have to reconfirm to avoid a merge."

Nothing in the instructions said a read-only instruction reaches writes a
session has already set going, and two standing rules pointed the other way:
the capture rule, and the item-only auto-merge in `CLAUDE.md`'s
commit-and-push bullet. Weighing them against a three-word instruction, the
session resolved the conflict toward the written rules.

**Where.** `CLAUDE.md` § "The queue, and how the project owner works", beside
the commit-and-push bullet the rule overrides.

**Done when.** `CLAUDE.md` carries the rule, resident.

**Routed resident, and nothing cut to pay for it.** It fires on the owner's
message, which no read precedes, so neither a path-scoped rule nor a skill can
carry it; and recognising that a message means read only is judgment, since
the owner's wording varies, which a hook matching the prompt would have to
guess at. No existing resident sentence covers it, so there is nothing it
replaces.
