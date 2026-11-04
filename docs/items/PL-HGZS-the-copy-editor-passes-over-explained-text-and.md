---
id: PL-HGZS
title: The copy editor passes over-explained text and lengthens it: on PL-SP6H it kept a 250-word model-specification paragraph's derivation whole, made a 539-word reply one word longer and a pull request body 12 words longer, and six second-pass rewrites added 14 to 78 words each, because it asks whether each sentence is clear and each fact present, never whether the reader needs the fact; the owner then judged all of it too verbose
priority: P1
effort: M
status: ready
classes: defect
feature: copy-editor
touches: .claude/agents/copy-editor.md, docs/prose-review, tools/rejected_prose.py
deferred-from: v0.7.0 - a workflow-lane generator, ranked by its generator tier rather than by the gate
added: 2026-11-04
payoff: a passage the copy editor passes is one its reader can act on without padding, so the rewrites it reviews stop growing
verify: grep -qi 'do without' .claude/agents/copy-editor.md
root-cause-of: PL-HRPK, PL-PS5H, PL-XBJ3, PL-XT53, PL-YVL0
generator: live - the copy editor reviews every rewrite, and its only cut keeps every fact, so each rewrite it passes can grow
misread: that a passage the copy editor passed is plain enough for its reader
---

**Problem.** The copy editor passes over-explained text and lengthens it: on PL-SP6H it kept a 250-word model-specification paragraph's derivation whole, made a 539-word reply one word longer and a pull request body 12 words longer, and six second-pass rewrites added 14 to 78 words each, because it asks whether each sentence is clear and each fact present, never whether the reader needs the fact; the owner then judged all of it too verbose

**Checked 2026-11-04.** `.claude/agents/copy-editor.md` asks four questions of each passage. Questions 1 and 3 ask which words the reader would not know and what is missing, so both add. Question 4, its only cut, allows a cut only "with every fact kept", so a fact the reader does not need can only move to another reader's place. A reply or a clinician's paragraph has no such place. No question asks which facts the reader can do without. `docs/prose-review/gold/` holds no passage, so the review's test set has no case where it must cut.

**Why it matters.** Every rewrite of the model specification and every long reply goes through the copy editor, and a pass is taken as proof that the text is plain. The owner judged three passed texts too verbose on 2026-11-04.

**Decision** (project owner, 2026-11-04): the copy editor is a root cause that must be fixed and stress-tested before wide use. Rewrites unrelated to testing it are blocked until then, and this item is the highest priority. It is the copy-editor half of `PL-J1ZM`'s fix, split out on the owner's order.

**Done when** (revised 2026-11-04, after two reviews by the owner). The copy editor edits like a professional technical copy editor. Verbose text comes back concise and clear, as long as its reader needs. Good text comes back nearly unchanged. Every fact the reader needs stays. The owner calls it alpha. It is built in three steps:

1. **Research the craft.** Find how professional technical editors work, from published sources, and write what applies into `.claude/agents/copy-editor.md` with citations. Start from Einsohn and Schwartz, *The Copyeditor's Handbook* (4th ed., 2019); Rude and Eaton, *Technical Editing* (5th ed., 2011); Van Buren and Buehler, *The Levels of Edit* (JPL Publication 80-1, 1980); the Federal Plain Language Guidelines (2011); the Google developer documentation style guide; and Williams and Bizup, *Style: Lessons in Clarity and Grace*.
2. **Debug on the repository's own text, one section at a time.** Run the copy editor on one section, judge its edit as a professional editor would, find why any edit falls short, fix the instructions and rerun. Then take the next section. Include good sections, which it should leave nearly alone. Start with the five sections in `root-cause-of`, and stop when five sections in a row need no fix. Record each section's result and fix in this item. The edits stay in scratch. Those sections' own items apply them once the copy editor is back.
3. **Confirm on sections it was not tuned on.** A separate judge, run blind, compares the originals with the edits. No single count, such as words, decides a verdict.

The session judges throughout, and the owner does not review edits (project owner, 2026-11-04: "That's what you are for. You are the copy editor"). The copy editor returns to use only when the owner agrees (`PL-HJFX`). Two earlier forms of this paragraph, a fixed stress test and then a 20-passage set the owner would sample, were superseded the same day.

**Generator check.** This item is a head: the copy editor reviews every rewrite, and the five rewrites in `root-cause-of` wait on it. It is a second head beside `PL-J1ZM`, whose misread fact is what a reader can do without; this one is that a copy editor pass proves the text plain.
