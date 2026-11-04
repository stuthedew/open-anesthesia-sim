---
id: PL-HGZS
title: The copy editor passes over-explained text and lengthens it: on PL-SP6H it kept a 250-word model-specification paragraph's derivation whole, made a 539-word reply one word longer and a pull request body 12 words longer, and six second-pass rewrites added 14 to 78 words each, because it asks whether each sentence is clear and each fact present, never whether the reader needs the fact; the owner then judged all of it too verbose
priority: P1
effort: M
status: ready
classes: defect
feature: copy-editor
touches: .claude/agents/copy-editor.md, docs/prose-review, tools/rejected_prose.py, tools/new_prose.py, tests/unit/test_new_prose.py
added: 2026-11-04
payoff: a passage the copy editor passes is one its reader can act on without padding, so the rewrites it reviews stop growing
verify: grep -qi 'do without' .claude/agents/copy-editor.md && grep -q 'def section_report' tools/new_prose.py && grep -q '^## Judging edits blind' docs/prose-review/README.md
root-cause-of: PL-HRPK, PL-PS5H, PL-XBJ3, PL-XT53, PL-YVL0
generator: live - the copy editor reviews every rewrite, and its only cut keeps every fact, so each rewrite it passes can grow
misread: that a passage the copy editor passed is plain enough for its reader
---

**Problem.** The copy editor passes over-explained text and lengthens it: on PL-SP6H it kept a 250-word model-specification paragraph's derivation whole, made a 539-word reply one word longer and a pull request body 12 words longer, and six second-pass rewrites added 14 to 78 words each, because it asks whether each sentence is clear and each fact present, never whether the reader needs the fact; the owner then judged all of it too verbose

**Checked 2026-11-04.** `.claude/agents/copy-editor.md` asks four questions of each passage. Questions 1 and 3 ask which words the reader would not know and what is missing, so both add. Question 4, its only cut, allows a cut only "with every fact kept", so a fact the reader does not need can only move to another reader's place. A reply or a clinician's paragraph has no such place. No question asks which facts the reader can do without. `docs/prose-review/gold/` holds no passage, so the review's test set has no case where it must cut.

**Why it matters.** Every rewrite of the model specification and every long reply goes through the copy editor, and a pass is taken as proof that the text is plain. The owner judged three passed texts too verbose on 2026-11-04.

**Decision** (project owner, 2026-11-04): the copy editor is a root cause that must be fixed and stress-tested before wide use. Rewrites unrelated to testing it are blocked until then, and this item is the highest priority. It is the copy-editor half of `PL-J1ZM`'s fix, split out on the owner's order.

**Done when** (revised 2026-11-04, after two reviews by the owner). The copy editor edits like a professional technical copy editor. Verbose text comes back concise and clear, as long as its reader needs. Good text comes back nearly unchanged. Every fact the reader needs stays. It rewrites a paragraph where trimming is not enough, to remove verbosity and repetition. It also reads a whole section or document, so it finds a fact said twice in different paragraphs, or a passage in the wrong place (project owner, 2026-11-04). `tools/new_prose.py` now hands it one passage at a time, so it must also hand over the whole section. The owner calls it alpha. It is built in three steps:

1. **Research the craft.** Find how professional technical editors work, from published sources, and write what applies into `.claude/agents/copy-editor.md` with citations. Start from Einsohn and Schwartz, *The Copyeditor's Handbook* (4th ed., 2019); Rude and Eaton, *Technical Editing* (5th ed., 2011); Van Buren and Buehler, *The Levels of Edit* (JPL Publication 80-1, 1980); the Federal Plain Language Guidelines (2011); the Google developer documentation style guide; and Williams and Bizup, *Style: Lessons in Clarity and Grace*.
2. **Debug on the repository's own text, one section at a time.** Run the copy editor on one section, judge its edit as a professional editor would, find why any edit falls short, fix the instructions and rerun. Then take the next section. Judge each section as a whole as well as paragraph by paragraph, and include some whole documents. Include good sections, which it should leave nearly alone. Start with the five sections in `root-cause-of`, and stop when five sections in a row need no fix. Record each section's result and fix in this item. The edits stay in scratch. Those sections' own items apply them once the copy editor is back.
3. **Confirm on sections it was not tuned on.** A separate judge, run blind, compares the originals with the edits. No single count, such as words, decides a verdict.

The session judges each edit (project owner, 2026-11-04: "That's what you are for. You are the copy editor"). Once a debug section's edit is tentatively final, the session also sends it to the owner with the text before and after, what was wrong, and what it changed and why (project owner, 2026-11-04 20:42Z: "run debug sections by me once you have a tentative finalized version"). It starts the next section without waiting for his verdict, as his brief at 20:17Z asked, and a verdict that finds a fault reopens that section and the count of five. The copy editor returns to use only when the owner agrees (`PL-HJFX`). Two earlier forms of this paragraph, a fixed stress test and then a 20-passage set the owner would sample, were superseded the same day.

**Generator check.** This item is a head: the copy editor reviews every rewrite, and the five rewrites in `root-cause-of` wait on it. It is a second head beside `PL-J1ZM`, whose misread fact is what a reader can do without; this one is that a copy editor pass proves the text plain.

**Debug record.** Each line gives a section, the runs, what was wrong with the edit and the fix to `.claude/agents/copy-editor.md`. The runs and their full notes are in the project files under `v0.7.0/copy-editor-alpha/` (`state.md`). A section the instructions were tuned on does not count toward the five.

1. `docs/MODEL.md` § "How this document is held to the tree" (`PL-HRPK`), tuned, runs 1 to 11. Runs 1 to 3 dropped the one fact the clinician needed and split the note for developers; fixed by leaving the needed sentence behind a move, one note per section, and a first paragraph that says what the section means. The owner judged run 3 "still very awkward" (20:54Z): it trimmed but kept sentence shapes and coined terms. Fixed by rewriting from facts, no clause between subject and verb, listing each unfamiliar word kept, and moving a sentence built on one. Run 7 was "better but still awkward" (21:09Z): the clauses are rules for writers; fixed by giving the clinician what a rule guarantees, everyday word senses and a separate sentence pass. Run 9 was "way better" (21:21Z), and he asked for examples of abstract terms, added for run 10. His question "where is clause 3?" (21:28Z) found a bare numbered cross-reference; fixed by writing the thing instead (run 11). The clinician's part went from 1,053 to about 235 words with every way of backing a number kept. It found `PL-6VBY`.
2. § "What this list requires once the layout is the reader's" (`PL-PS5H`), tuned, runs 1 to 5. Run 1 moved decision history into the note for developers and left narration; fixed by sending history to its item, keeping a short owner-decision tag where no item holds it, and checking the five patterns. It raised three good queries.
3. § "MAC multiples as a display unit" (`PL-PS5H`), runs 1 to 6. It found two errors in the section, filed as `PL-GW26`. Run 5 repeated a word in neighbouring sentences and used "divisor" before saying what it is; fixed by a neighbour check in the self-check and defining a term where it first appears.
4. § "The chart's time base" (`PL-PS5H`), runs 1 to 5. Runs 1 and 4 needed no fix. Run 1 changed the lead-in that `PL-RCTQ`'s verify greps for, which the rewrite item must handle.
5. § "MAC-awake as a chart reference" (`PL-PS5H`), runs 1 to 5. Run 4 called one band edge a "stroke" and a "rule", and kept the original's "one measurement" for a run of the model; fixed by one name per thing and keeping "measured" for patient or instrument data.
6. § "The chart's hover readout: what the tooltip may show" (`PL-XBJ3`), runs 1 and 2. Run 1's clinician part read well.
7. `README.md` § "What it is for", good text, runs 1 and 2. Run 1 made a light edit with one repeated word.
