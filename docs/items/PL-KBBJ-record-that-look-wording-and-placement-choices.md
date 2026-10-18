---
id: PL-KBBJ
title: Record that look, wording and placement choices are placeholders while structure and function are built, so sessions decide them rather than putting them to the owner
priority: P2
effort: S
status: done
classes: planning
feature: owner-attention
milestone: v0.5.29
touches: .claude/rules/instruction-writing.md
added: 2026-10-18
closed: 2026-10-18
pr: 1589
payoff: a session decides a look, wording or placement call itself and records it as a placeholder, so the owner is not asked about styling while the structure is being built
verify: grep -q 'Look, wording and placement are not among them for now' .claude/rules/instruction-writing.md
---

**Problem.** `.claude/rules/instruction-writing.md` rule 14 makes "behavior a
learner would see" one of the owner's questions. Read literally, that sends
every choice of look, wording or placement to the owner as a card. On
2026-10-18 the owner answered such a card on `PL-NWTM` (where the delivered
concentration and the 1 MAC divisor go on the readout heading) with "Agree with
recs but to be honest, I'm not really focusing on [a]esthetics now so all of
these type of aesthetic decisions are meant to be place holders for now while
[I] develop the structure and function" (project thread, 17:40 UTC).

**Why it matters.** Every later session reads rule 14, not that thread. Until
the rule says so, the next styling call goes to the owner as a card again.
`CLAUDE.md` says a change to how sessions work takes effect in the session that
asks for it.

**Done when.** Rule 14 says that look, wording and placement are the session's
to decide for now, recorded as a placeholder. It also says that a choice which
decides whether a value the safety-critical standard requires is on screen,
readable or correctly labelled stays the owner's.

**Where it goes.** Rule 14 is the one place that sorts which questions are the
owner's, and `.claude/skills/docket/modes/design.md` step 4 points at it rather
than restating the test, so one sentence there covers both. It is resident
because the moment it governs is a reply, which no read comes before. Nothing
in the resident set can be cut to pay for it: the sentence narrows an existing
list rather than repeating one held elsewhere.

**Conflict noted.** The new instruction narrows "behavior a learner would see"
rather than contradicting it. Structure and function stay the owner's, and so
does anything the safety-critical standard reaches.
