---
id: PL-7RYB
title: PL-JQJQ's brief does not mark its design decision as ratified rather than specified, and nothing sweeps the items closed before that rule landed on 2026-09-16
priority: P2
effort: S
status: needs-decision
classes: docs, planning
feature: queue-hygiene
touches: docs/items
added: 2026-09-16
---

**Problem.** `CLAUDE.md` gained the ratified-versus-specified rule on
2026-09-16: a decision taken on a session's recommendation is written
`(project owner, DATE, ratified)` and names in one clause what it was chosen
over, so a later session can tell a design the owner authored from one they
nodded at, and so the two carry different bars to reopen.

`PL-JQJQ` closed hours before that rule landed and is a clean instance of what
it governs. The owner proposed pointing the system `python3` at 3.14; the
session refused it and recommended the `PreToolUse` guard hook; the owner
replied "Agree with recs". That is ratification, not specification, and the
brief does not say so - it records the rejected mechanism and the reasoning at
length, which is the harder half, but not the one word that sets the bar for
reopening it.

**The general half, which is the reason this is an item rather than a
one-line edit.** Every decision recorded before 2026-09-16 carries the plain
form or no marker at all, so the absence of `ratified` currently means
"specified" and "closed before the rule existed" indistinguishably. That is
the rule reading backwards as the opposite of what it says. Whether to sweep,
how far back, and whether an unmarked pre-rule decision should instead be read
as unknown are the questions to answer; a blanket retro-marking would be a
session asserting what the owner meant on decisions nobody can now reconstruct.

**Where.** `docs/items/PL-JQJQ-a-bare-python3-here-is-the-3-11-tools-floor-so.md`
for the concrete instance. The general half touches whatever the sweep decides,
and may be answerable by a check: whether a closed item's brief carries a
decision marker at all is decidable by reading the file, though which kind it
should be is not - that is the judgment half `CLAUDE.md` says not to script.

**Why it matters.** It is small but it fails in the direction that costs: the
bar to reopen a ratified decision is ordinary evidence, and the bar for a
specified one is a compelling argument. A session reading `PL-JQJQ` today would
apply the higher bar to a decision the owner nodded at, which is exactly the
confusion the new rule was written to remove.

**Found** while working `PL-FBXP` (the seven owed pull request numbers), when
the re-read `CLAUDE.md` showed the rule had landed mid-session.

**Done when.** `PL-JQJQ`'s brief marks its decision `(project owner, 2026-09-16,
ratified)` with the clause naming the `python3`-at-3.14 route it was chosen over,
and the general question below has an answer recorded - whichever way it goes - so
that the absence of a marker on a pre-2026-09-16 decision means one thing rather
than two.

**Decision needed.** How should a decision recorded *before* 2026-09-16 be read?
`CLAUDE.md`'s rule gives the plain form the meaning "specified", which carries the
higher bar to reopen, so every decision already in the store now reads as
specified whether it was or not. Three dispositions, and the choice is the project
owner's because it is about what their own past decisions meant:

1. **Read an unmarked pre-rule decision as unknown** and mark it so. Honest, and
   it requires a session to assert nothing it cannot know.
2. **Sweep and mark each one** from the reasoning recorded in its brief. The most
   useful and the least safe - a session asserting what the owner meant on
   decisions nobody can now reconstruct.
3. **Leave them and apply the rule forward only**, accepting that every pre-rule
   decision carries the higher bar by default.

The concrete half is not open in the same way and does not wait on this:
`PL-JQJQ`'s exchange is on record - "Agree with recs" to a session's
recommendation - so it is ratified under any of the three, and marking it is this
item's first edit.
