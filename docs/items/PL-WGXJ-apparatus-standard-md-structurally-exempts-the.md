---
id: PL-WGXJ
title: apparatus-standard.md structurally exempts the apparatus from the expert-review standard, so the largest part of the tree has no review bar
priority: P2
effort: S
status: needs-decision
classes: planning, docs
touches: .claude/rules/apparatus-standard.md, .claude/rules/expert-review.md
added: 2026-09-05
---
**Problem.** `.claude/rules/apparatus-standard.md` sets a deliberately
lower bar for `subprojects/docket/`, `tools/`, `.claude/`, `docs/worker.md` and
`CLAUDE.md`, and `.claude/rules/expert-review.md` scopes the specialist
standard to the simulator. Between them the apparatus — by file count the
larger part of the tree — is *exempt* from the expert-review standard rather
than held to a different one.

**Why it matters.** The inequality is deliberate and `PL-6SBB` is what the
mirror error cost, so this is not an argument for one standard. It is that
"lower" was never given a floor. The apparatus now decides what every session
works on, what it is held to, and what a release contains, so a defect in it
gives a wrong answer silently in a way a defect in a helper script does not —
`PL-NBCS` (docket next reads a scope exclusion as membership) and `PL-KD98`
(wave reports implement for a completed scope), both open, are exactly that. A
bar stated only as "not the specialist one" cannot refuse anything.

**Where.** `.claude/rules/apparatus-standard.md`;
`.claude/rules/expert-review.md`, its scope paragraph.

**Decision needed.** Whether the apparatus standard gains a floor of its own —
and if so whether it covers all of it, or only the parts a session reads
answers from, which is a narrower and more defensible line than the path list.
The alternative is that the wording is right as it stands and the two open
defects above are ordinary bugs rather than evidence of a missing bar.

**Done when.** The question has a recorded answer, and
`.claude/rules/apparatus-standard.md` either states the floor or records why it
has none.
