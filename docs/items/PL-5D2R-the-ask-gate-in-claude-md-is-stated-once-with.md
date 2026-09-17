---
id: PL-5D2R
title: The ask-gate in CLAUDE.md is stated once with emphasis and released four times without it, which is the contradiction shape Anthropic documents as resolved arbitrarily
priority: P2
effort: S
status: done
classes: defect, session-cost
milestone: v0.4.26
touches: CLAUDE.md, docs/resident-instructions.md
added: 2026-09-16
closed: 2026-09-16
pr: 622
verify: grep -qF 'The gate has one trigger and no others' CLAUDE.md && grep -qF 'gate-scope bullet in that section was added' docs/resident-instructions.md && python3 tools/doc_check.py check
---

**Problem.** `CLAUDE.md`'s stop-and-wait gate is stated once, bolded, at line
66. The cases that release it are stated four times and never emphasised: "a
note, not a gate" (line 96), decomposition "rather than handing the question
back" (line 246), "do not ask whether to record it" (line 254), and "do not ask
first" on a pull request (line 343) — spread across 250 lines, each inside a
bullet whose subject is something else. `.claude/rules/instruction-writing.md`
rule 14's "three honest dispositions ... all yours to pick, not the reader's"
is a fifth, in the other resident file, two thirds of the way into a rule that
is 67% of it.

A session retaining one sentence of that section retains the bolded one. Claude
Code's documentation names the outcome: "if two rules contradict each other,
Claude may pick one arbitrarily"
([memory](https://code.claude.com/docs/en/memory)).

**Reported.** The project owner, 2026-09-16: "Offering me decisions you
shouldn't based on claude.md." The predicted failure, observed.

**Fixed in this session.** A gate-scope bullet now sits immediately after the
stop-and-wait bullet, naming the one trigger and listing the five releases with
where each is settled. It restates no rule. 683 characters; recorded in
`docs/resident-instructions.md` § "What stays resident, and on what argument".

**Method, for the next time this is suspected.** Grep the emphasised rule,
grep its releases, and compare the distance between them in lines. An
emphasised rule whose exceptions live more than a screen away, unemphasised, is
the shape that fails; co-locating them costs less than the decision it saves.
