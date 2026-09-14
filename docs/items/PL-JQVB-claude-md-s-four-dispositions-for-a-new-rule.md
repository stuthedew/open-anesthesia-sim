---
id: PL-JQVB
title: CLAUDE.md's four dispositions for a new rule list no carrier for a paste-able brief or an agent definition, and a skill's resident cost is invisible to measure_resident
priority: P3
effort: S
status: done
classes: session-cost, docs
touches: tools/doc_check.py, tests/unit/test_doc_check.py, docs/resident-instructions.md
added: 2026-09-05
closed: 2026-09-14
pr: 558
verify: python3 tools/doc_check.py check | grep -q 'instructions loaded on demand:' && grep -q 'def test_a_rule_routed_into_a_skill_moves_both_totals' tests/unit/test_doc_check.py
---

**Problem.** `CLAUDE.md`'s four dispositions for a new rule — a check, a
skill, a path-scoped rule, or resident — name no carrier for two things this
repository already uses: a paste-able brief handed to a fresh session, and an
agent definition. Separately, `check_resident_instructions` measures `CLAUDE.md`
and `.claude/rules/`, so a rule moved into a skill leaves the measured set
entirely and reads as a pure reduction when it is a relocation.

**Why it matters.** The dispositions are the routing rule every behaviour
change passes through, and `CLAUDE.md` says a rule landing in none of the four
"has been lost". A carrier in live use that the list does not name forces a
session either to file the rule under a disposition that does not fit or to
leave it resident by default — and resident-by-default is the outcome the list
exists to prevent. The measurement gap compounds it: the cheapest way to make
the growth advisory go quiet is the one move it cannot see.

**Where.** `CLAUDE.md`, the four dispositions under the behaviour-change rule;
`tools/doc_check.py`, `check_resident_instructions` and what it reads.

**Decision needed.** Two questions, separable. Whether the disposition list gains
entries for a brief and an agent definition, or whether those are deliberately
not carriers for a *rule* and the list is right as it stands. And whether
skills enter the measured set — which changes what the number means, from "text
every session loads" to "text a session may be made to load", rather than
merely widening its scope.

**Done when.** Both questions have a recorded answer, and either `CLAUDE.md`
and the measurement reflect it or `docs/resident-instructions.md` records why
they do not.

## Worked 2026-09-14: one question answered no, the other answered by a number nobody had counted

**Q1 — does the disposition list gain a brief and an agent definition? No, and
`CLAUDE.md` is unchanged.** The four dispositions route a **rule**: text that
binds a session whether or not anyone remembers to supply it. Neither candidate
is one.

`docs/consultant-brief.md` reaches a session only when the project owner pastes
it, so a rule routed there binds the sessions they happen to paste it into and
no others. That is not a weakness to be fixed — it is the property the brief was
built for. `PL-1H3H` chose a pasted user message over a skill on three counts it
verified rather than argued, and the second is decisive here: a consultant
reviewing the apparatus would otherwise load, by opening the thing under review,
`.claude/rules/apparatus-standard.md` telling it that tree is not worth
reviewing. A carrier for a *pass*, not for a rule.

An agent definition is not in live use at all — this tree holds none — and
`PL-1H3H` records why the one considered was refused: a subagent returns a
summary and cannot hold a conversation, and a custom agent inherits the whole
`CLAUDE.md` hierarchy anyway. So the brief's premise that both are "carriers in
live use that the list does not name" is half right: one is in live use and is
not a carrier; the other is neither.

Recorded in `docs/resident-instructions.md` § "What is not a carrier, and why
the list stays at four", which is where this item's own **Done when** sends a
no. Nothing resident changed, which is the point — the alternative was two more
entries on the routing list for carriers that cannot carry.

**Q2 — do skills enter the measured set? Not the same number, but they are
measured, on a second line.** The question the brief poses — whether admitting
them changes the number's meaning from "text every session loads" to "text a
session may be made to load" — answers itself: those are two quantities, and one
total cannot mean both. A skill that is never invoked costs a session nothing,
and a rule scoped to `src/**` costs a workflow session nothing, so a combined
figure would overstate every session and describe none.

**The count that settled it, which is the half this brief could not have.**
Measured from the tags, `v0.4.0` to `v0.4.22`:

| file | v0.4.0 | v0.4.22 | growth | seen by the advisory |
| --- | --- | --- | --- | --- |
| `CLAUDE.md` | 29,675 | 32,810 | +3,135 | yes |
| `.claude/skills/docket/SKILL.md` | 54,352 | 69,768 | +15,416 | no |
| `docs/worker.md` | 12,877 | 13,579 | +702 | no |

19,253 characters of instruction text were added over twenty-two patch
releases and the growth instrument reported 3,135 of them — **16%**. Over the
last two releases it reported none: `CLAUDE.md` has not moved since `v0.4.18`
while the skill gained 1,729. This is not a hypothetical blind spot; it is where
four fifths of the growth actually went. Measured today, the two sets stand at
50,570 resident characters against 113,203 reachable on demand.

**What was built.** `tools/doc_check.py` gains `measure_on_demand`,
`check_on_demand_instructions` and a second report line covering
`.claude/skills/**`, the path-scoped `.claude/rules/*.md` and `docs/worker.md`.
`_resident_baseline` was generalised to `_baseline(root, roots, measure)` so
both sets are read from the same git walk at the same ref — a second copy of
that walk would have been free to drift from the first.

**No advisory, deliberately, and this is the part that had to be got right.**
Routing a rule into a skill is disposition 2 — the *preferred* answer to the
growth advisory. A signal that fired when one happened would fire on the project
doing the right thing, which is exactly the check `CLAUDE.md` calls a defect in
the check. What was missing was never a verdict but a number: the growth
advisory reads one set, a routing pass moves text into the other, and the move
appeared as a reduction with nothing on the far side of it. Printing both totals
is the whole fix.

**Six tests**, each one a defect the absence would let through rather than a
getter: a skill is measured on demand and never as resident; a rule lands in
exactly one of the two sets (double-counting fails nothing, so only a test says
whether the two lines can be read side by side); `docs/worker.md` is on demand;
an empty tree reports nothing; a rule routed out of `CLAUDE.md` into a skill
moves **both** totals, which is the blind spot itself; and the real tree is
measured, so the `docket` skill's own 69,530 characters are pinned as the text
this was built for.
