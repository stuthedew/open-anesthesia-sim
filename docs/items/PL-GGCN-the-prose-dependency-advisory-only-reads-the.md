---
id: PL-GGCN
title: The prose-dependency advisory only reads the first id in a compound prerequisite, so 'blocked on A and on B' leaves B undeclared and unreported
status: untriaged
added: 2026-09-05
---
**Problem.** `PROSE_DEPENDENCY` (`subprojects/docket/src/docket/checks.py:824`)
requires a cue word from `PREREQUISITE_CUES` within 40 characters of the id,
and its character class excludes `(`, `)`, `.`, `;`, `:` and `—`. So in a
sentence naming two prerequisites off one cue, only the first is ever checked.

**The live instance.** `PL-VZL0` (cite MODEL.md from every `core/` function
implementing a governing equation) line 69 reads:

that line names two prerequisites off a single cue word — first `PL-GS5X`,
then, past a parenthetical, `PL-X2XX`. Read it in the file rather than here:
quoting it verbatim makes *this* item trip the same advisory on the same first
id, which is a neat confirmation and a warning that then fires forever, so the
wording is described instead of reproduced.

`blocked-by` declares `PL-GS5X` alone. `PL-X2XX` is open (`ready`), is a real
prerequisite - without it the citations `PL-VZL0` adds are unenforced prose and
a section rename orphans every one of them - and **no advisory fires**. The
first id is skipped by `other in item.blocked_by`; the second never matches the
cue at all.

**Why it matters.** This is `CLAUDE.md`'s first escalation test exactly: a check
passes while the guarantee it stands for is void. `PL-ZBRB` built this advisory
so that a prose prerequisite could not stay invisible to `docket next`, and the
compound form - which is how a brief naturally states two blockers - is the one
shape it does not see. `docket next` will offer `PL-VZL0` as soon as `PL-GS5X`
closes, stating a sound-looking reason for an order that is wrong.

**Where.** `subprojects/docket/src/docket/checks.py:824` (`PROSE_DEPENDENCY`),
`_check_prose_dependencies` at `:830`.

**Approach.** After a cue matches, keep scanning the same sentence for further
ids rather than stopping at the first - a second pass over the remainder of the
clause, or a cue that may be followed by a list. Do not widen the character
class to swallow parentheticals: that trades this false negative for false
positives, which `PL-B2NS` already paid for once in `doc_check candidates`.

**Done when.** A brief saying "blocked on A and on B" with only A declared
raises the advisory for B, and `PL-VZL0`'s missing `PL-X2XX` edge is reported.
