---
id: PL-HGZS
title: The copy editor passes over-explained text and lengthens it: on PL-SP6H it kept a 250-word model-specification paragraph's derivation whole, made a 539-word reply one word longer and a pull request body 12 words longer, and six second-pass rewrites added 14 to 78 words each, because it asks whether each sentence is clear and each fact present, never whether the reader needs the fact; the owner then judged all of it too verbose
priority: P1
effort: M
status: ready
classes: defect
feature: prose-quality
touches: .claude/agents/copy-editor.md, docs/prose-review, tools/rejected_prose.py
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

[superseded 2026-11-04: the owner found it too narrow, and the revised form follows] **Done when.** The copy editor can cut a fact its reader does not need, naming the reason. A stress test runs it on passages the owner judged too verbose on 2026-11-04 and on passages the owner accepted. It must cut the first to what the owner accepted and keep the second. The verbose passages are on `#2024`'s branch: the 250-word delivered-total paragraph of `docs/MODEL.md` § "Displayed precision" at `e3834f81c`, and the cut version at `14387f045`. The test runs in `make check`. Only then do the blocked rewrites resume.

**Done when** (revised 2026-11-04, after the owner's review). The copy editor edits like a professional technical copy editor. Given verbose or badly written text, it returns text that is concise and clear, as long as its reader needs and no longer. Given good text, it changes little. It keeps every fact the reader needs.

The building session judges this, not the owner:

1. A test set of at least 20 passages across the kinds the copy editor reads: model-specification paragraphs, docstrings, replies and pull request bodies. Some are verbose, some already good, and the texts the owner found too verbose on 2026-11-04 are among them.
2. A separate judge, run blind, compares each original with its edit. It asks which keeps every needed fact, which reads more like professional technical writing, and which is shorter without loss. No single count, such as words, decides a verdict. The judge's standard draws on published guides: the Federal Plain Language Guidelines (plainlanguage.gov, 2011), the Google developer documentation style guide, and Williams and Bizup, *Style: Lessons in Clarity and Grace*.
3. The session revises the copy editor and reruns the set until its edits win on most passages and make no good passage worse. It runs at least five such rounds before showing the owner anything.
4. The owner then reads a few before-and-after pairs. Passages the owner accepted earlier are a floor, not a target.

The copy editor returns to use only after the owner agrees (`PL-HJFX`).

**Generator check.** This item is a head: the copy editor reviews every rewrite, and the five rewrites in `root-cause-of` wait on it. It is a second head beside `PL-J1ZM`, whose misread fact is what a reader can do without; this one is that a copy editor pass proves the text plain.
