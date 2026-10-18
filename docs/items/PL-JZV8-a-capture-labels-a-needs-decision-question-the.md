---
id: PL-JZV8
title: A capture labels a needs-decision question the owner's because it 'reopens' a ratified decision when the answer only extends the mechanism that decision chose (PL-KFNP: refusing a stale cardiac output at the write extends PL-LBQY's guard and chooses neither frozen compartments nor the accepted window), so a design round put an obvious call to the owner, who asked why it was his; the triage and design modes should say that reopening is choosing what a decision was chosen over, and an extension of its mechanism is a session's call (found in PL-KFNP's design round, Stuart 2026-10-12)
priority: P2
effort: S
status: done
classes: docs
feature: decision-ownership
touches: .claude/skills/docket/modes/triage.md, .claude/skills/docket/modes/design.md
added: 2026-10-12
closed: 2026-10-18
pr: 1539
payoff: a capture stops putting an extension of a ratified mechanism to the owner as a reopening, so a design round asks the owner only the questions that are theirs
verify: grep -qi 'extends the mechanism' .claude/skills/docket/modes/triage.md
---

**Problem.** A capture labels a needs-decision question the owner's because it 'reopens' a ratified decision when the answer only extends the mechanism that decision chose (PL-KFNP: refusing a stale cardiac output at the write extends PL-LBQY's guard and chooses neither frozen compartments nor the accepted window), so a design round put an obvious call to the owner, who asked why it was his; the triage and design modes should say that reopening is choosing what a decision was chosen over, and an extension of its mechanism is a session's call (found in PL-KFNP's design round, Stuart 2026-10-12)

**Checked 2026-10-17: not landed.** Neither
`.claude/skills/docket/modes/triage.md` nor `.claude/skills/docket/modes/design.md`
says what reopening a ratified decision is: `grep -niE "extension of|extends?
(the|its) mechanism|reopen"` over both and `CLAUDE.md` finds only `CLAUDE.md`
§ "Working with the project owner"'s bars to reopen ("Reopen a ratified
decision on ordinary evidence", "Reopen a specified one only on a compelling
argument"), which say *when* a decision may be reopened and never what counts
as reopening one. The only commit to either file since 2026-10-12 is
`d296a4ec` (#1441), which is unrelated. `PL-KFNP`'s "**Answered 2026-10-12**"
records the owner asking why the question was theirs and names this item as the
fix, so the edit owed under `CLAUDE.md`'s behaviour-change rule was never made.

**Why it matters.** A capture that reads "touches a ratified decision" as
"reopens it" hands the owner a question with one clearly correct answer, which
`.claude/rules/instruction-writing.md` rule 14 says is never offered, and it
does so with the authority of the reopening bar behind it - so the next design
round makes the same call. Each costs the owner a decision they have said they do
not want to spend attention on, and a round that waits on them.

**Done when.** triage.md's paragraph opening "And `needs-decision` says the
next step is a decision, never whose" says, once, that reopening a decision
means choosing one of the alternatives it was recorded as chosen over (the
clause `CLAUDE.md` requires every ratified record to carry), and that an
answer which extends the chosen mechanism - a further site, a further field,
the same guard applied at a new write - chooses none of them and is a
session's call, with `PL-KFNP` as the worked example. design.md step 4, which
already cites that paragraph for the sort, points at it rather than restating
it, so the rule has one home.

**Under the generator pause.** Not a new workflow mechanism: it adds no
command, check or field, only a sentence defining a term the existing
reopening bars and rule 14's sort already use. The owner raised it in
`PL-KFNP`'s round, which also lifts the pause for this request by
`CLAUDE.md`'s own terms; and under the product-focus paragraph it blocks no
product item, so it is queued for the coordinator rather than worked in a
product session.

**Generator check.** Work the owner asked for. The fact misread is whose a
`needs-decision` question is; no head's `misread:` states it
(`bin/docket generators --misread`, 2026-10-17), and its earlier corrections -
rule 14's consequence test (2026-09-19, `PL-HGN6`, `PL-C4RS`) and its
one-clear-option clause (2026-09-27) - were each a sharpening of the same
prose rather than a fix this item re-enters, so `reenters:` is not set.
