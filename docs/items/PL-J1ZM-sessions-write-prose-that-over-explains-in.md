---
id: PL-J1ZM
title: Sessions write prose that over-explains, in every kind of text they write: each writing rule adds something a text must carry (a reason for each value, what changing it would do, the test that holds it, its provenance) and none says what the reader can do without, so docs, docstrings, the interface, item briefs, pull requests and replies each need rewrites, and each later change grows them again
priority: P1
effort: M
status: ready
classes: defect
feature: reader-first-prose
touches: .claude/rules/plain-writing.md, .claude/rules/instruction-writing.md, docs/prose-review/prompt.md, docs/prose-review/gold, tools/new_prose.py, .claude/skills/docket/modes/close-out.md, docs/dead-ends.md, docs/items/PL-9331-make-docs-model-md-assumptions-known.md, docs/items/PL-BSYT-apply-the-prose-review-s-rewrites-of-four-docs.md, docs/items/PL-J37P-make-docs-model-md-displayed-precision-readable.md, docs/items/PL-PS5H-make-docs-model-md-minimum-displayed-outputs-up.md, docs/items/PL-XBJ3-make-docs-model-md-the-chart-s-hover-readout.md, docs/items/PL-XT53-make-docs-model-md-the-control-input-timeline.md, docs/items/PL-YVL0-make-docs-model-md-reset-behavior-through.md
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
2. Give the writer examples, not only the reviewer. `docs/prose-review/gold/` is empty. Fill it with paragraphs the owner approves, starting with the accepted `PL-ZDZ0` paragraph, and print them to the writing session before it drafts. Check published prompting guidance on examples against rules before building this. [superseded 2026-11-04: the examples go to the copy editor, not to writers, per Question 2's answer]
3. Build `PL-W8FL` and `PL-22T5`, and fold `PL-43GT` and `PL-JP8X` into point 1 where they overlap.

**Done when.** On three branches in a row, the text a fresh session writes is no longer than what it replaced, and the owner accepts it on the first read. That covers the docs, code comments and the reply. [superseded 2026-11-04: no word target, per Question 1's answer]

**Done when** (2026-11-04). On three branches in a row, every cut the copy editor makes carries its reason, every passage that grew names in its pull request the facts its added words carry, and the owner accepts the text on the first read. That covers the docs, code comments and a reply.

**Generator check.** This is the head: a generator of the rewrites named in `root-cause-of`, across every kind of text, recorded live at the project owner's word (2026-11-03). `PL-W8FL`, `PL-22T5`, `PL-43GT` and `PL-JP8X` are parts of its fix.

## Design round, 2026-11-04

**Question 1. Which design fixes the generator?** **Recommendation:** one design in four parts, each replacing something rather than adding to it.

1. **A subtractive rule leads `.claude/rules/plain-writing.md`.** "Write what the reader needs to act on, and stop. Put what they see first, then what it means for them, then why, only where they act on the why. Move each reason, derivation, test name and piece of history to the developer note or the item, or cut it." It replaces three things: the paragraph "Before you write a paragraph, decide what its reader needs", the clinician-text half of "Give a chosen value its reason from a record" (which then applies only to the developer note), and "Most sentences should be under 25 words" (`PL-43GT`). It also says to keep one line of reasoning in one sentence where it fits (`PL-43GT`).
2. **A copy-editor agent replaces the close-out prose review.** It is `.claude/agents/copy-editor.md`, started without the resident instructions so each run starts small. It reads whole passages, from heading to heading (`PL-22T5`, `PL-JP8X`). It cuts a sentence, or words in one, only for one of three reasons: it repeats a fact another sentence already gives, it uses more words than its fact needs, or its fact belongs to another reader and moves to the developer note or the item. It returns each cut with its reason, and the counts before and after as a measurement. The writer reviews the reasons. Its edits apply by default. The writer reverts one only where it lost or changed a value, unit, condition, identifier or citation, and reports how many it reverted. Its prompt moves from `docs/prose-review/prompt.md` into the agent file, which becomes its one home, and the test set in `docs/prose-review/` tests it.
3. **It covers every kind of text, each at the moment that text is finished.** Files a branch changed (docs, docstrings, comments, interface strings of 30 words or more, rules, skills, item briefs) go through it at close-out, on every branch, from `tools/new_prose.py` widened to print whole passages with their before-and-after counts. The pull request title and body go through it before the pull request is marked ready, because the squash merge makes them the commit on `main`. A reply to the owner goes through it when it is a decision request or runs over 150 words: the session writes the draft to its scratchpad, runs the copy editor, and sends the result. In a reply the copy editor keeps each decision stated in full, with what it decides and the recommendation. It never shortens one to a pointer at an earlier reply. On 2026-11-04 this session's closing block twice said "approve, change or reject the four-part design in my last reply", and the owner had to ask what the decision was.
4. **No word target** (project owner, 2026-11-04: "I want efficient, clear and cohesive writing (eliminate verbose and redundant prose) not necessarily an arbitrary word count"). A target can be met by cutting a fact the reader needs. The prototype, given 110 words, cut "above zero" from the condition for `<0.01 ×MAC`. Models do follow short length instructions, so a target would be met: LIFEBench found that "most models reasonably follow short-length instructions but deteriorate sharply beyond a certain threshold" (Zhang et al. 2025, arXiv:2505.16234). One count stays, as a flag rather than a limit: a changed passage that grows must have its pull request name the facts the added words carry, because growth with no new fact is this generator's mark. Rule 13's "one screen" in `.claude/rules/instruction-writing.md` is left as it stands. The draft prompt's last step, "meet the target or name the fact that pushes it over", becomes "give each cut its reason".

**What it costs.** One copy-editor run per branch, one per pull request, and one per long reply. Without the resident instructions a run should start far below the 80,000 tokens `PL-PRCS` measured for a general-purpose reviewer; the first build measures it. Fix branches show larger diffs, limited to the passage the fix is in.

**What no check enforces.** Replies. Hooks do not run in project threads (`PL-D1FD`), and a stop hook cannot rewrite a reply already sent. The rule is resident in `.claude/rules/instruction-writing.md`, and the Done-when measures it.

**Build order.** `PL-W8FL` first, because the documentation check rejects a clinician paragraph whose tests sit in the developer note, so no design can land without it. Then the rule (part 1, with `PL-43GT`), then the copy editor and the passage unit (parts 2 to 4, with `PL-22T5` and `PL-JP8X`).

**Prototype run, 2026-11-04.** The draft copy-editor prompt ran once in a fresh `general-purpose` agent, at the session's effort, on two passages. It cut the MAC passage of § "Displayed precision" from 277 words (the passage on `main` since `PL-ZDZ0` merged in #1992) to 110, and a 404-word reply to the owner to 150. It made three errors that applying by default would have published. It wrote "A MAC value below one step shows as `<0.01 ×MAC`", but `format_mac_multiple` marks only a positive value, so zero still reads `0.00`. It rewrote "have no test yet (`PL-19W8`)" as "are untested", which the documentation check does not read as a declaration. It dropped the reply's effort-trial line, which the session-start hook requires in a first reply. So part 2 also needs a script that lists every number, name in backticks, item id and "no test yet" form that an edit removed, for the writer to confirm before the edit lands. That is decidable, so it goes in `tools/new_prose.py`. The run took 11 minutes and 169,720 tokens, with the resident instructions loaded.

**Answer** (project owner, 2026-11-04, ratified, over keeping the close-out prose review advisory and adding rules to it): build the design above, in the build order above. Part 4, no word target, is the owner's own (project owner, 2026-11-04).

**Question 2. Should writers be shown owner-approved example paragraphs?** **Recommendation:** show the examples to the copy editor, not to writers, and only once three pairs of different kinds exist. Each pair is a before and an after the owner approved, with one sentence saying why the after is better. Until there are three, the rule works alone.

- Published guidance pairs examples with rules, and does not offer them instead of rules. Anthropic: "Examples are one of the most reliable ways to steer Claude's output format, tone, and structure", in "3–5 examples", "Diverse" enough that "Claude doesn't pick up unintended patterns" (https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices). OpenAI: "ensure that any important behavior demonstrated in your examples are also cited in your rules" (https://cookbook.openai.com/examples/gpt4-1_prompting_guide).
- Models copy an example's form and length more than its content (Min et al. 2022, arXiv:2202.12837; Schoch and Ji 2025, arXiv:2502.06653). One MAC paragraph shown to every writer would pull docstrings and replies toward its shape. Examples with a reason beat examples alone (Lampinen et al. 2022, arXiv:2204.02329).
- The copy editor's text is what gets published, so the examples pay off there. The two before-and-afters in this round are the first two pairs if the owner approves them, with the effort-trial line the prototype dropped put back into the reply's after first. They go in `docs/prose-review/examples/`, apart from `gold/`, whose entries the owner names gold in those words.

**Answer** (project owner, 2026-11-04, ratified, over printing approved paragraphs to the writing session): the examples go to the copy editor only, once three pairs of different kinds exist. The two pairs below are the first two (project owner, 2026-11-04, ratified, over writing new pairs). They move to `docs/prose-review/examples/` when the copy editor is built, and this item holds them until then.

**Pair 1, the MAC passage of `docs/MODEL.md` § "Displayed precision".** Why the after is better: it gives the clinician the three per-agent steps and both display behaviours in 54 words, and moves the derivation and every test name to the developer note.

Before (277 words):

```text
**The MAC resolution is derived from this one, not chosen beside it.** A MAC
multiple is a percent divided by the agent's own `mac_percent`. So the
resolution above already fixes how finely the quotient is known. Stating a
second resolution independently would mean re-deriving two numbers whenever
this one is re-measured. The rule is one line: **the finest power of ten that
is nowhere finer than the percent resolution converted into MAC.** That
conversion is agent-specific. Converted, 0.01 percentage points is 0.005 MAC
for sevoflurane, 0.0083 for isoflurane and 0.0017 for desflurane. So the
binding agent is isoflurane at 0.0083 MAC, and **0.01 MAC** is the finest power
of ten at or above it.
`test_the_mac_resolution_is_derived_from_the_percent_resolution` repeats this
arithmetic for every shipped agent.

The smallest change the MAC readout can show is therefore 0.02 percentage points
of sevoflurane, 0.012 of isoflurane and 0.06 of desflurane, never less than the
percent readout's. The two readouts round separately, so the MAC value can
occasionally change while the percent stays the same. The three per-agent
figures have no test yet (`PL-19W8`).
<!-- not-restated: 0.06 -->

The below-resolution form applies to the MAC line for the same reason it
applies to the percent line, and it matters more there, not less. A
compartment clears 0.01 MAC later than it clears 0.01 percentage points. So
`0.00 ×MAC` beneath a percent line that already shows the compartment filling
would make the two readouts contradict each other. `<0.01 ×MAC` states what is
known, and `test_format_mac_multiple_marks_a_value_below_the_resolution` holds
that form. The derivation test named above re-runs the derivation against
every shipped agent. So adding an agent or changing the percent resolution
fails there rather than silently over-claiming.
```

After (120 words):

```text
The MAC readout's step, 0.01 MAC, is 0.02 percentage points of sevoflurane,
0.012 of isoflurane and 0.06 of desflurane, never finer than the percent
readout's. The readouts round separately, so the MAC value can occasionally
change while the percent does not. A MAC value above zero but below one step
shows as `<0.01 ×MAC`.
<!-- not-restated: 0.06 -->

**For developers.** Dividing the percent step by the smallest `mac_percent`,
isoflurane's, gives 0.0083 MAC. The MAC step is that, rounded up to a power of
ten. `test_the_mac_resolution_is_derived_from_the_percent_resolution` repeats
this arithmetic for every shipped agent, so a new agent or percent step that
would over-claim fails there.
`test_the_mac_digit_can_move_alone_at_a_rounding_boundary` checks the second
sentence, and `test_format_mac_multiple_marks_a_value_below_the_resolution`
the `<0.01 ×MAC` form. The three per-agent figures have no test yet (`PL-19W8`).
```

**Pair 2, a reply to the owner.** Why the after is better: it says why the session stopped and asks the two decisions in about 160 words, and drops history and session status that no decision depended on.

Before (404 words):

```text
I've stopped. This session wrote nothing: it made no claim, no branch and no file edits. It runs in the effort trial's xhigh arm.

**Sessions on this work right now**

- **"Prose generation clarity issues"** is running and overlaps directly. It filed PL-J1ZM (the live generator for over-explaining prose) in #2000, which has merged. It also wrote the prompt this session was given, and it found that prompt too narrow too. Its current task is "Rescope PL-J1ZM to all prose and check the item store", so it is widening the generator from `docs/MODEL.md` to every kind of prose a session writes. It will probably edit PL-J1ZM's item file. A design round started here would then work from a stale brief and conflict with it at merge.
- **PL-ZDZ0** (the fix to the false MAC-digit sentence in § "Displayed precision") is idle and waiting for you. Its last line asks you to reply "Merge it" to merge #1992, or to say what to change in the MAC sentence. #1992 is open. It also carries PL-JP8X (the prose review never compares new text with the text it replaced) and PL-BSYT's status change. Until it merges, PL-JP8X exists only on that branch.
- PL-CJGH and PL-RKRG are idle on unrelated apparatus items. Nothing else touches PL-W8FL, PL-22T5 or PL-43GT. None of those three is claimed on any branch.

**What I'd already found, so the next prompt doesn't have to repeat it**

- Main's MAC passage is 381 words. ZDZ0's branch brings it to about 318 by folding its middle paragraphs. The two paragraphs on either side are unchanged from main.
- The other session's draft of the ~110-word target puts a clinician paragraph first and the derivation in a developer note. It notes that the documentation check would reject that draft until PL-W8FL (the check that forces test names into clinician paragraphs) is fixed. That makes PL-W8FL the right first build under any design.

**What needs you**

1. Send the new prompt. If the rescope session is still running when you do, either let it finish its PL-J1ZM edit first or tell me to work from its branch. Otherwise the two sessions will edit the same item file.
2. Separately, in the PL-ZDZ0 session: decide whether #1992 merges as it stands. Its session and the rescope session both recommend yes, because it corrects the one false clinical claim and the long text around it is main's old wording.
```

After:

```text
I stopped before writing anything: "Prose generation clarity issues" is widening PL-J1ZM (the live generator for over-explaining prose) to all prose. Starting the design round now risks a stale brief and a merge conflict. This session runs in the effort trial's xhigh arm.

No other session or claim touches PL-W8FL (the check that forces test names into clinician paragraphs), PL-22T5 or PL-43GT. Fixing that check comes first under any design: it would reject the other session's ~110-word draft.

**What needs you**

1. Send the new prompt once "Prose generation clarity issues" finishes editing PL-J1ZM (the generator), or have me work from its branch.
2. In the PL-ZDZ0 session (the MAC-sentence fix), reply "Merge it" to merge #1992, or say what to change in that sentence. Both other sessions recommend merging: it corrects the one false clinical claim, and the rest is main's old wording. It also holds the only copy of PL-JP8X (the prose review never compares new text with old).
```
