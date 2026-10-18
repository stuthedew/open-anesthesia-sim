---
id: PL-9KGT
title: triage.md's reply rule escalates only a P0 or a compounding-friction finding, 'nothing else', and omits the fresh-session ending CLAUDE.md requires for a live generator or an impairs-generators item (PL-ZKT8 audit flag E4)
priority: P2
effort: S
status: done
classes: docs, defect
milestone: v0.5.28
touches: .claude/skills/docket/modes/triage.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-10-18
closed: 2026-10-18
pr: 1545
payoff: a triage pass that finds a ranking generator ends its reply with the prompt that starts it, so the head is not left to wait for its band
verify: grep -qF 'ranking generator' .claude/skills/docket/modes/triage.md
---

**Problem.** triage.md's reply rule escalates only a P0 or a compounding-friction finding, 'nothing else', and omits the fresh-session ending CLAUDE.md requires for a live generator or an impairs-generators item (PL-ZKT8 audit flag E4)

**Why it matters.** `CLAUDE.md` says a ranking generator, a head recorded
`generator: live` or an item recorded `impairs-generators:`, takes one of two
endings: fix it in this session, or end the reply with a ready-to-paste prompt
for a fresh one. triage.md's "Escalate only a `P0` or a compounding-friction
finding" names neither kind, so a triage pass that finds one escalates nothing
and the head waits for its band. The `PL-ZKT8` prompt audit flagged it as E4.

**Done when.** triage.md's escalation paragraph names a ranking generator and an
`impairs-generators:` item beside a `P0` and compounding friction, and says a
triage pass gives it the prompt ending, since the pass is not the fix.
