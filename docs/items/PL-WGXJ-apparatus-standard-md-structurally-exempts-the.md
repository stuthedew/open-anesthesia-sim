---
id: PL-WGXJ
title: apparatus-standard.md structurally exempts the apparatus from the expert-review standard, so the largest part of the tree has no review bar
priority: P2
effort: S
status: done
classes: planning, docs
milestone: v0.4.23
touches: .claude/rules/apparatus-standard.md
added: 2026-09-05
closed: 2026-09-14
pr: 558
verify: grep -q 'The floor: an answer has to be true' .claude/rules/apparatus-standard.md
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

## Worked 2026-09-14: yes to a floor, on the narrow line, and the property was chosen by counting

**Decided: the apparatus standard gains a floor, and it binds the
answer-giving surface rather than the path list.** Added to
`.claude/rules/apparatus-standard.md` as § "The floor: an answer has to be
true, or has to say it could not answer". `.claude/rules/expert-review.md` is
unchanged and its scope paragraph is still correct, so this item's `touches`
was narrowed to the one file that moved.

**The floor.** What the apparatus tells a session must be true, or must say
what it could not read. A partial reading handed over as a complete one is the
violation, because at the point of use the two are indistinguishable.

**Why the narrow line.** The brief offered it as the more defensible of the two
and it is, for the reason the brief itself gives against the current wording: a
bar stated over everything refuses nothing in particular. A formatter, a
fixture and a Makefile target have no answer to get wrong; `bin/docket`'s
output, the digest, a check's report and an item brief's claim about the tree
all do, and the consequence of getting one wrong is not symmetric with an ugly
line.

**The property was chosen by counting rather than by argument.** Of the 41 open
apparatus-only `defect` items today, about 35 describe a command, check or
brief handing a session a confident answer that is wrong or incomplete. That is
a reading of their titles rather than a script's count and is recorded in the
rule as an order of magnitude, not a statistic — but the four clear exceptions
name themselves: `PL-7QKY` (a circular instruction), `PL-BHVM` (nineteen items
re-deciding one thing), `PL-MSFB` (a stale workaround), `PL-YTDN` (renames).
A floor aimed anywhere else would be aimed away from the defect load.

**The strongest justification is one the brief did not have, and it is
measured.** `docket check` is what pins `safety`- and `science`-classed work to
`P1`. `PL-MVC2` records a class misspelt as `safey`: it matched no rule, so work
a clinician could be misled by stayed seatable in the bottom band and the check
reported zero errors. The apparatus decides which safety work a session is
offered, so a silent wrong answer here defers safety work without anyone having
decided to. That is the line from an apparatus defect to the simulator's own
standard, and it is a real instance rather than a construction.

**The brief's two cited defects have both closed since it was written** —
`PL-NBCS` and `PL-KD98` are `done`. The evidence was not withdrawn with them:
the count above replaces two instances with the whole open set, which is the
stronger form of the same claim.

**What the floor deliberately does not do.** It asks for no polish, no coverage
target, no abstraction and no prose, so it is not the specialist standard
arriving by another door and cannot be quoted as one — which is the failure
`PL-6SBB` cost, running the other way. Writing it down cost nothing in
behaviour, because the code already holds to it: `FlightReport.unreadable`,
`PullRequestHistory.declined` and `doc_check`'s `Report.declined` exist so that
what went unread travels with the answer. The floor is the rule those three
were already instances of, said once where a session can be refused by it.

**Zero resident characters.** `apparatus-standard.md` is path-scoped, so the
floor loads when a session opens an apparatus path — which is the moment it
governs. Its 2,606 characters are now visible in `doc_check`'s new on-demand
line, which is `PL-JQVB` in the same batch working on its first use.
