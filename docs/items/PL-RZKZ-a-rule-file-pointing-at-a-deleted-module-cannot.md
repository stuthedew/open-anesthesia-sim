---
id: PL-RZKZ
title: A rule file pointing at a deleted module cannot cite it by path, and nothing warns the writer before doc_check refuses the draft: citation-drift.md is scoped to docs/items, WORKING_NOTES and skills, so a session writing .claude/rules never loads the rule that would tell it to route the pointer through the item instead
priority: P3
effort: S
status: ready
classes: docs, infra
touches: .claude/rules/citation-drift.md, tests/unit/test_rules_paths_check.py
added: 2026-09-21
payoff: a session writing a rules file is told how to cite a moving target before doc_check refuses the finished draft
verify: grep -qF '/.claude/rules/**' .claude/rules/citation-drift.md
---

**Problem.** A rule file pointing at a deleted module cannot cite it by path, and nothing warns the writer before doc_check refuses the draft: citation-drift.md is scoped to docs/items, WORKING_NOTES and skills, so a session writing .claude/rules never loads the rule that would tell it to route the pointer through the item instead

**Measured 2026-09-21.** `.claude/rules/citation-drift.md` carries three `paths:`
entries - the queue directory, the working notes, and the skills tree - and
nothing matching `.claude/rules/`. So the rule that decides when a drifted
citation is a finding does not load for a session writing the rules themselves.

**Why it matters.** The rules tree is where this project puts the statements
that survive longest and are read by the most sessions, which is exactly where a
pointer at a deleted module is most expensive. The failure is also the worst
shape available: nothing warns while the draft is being written, and `doc_check`
refuses the finished file at commit time with a message about a path that does
not exist, so the writer learns the constraint by having the work rejected
rather than by being told. A rule whose own tree is outside its scope is also the
kind of gap nothing else will catch, since no check reads a frontmatter list for
completeness.

**Done when.** A session editing a file under `.claude/rules/` loads
`citation-drift.md`, and the rule's own frontmatter says so.
