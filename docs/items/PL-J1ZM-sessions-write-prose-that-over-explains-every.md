---
id: PL-J1ZM
title: Sessions write prose that over-explains: every writing rule adds something a paragraph must carry (a reason for each value, what changing it would do, the test that holds it, its provenance) and none says what to leave out, so each docs/MODEL.md section needs its own rewrite item and fix branches grow it again
priority: P1
effort: M
status: ready
classes: defect
feature: reader-first-prose
touches: .claude/rules/plain-writing.md, docs/prose-review/prompt.md, docs/prose-review/gold, tools/new_prose.py, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - captured after the freeze; it changes how prose is written, not a displayed value
added: 2026-11-03
payoff: a clinician reading docs/MODEL.md gets what a value means in a few sentences, and fix branches stop growing sections that then need their own rewrite
not-delegable: the approach changes how every session writes and needs a design round with the owner
root-cause-of: PL-BSYT, PL-J37P, PL-9331, PL-PS5H, PL-XBJ3, PL-XT53, PL-YVL0
generator: live - every fix branch to docs/MODEL.md still writes under the additive rules, and PL-ZDZ0 alone added PL-JP8X on 2026-11-03
misread: what a clinician paragraph may leave out, which no rule states, so each writer adds
---

**Problem.** The project owner judged reviewed `docs/MODEL.md` prose "still way over explaining" on 2026-11-03, after `PL-ZDZ0`'s three review rounds, and named the prose process a generator (project owner, 2026-11-03). Each rule a session writes under asks a paragraph to carry one more thing. `.claude/rules/plain-writing.md` asks for each chosen value's purpose, its reason, and what changing it would do. The documentation check asks each numeric paragraph to name its test (`PL-W8FL`). The safety standard asks for provenance and visible limits. No rule says what a reader can do without, and the review can only trim sentences inside the paragraphs a branch changed (`PL-22T5`). So every section needs a rewrite item, and each fix branch grows the section again.

**Why it matters.** `docs/MODEL.md` is what a clinician reads to judge a displayed value, and a meaning buried in explanation is one they miss.

**Evidence.** The MAC passage in § "Displayed precision" was 381 words on `main`. A version that keeps every value the clinician needs, with the derivation and tests in a developer note, is about 110 words. Seven `prose-quality` items are open for sections that need the same cut.

**Recommended, for a design round with the owner.**

1. Put a subtractive rule ahead of the sentence rules. A clinician paragraph says what the reader sees and what it means, and stops. Each reason, derivation, test and piece of history goes to the developer note or the item, or is cut. This replaces the rule asking each value for its purpose, reason and effect of change, which moves to the developer note.
2. Give the writer examples, not only the reviewer. `docs/prose-review/gold/` is empty. Fill it with paragraphs the owner approves, starting with the accepted `PL-ZDZ0` paragraph, and print them to the writing session before it drafts. Check published prompting guidance on examples against rules before building this.
3. Build `PL-W8FL` and `PL-22T5`, and fold `PL-43GT` and `PL-JP8X` into point 1 where they overlap.

**Done when.** A fresh session writing a fix to a `docs/MODEL.md` section produces a passage no longer than the one it replaced, and the owner accepts it on the first read, on three branches in a row.

**Generator check.** This is the head: a generator of the seven section rewrites named in `root-cause-of`, recorded live at the project owner's word (2026-11-03). `PL-W8FL`, `PL-22T5`, `PL-43GT` and `PL-JP8X` are parts of its fix.
