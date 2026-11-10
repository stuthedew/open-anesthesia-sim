---
id: PL-6590
title: ROADMAP.md's Gate 3 row and v0.7.0's frozen-list heading say the list clears before v0.7.0's implementation begins, but v0.7.0's Required scope closed in v0.6.16 while Gate 3 was still open
status: untriaged
added: 2026-11-10
---

**Problem.** ROADMAP.md's Gate 3 row and v0.7.0's frozen-list heading say the list clears before v0.7.0's implementation begins, but v0.7.0's Required scope closed in v0.6.16 while Gate 3 was still open.

**Where.** § "The timeline", row 8 (Gate 3): "Its work ships in `v0.6.x` patches as it clears, before v0.7.0's implementation begins." § "v0.7.0 - the schematic", the frozen list's heading "Cleared before v0.7.0's implementation begins, unless deferred". § "Current baseline" says every id in v0.7.0's Required scope closed in v0.6.16, and that 87 of the gate's 90 entries had cleared then, with the list grown since.

**Why it matters.** A reader deciding what the gate means takes "before implementation begins" as the rule that orders the work. The record shows the work ran the other way, so either the rule was set aside by a decision nobody wrote down, or the rule is stated wrongly. A session reading it later may hold back v0.7.0 work, or treat the gate as advisory, on the wrong ground.

**Done when.** The roadmap says what the gate actually orders for v0.7.0: either the decision that let the Required scope close first, with its date and who took it, or a rule that matches what happened. Whether a gate must clear before implementation is the project owner's to decide if no record holds it.

**Found by** the thread working `PL-PNH2` (the timeline's Size column and ship status), 2026-11-10.
