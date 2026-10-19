---
id: PL-6XZG
title: Record the owner's 2026-10-19 decision to keep apparatus sessions at high effort as their own judgement, replacing the ratified 2026-10-17 record whose reason was cost
priority: P2
effort: S
status: done
classes: session-cost
feature: model-evidence
touches: docs/maintainer.md, .claude/rules/apparatus-standard.md
added: 2026-10-19
closed: 2026-10-19
payoff: a later session reads apparatus effort as the owner's own call, not a cost trade it should reopen or copy
verify: grep -q 'PL-6XZG' docs/maintainer.md && grep -q 'PL-6XZG' .claude/rules/apparatus-standard.md
---

**Problem.** Record the owner's 2026-10-19 decision to keep apparatus sessions at high effort as their own judgement, replacing the ratified 2026-10-17 record whose reason was cost

The owner asked on 2026-10-19 whether apparatus sessions should move from
`high` to `xhigh` or `max` effort, since their rule that cost never justifies
a lower setting removed the only reason recorded for `high`. Their answer:
keep `high` for now, as their own judgement that the marginal benefit of
`xhigh` is small (project owner, 2026-10-19). The evidence they weighed: on
Opus 5.5, `xhigh` solved 96.7% of a SWE-bench Pro subset against 95.3% at
`high`, and 91.1% of an internal agentic-coding set against 88.4%. No `max`
figure is published (Anthropic, *Optimizing for cost and intelligence*, read
2026-10-19).

**Generator check.** A one-off record of an owner decision, not a member of a head.
