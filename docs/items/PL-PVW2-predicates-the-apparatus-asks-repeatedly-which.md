---
id: PL-PVW2
title: Predicates the apparatus asks repeatedly - which ids a subject leads with, which files a branch changed, the pull-request number, the origin slug, the default ref, captures-only, how a shell command splits - are spelled again wherever they are needed, and the spellings disagree
status: untriaged
feature: one-answer
touches: subprojects/docket/src/docket/vcs.py, tools/generator_check.py, tools/pr_body_check.py, tools/open_pull_requests.py
added: 2026-09-25
root-cause-of: PL-KR69, PL-YYDT, PL-2TV9, PL-GNCB, PL-0JGZ, PL-BBV7, PL-6P0F
generator: live - PL-FFR0 closed one on 2026-09-25 and the audit the same day reproduced seven more disagreeing pairs; each new tool copies whichever spelling it finds
misread: Which spelling of a repeated predicate is the answer, when tools, hooks and docket each spell it
---

**Problem.** Predicates the apparatus asks repeatedly - which ids a subject leads with, which files a branch changed, the pull-request number, the origin slug, the default ref, captures-only, how a shell command splits - are spelled again wherever they are needed, and the spellings disagree

The audit enumerated the questions the apparatus asks and found every implementation. Nine questions have two or more that disagree on a constructed input, one of them on the protected-path audit (PL-KR69). Four questions are already single-sourced (who holds an item, gate parity, canonical form, item id grammar) and have produced no disagreement since - which is the evidence that consolidation holds.

**Why it matters.** The members are one mechanism; fixed one at a time, each fix leaves the mechanism in place to hand over the next.

**Done when.** Each listed question has one implementation that every caller imports, with `tools/` importing `subprojects/docket/src` as `branch_id_check` already does; a test per question holds the disagreeing input.

Evidence: `docs/stress-2026-09-25/evidence.tar.gz` (PL-P0FP).
