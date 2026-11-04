---
id: PL-J1ZM
title: Sessions write prose that over-explains, in every kind of text they write: each writing rule adds something a text must carry (a reason for each value, what changing it would do, the test that holds it, its provenance) and none says what the reader can do without, so docs, docstrings, the interface, item briefs, pull requests and replies each need rewrites, and each later change grows them again
priority: P1
effort: M
status: ready
classes: defect
feature: reader-first-prose
touches: .claude/rules/plain-writing.md, .claude/rules/instruction-writing.md, docs/prose-review/prompt.md, docs/prose-review/gold, tools/new_prose.py, .claude/skills/docket/modes/close-out.md
deferred-from: v0.7.0 - captured after the freeze; it changes how prose is written, not a displayed value
added: 2026-11-03
payoff: every reader, from a clinician in docs/MODEL.md to the owner reading a reply, gets the point in a few sentences, and changes stop growing text that then needs its own rewrite
not-delegable: the approach changes how every session writes and needs a design round with the owner
root-cause-of: PL-BSYT, PL-J37P, PL-9331, PL-PS5H, PL-XBJ3, PL-XT53, PL-YVL0, PL-QS9H, PL-TPS7, PL-1K5X, PL-FDMJ, PL-VGDX, PL-K7N7, PL-2K0K
generator: live - every session still writes all its prose under the additive rules; PL-ZDZ0 alone added PL-JP8X on 2026-11-03
misread: what a reader can do without, which no rule states for any kind of text, so each writer adds
---

**Problem.** The project owner judged reviewed prose "still way over explaining" on 2026-11-03, and named the prose process one generator across every kind of text (project owner, 2026-11-03). `.claude/rules/plain-writing.md` governs all of it: docs, docstrings, comments, interface text, item briefs, commit messages, pull requests and replies. Each rule there, and in the documents around it, asks a text to carry one more thing: each chosen value's purpose, reason and effect of change; the test that holds a figure (`PL-W8FL`); provenance; visible limits; the reasoning behind a decision. No rule says what the reader can do without, and the review can only trim sentences inside the units a branch changed (`PL-22T5`). So each kind of text has needed its own rewrite item, listed in `root-cause-of`, and each later change grows it again. The resident instructions show it too: 8,903 characters at inception, 95,077 on 2026-11-03.

**Why it matters.** A clinician reads `docs/MODEL.md` and the interface to judge a displayed value, and the owner reads replies and briefs to decide. A point buried in explanation is one they miss.

**Evidence.** One instance: the MAC passage in § "Displayed precision" was 381 words on `main`. A version that keeps every value the clinician needs, with the derivation and tests in a developer note, is about 110 words. Seven `prose-quality` items are open for sections that need the same cut.

**Recommended, for a design round with the owner.**

1. Put a subtractive rule ahead of the sentence rules, for every kind of text. Say what the reader needs to act on, and stop. In `docs/MODEL.md` that is what the clinician sees and what it means. Each reason, derivation, test and piece of history goes to the developer note or the item, or is cut. This replaces the rule asking each value for its purpose, reason and effect of change, which moves to the developer note.
2. Give the writer examples, not only the reviewer. `docs/prose-review/gold/` is empty. Fill it with paragraphs the owner approves, starting with the accepted `PL-ZDZ0` paragraph, and print them to the writing session before it drafts. Check published prompting guidance on examples against rules before building this.
3. Build `PL-W8FL` and `PL-22T5`, and fold `PL-43GT` and `PL-JP8X` into point 1 where they overlap.

**Done when.** On three branches in a row, the text a fresh session writes is no longer than what it replaced, and the owner accepts it on the first read. That covers the docs, code comments and the reply.

**Generator check.** This is the head: a generator of the rewrites named in `root-cause-of`, across every kind of text, recorded live at the project owner's word (2026-11-03). `PL-W8FL`, `PL-22T5`, `PL-43GT` and `PL-JP8X` are parts of its fix.
