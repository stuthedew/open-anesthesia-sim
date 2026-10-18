---
id: PL-87H2
title: instruction-writing.md rule 1 says to give 'Phase 1 in detail' while its scope note says never to mention phases; decide which reading is meant (PL-ZKT8 audit flag B10)
priority: P3
effort: S
status: ready
classes: docs
feature: decision-ownership
touches: .claude/rules/instruction-writing.md
deferred-from: v0.6.0 - captured after the freeze, and not safety or science
added: 2026-10-18
payoff: rule 1 and the scope note no longer contradict each other, so a session stops guessing which to break
verify: ! grep -qF 'Phase 1 in detail' .claude/rules/instruction-writing.md
---

**Problem.** instruction-writing.md rule 1 says to give 'Phase 1 in detail' while its scope note says never to mention phases; decide which reading is meant (PL-ZKT8 audit flag B10)

**Why it matters.** Both sentences are resident in every session. Read
literally, rule 1 asks for "Phase 1 in detail" and the scope note forbids the
word "phases" in the output, so a session either breaks one or guesses which
was meant. The `PL-ZKT8` prompt audit flagged it as B10 and left it for a
decision.

**Decided 2026-10-18** (a session's call under rule 14 of
`.claude/rules/instruction-writing.md`: one document's phrasing, and no reader
would prefer either contradiction). The two rules do not conflict in intent.
Rule 1 asks for the structure, an overview of the stages and then the first
stage in detail. The scope note forbids the rules' own vocabulary in the
output. So a stage is named for what it does, never "Phase 1". The fix
rewords rule 1 so it no longer uses the word it forbids.

**Done when.** Rule 1 asks for an overview of the stages and the first stage in
detail without using the word "phase", and the scope note says a stage is named
for what it does.
