---
id: PL-7RYB
title: PL-JQJQ's brief does not mark its design decision as ratified rather than specified, and nothing sweeps the items closed before that rule landed on 2026-09-16
status: untriaged
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
