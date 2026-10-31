---
id: PL-3XP7
title: The model-review skill's description names only the monthly review, so an ad hoc request to analyse what the blind review passes caught does not load the skill that runs tools/blind_review_report.py; add that trigger to its description
priority: P3
effort: S
status: ready
classes: defect
touches: .claude/skills/model-review/SKILL.md
deferred-from: v0.7.0 - captured after the freeze; a skill description in the workflow lane, not safety or science
added: 2026-10-26
payoff: a request to analyse what the blind review passes caught loads the procedure for counting them, instead of a session reinventing the method
verify: grep -qE '^description:.*blind review' .claude/skills/model-review/SKILL.md
---

**Problem.** The model-review skill's description names only the monthly review, so an ad hoc request to analyse what the blind review passes caught does not load the skill that runs tools/blind_review_report.py; add that trigger to its description

**Checked 2026-10-31.** The `description:` line of `.claude/skills/model-review/SKILL.md` names the monthly review, an owner-started run and a generator or cluster. It does not mention the blind review passes or `tools/blind_review_report.py`, although § "Check that each blind review pass still finds faults" holds that procedure.

**Why it matters.** A harness loads a skill from its description. So a request to analyse what the blind review passes caught starts without the procedure that says how to count them, where to write the result and what bar to compare it against. That session then reconstructs the method or skips it.

**Done when.** The description names an ad hoc analysis of what the blind review passes caught as a trigger. It stays one sentence.

**Generator check.** A one-off. The fact is which requests a skill's description routes to it. No head's `misread:` states it, and this is the only open item about a skill's trigger.
