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

## Design round, 2026-11-04

**Question 1. Which design fixes the generator?** **Recommendation:** one design in four parts, each replacing something rather than adding to it.

1. **A subtractive rule leads `.claude/rules/plain-writing.md`.** "Write what the reader needs to act on, and stop. Put what they see first, then what it means for them, then why, only where they act on the why. Move each reason, derivation, test name and piece of history to the developer note or the item, or cut it." It replaces three things: the paragraph "Before you write a paragraph, decide what its reader needs", the clinician-text half of "Give a chosen value its reason from a record" (which then applies only to the developer note), and "Most sentences should be under 25 words" (`PL-43GT`). It also says to keep one line of reasoning in one sentence where it fits (`PL-43GT`).
2. **A copy-editor agent replaces the close-out prose review.** It is `.claude/agents/copy-editor.md`, started without the resident instructions so each run starts small. It reads whole passages, from heading to heading, with each passage's words before and a target in words (`PL-22T5`, `PL-JP8X`). Its edits apply by default. The writer reverts one only where it lost or changed a value, unit, condition, identifier or citation, and reports how many it reverted. Its prompt moves from `docs/prose-review/prompt.md` into the agent file, which becomes its one home, and the test set in `docs/prose-review/` tests it.
3. **It covers every kind of text, each at the moment that text is finished.** Files a branch changed (docs, docstrings, comments, interface strings of 30 words or more, rules, skills, item briefs) go through it at close-out, on every branch, from `tools/new_prose.py` widened to print whole passages with their before-and-after counts. The pull request title and body go through it before the pull request is marked ready, because the squash merge makes them the commit on `main`. A reply to the owner goes through it when it is a decision request or runs over 150 words: the session writes the draft to its scratchpad, runs the copy editor, and sends the result. In a reply the copy editor keeps each decision stated in full, with what it decides and the recommendation. It never shortens one to a pointer at an earlier reply. On 2026-11-04 this session's closing block twice said "approve, change or reject the four-part design in my last reply", and the owner had to ask what the decision was.
4. **Length targets.** A changed file passage may not grow unless the pull request says what the added words buy. The copy editor states its own target from the facts the reader needs, and meets it or names the fact that pushes it over. A decision request or status reply fits one phone screen, about 150 words with the closing block, which replaces rule 13's undefined "one screen" in `.claude/rules/instruction-writing.md`. A longer reply, such as a design round, is copy-edited to the editor's own target.

**What it costs.** One copy-editor run per branch, one per pull request, and one per long reply. Without the resident instructions a run should start far below the 80,000 tokens `PL-PRCS` measured for a general-purpose reviewer; the first build measures it. Fix branches show larger diffs, limited to the passage the fix is in.

**What no check enforces.** Replies. Hooks do not run in project threads (`PL-D1FD`), and a stop hook cannot rewrite a reply already sent. The rule is resident in `.claude/rules/instruction-writing.md`, and the Done-when measures it.

**Build order.** `PL-W8FL` first, because the documentation check rejects a clinician paragraph whose tests sit in the developer note, so no design can land without it. Then the rule (part 1, with `PL-43GT`), then the copy editor and the passage unit (parts 2 to 4, with `PL-22T5` and `PL-JP8X`).

**Prototype run, 2026-11-04.** The draft copy-editor prompt ran once in a fresh `general-purpose` agent, at the session's effort, on two passages. It cut the MAC passage of § "Displayed precision" from 277 words (the passage on `main` since `PL-ZDZ0` merged in #1992) to 110, and a 404-word reply to the owner to 150. It made three errors that applying by default would have published. It wrote "A MAC value below one step shows as `<0.01 ×MAC`", but `format_mac_multiple` marks only a positive value, so zero still reads `0.00`. It rewrote "have no test yet (`PL-19W8`)" as "are untested", which the documentation check does not read as a declaration. It dropped the reply's effort-trial line, which the session-start hook requires in a first reply. So part 2 also needs a script that lists every number, name in backticks, item id and "no test yet" form that an edit removed, for the writer to confirm before the edit lands. That is decidable, so it goes in `tools/new_prose.py`. The run took 11 minutes and 169,720 tokens, with the resident instructions loaded.

**Question 2. Should writers be shown owner-approved example paragraphs?** **Recommendation:** show the examples to the copy editor, not to writers, and only once three pairs of different kinds exist. Each pair is a before and an after the owner approved, with one sentence saying why the after is better. Until there are three, the rule works alone.

- Published guidance pairs examples with rules, and does not offer them instead of rules. Anthropic: "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure", in "3–5 examples", "Diverse" enough that "Claude doesn't pick up unintended patterns" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). OpenAI: "ensure that any important behavior demonstrated in your examples are also cited in your rules" (https://cookbook.openai.com/examples/gpt4-1_prompting_guide).
- Models copy an example's form and length more than its content (Min et al. 2022, arXiv:2202.12837; Schoch and Ji 2025, arXiv:2502.06653). One MAC paragraph shown to every writer would pull docstrings and replies toward its shape. Examples with a reason beat examples alone (Lampinen et al. 2022, arXiv:2204.02329).
- The copy editor's text is what gets published, so the examples pay off there. The two before-and-afters in this round are the first two pairs if the owner approves them, with the effort-trial line the prototype dropped put back into the reply's after first. They go in `docs/prose-review/examples/`, apart from `gold/`, whose entries the owner names gold in those words.
