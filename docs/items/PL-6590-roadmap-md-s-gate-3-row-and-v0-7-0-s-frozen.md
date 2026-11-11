---
id: PL-6590
title: ROADMAP.md's Gate 3 row and v0.7.0's frozen-list heading say the list clears before v0.7.0's implementation begins, but v0.7.0's Required scope closed in v0.6.16 while Gate 3 was still open
priority: P2
effort: S
status: needs-decision
classes: defect, docs
touches: ROADMAP.md
deferred-from: v0.7.0 - the answer decides how a gate orders its work from Gate 4 on, and no displayed value depends on it
added: 2026-11-10
payoff: a reader of the roadmap can tell whether debt must clear before a milestone's features are built, and the record matches what was done
---

**Problem.** ROADMAP.md's Gate 3 row and v0.7.0's frozen-list heading say the list clears before v0.7.0's implementation begins, but v0.7.0's Required scope closed in v0.6.16 while Gate 3 was still open.

**Where.** § "The timeline", row 8 (Gate 3): "Its work ships in `v0.6.x` patches as it clears, before v0.7.0's implementation begins." § "v0.7.0 - the schematic", the frozen list's heading "Cleared before v0.7.0's implementation begins, unless deferred". § "Current baseline" says every id in v0.7.0's Required scope closed in v0.6.16, and that 87 of the gate's 90 entries had cleared then, with the list grown since.

**Why it matters.** A reader deciding what the gate means takes "before implementation begins" as the rule that orders the work. The record shows the work ran the other way, so either the rule was set aside by a decision nobody wrote down, or the rule is stated wrongly. A session reading it later may hold back v0.7.0 work, or treat the gate as advisory, on the wrong ground.

**Done when.** The roadmap says what the gate actually orders for v0.7.0: either the decision that let the Required scope close first, with its date and who took it, or a rule that matches what happened. Whether a gate must clear before implementation is the project owner's to decide if no record holds it.

**Found by** the thread working `PL-PNH2` (the timeline's Size column and ship status), 2026-11-10.

**Decision needed.** Whether Gate 3's second group must clear before v0.7.0's implementation begins, as `ROADMAP.md` says, now that v0.7.0's Required scope closed in v0.6.16 while that group was still open. There are two answers:

1. Keep the rule. Record in the Gate 3 row that v0.7.0's Required scope was worked before the group cleared, with no decision recorded, so the rule binds again from Gate 4.
2. Change the rule to what happened. A gate's second group and the next milestone's Required scope are worked side by side, and the milestone ships when both have cleared.

**Recommendation: 1.** The gate exists so that new work does not outrun the debt already owed. A search of `ROADMAP.md` and the item store on 2026-11-11 found no decision that set the rule aside, so the record shows the rule was not applied, not that it was changed. Writing answer 2 would turn an omission into policy. The choice is the owner's because it sets the order in which debt and new features are worked.

**Generator check.** A one-off: the rule and the work disagreed once. No head's `misread:` states which order a debt gate imposes.
