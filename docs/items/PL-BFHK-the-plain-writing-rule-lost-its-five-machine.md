---
id: PL-BFHK
title: The plain-writing rule lost its five machine-writing patterns in PL-J1ZM; restore them as positive instructions with no bad examples, as Anthropic's and OpenAI's prompting guides recommend
priority: P2
effort: S
status: untriaged
classes: defect
feature: prose-quality
touches: .claude/rules/plain-writing.md, docs/resident-instructions.md
deferred-from: v0.7.0 - its problem is new since the freeze and no release schedules it, so it is deferred on the terms of § "Deferring to the next gate"; not safety or science
added: 2026-11-14
payoff: a session writing prose is told what to write in place of each of the five kinds of padding, in the form the prompting guides say works best
verify: grep -q 'State the claim directly' .claude/rules/plain-writing.md && grep -q 'Give separate points their own structure' .claude/rules/plain-writing.md && ! grep -q 'A contrast nobody claimed' .claude/rules/plain-writing.md
---

**Problem.** `PL-J1ZM` (#2119, merged 2026-11-14) deleted the list of five
machine-writing patterns from `.claude/rules/plain-writing.md`: a tautological
aside, a contrast nobody claimed, narration about the text itself, a defensive
scope statement, and a table cell or paragraph grown into an essay. The list
named each fault and showed a bad sentence for it, with one before-and-after
example from `docs/MODEL.md`.

**The ask** (project owner, 2026-11-14): "If we can convert them to a form
Anthropic recommends then do it. If it's not recommend to have a don't do this
example then we shouldn't. Does anyone recommend doing that? Did we do any
research before we implemented the negative examples?"

**What the sources say, each read on 2026-11-14.** Anthropic's three pages were
fetched as Markdown and each quotation below was checked against the saved
copy. The other pages were read by a fetch agent.

- Anthropic, "Prompting best practices", § "Control the format of responses":
  "Tell Claude what to do instead of what not to do", with the pair
  "Instead of: 'Do not use markdown in your response'" and "Try: 'Your response
  should be composed of smoothly flowing prose paragraphs.'" § "Use examples
  effectively": "Examples are one of the most reliable ways to steer Claude's
  output format, tone, and structure", made "Relevant", "Diverse" and
  "Structured". The same page shows that a reason helps: "Claude can generalize
  from the explanation."
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices
- Anthropic, "Prompting Claude Sonnet 5", § "Response length and verbosity":
  "If you see specific kinds of verbosity (such as over-explaining), you can add
  additional instructions in your prompt to prevent them. Positive examples
  showing how Claude can communicate with the appropriate level of concision
  tend to be more effective than negative examples or instructions that tell
  the model what not to do."
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-sonnet-5
- Anthropic, "Prompting Claude Fable 5", § "Strong instruction following":
  "A short brevity instruction is as effective as listing each pattern".
  https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5
- OpenAI, "Best practices for prompt engineering with the OpenAI API", point 7:
  "Instead of just saying what not to do, say what to do instead."
  https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api
- Google, "Prompt design strategies", § "Constraints": "You can tell the model
  what to do and not to do." It takes no side, and recommends examples of the
  wanted output only. https://ai.google.dev/gemini-api/docs/prompting-strategies
  A sentence often attributed to Google, that an example of a pattern to follow
  works better than one of an anti-pattern to avoid, was not found on any
  current Google page; only secondary sites quote it, so it is not relied on.
- Jang, Ye and Seo, arXiv:2209.12711 (2022), abstract: "all LM types perform
  worse on negated prompts as they scale". García-Ferrero et al.,
  arXiv:2310.15941 (2023), abstract: LLMs "struggle with negative sentences".
  Both test older models on classification tasks, not writing style.
- Chia et al., "Contrastive Chain-of-Thought Prompting", arXiv:2311.09277
  (2023), abstract: provides "both valid and invalid reasoning demonstrations".
  This is the one source found that recommends showing a wrong example. It is
  for reasoning tasks, with each invalid example paired with a valid one.

So no vendor guide recommends showing a model a bad example of style, and
Anthropic and OpenAI both recommend saying what to do instead. Anthropic's own
"Less effective / More effective" pairs teach the person writing a prompt; the
page does not put the "Less effective" text into a prompt.

**What the project researched before.** `PL-ZT47` added the five patterns on
2026-11-02 (#1943) from the owner's reading of `docs/MODEL.md` and phrase counts
in it. Its brief cites no prompt-engineering source. `PL-8ZTQ`'s sources
(2026-10-17, `/mnt/project-files/v0.6.0/plain-writing/sources.md`) read
Anthropic's best-practices page but quoted only its advice on examples and on
matching prompt style; it recorded nothing on negative instructions.
`PL-J1ZM` read the Sonnet 5 and Fable 5 pages on 2026-11-11 and quoted both
sentences above, and deleted the list on that evidence and on four writing
tests that showed the rule changing nothing.

**What this item does.** Points 7 to 11 of the rule now state each pattern as
what to write, with one sentence of reason, and show no bad example:

1. Tautological aside: point 7, "Give each clause a fact that the rest of its
   sentence does not already state."
2. Contrast nobody claimed: point 8, "State the claim directly."
3. Narration about the text: point 9, "Write about the subject."
4. Defensive scope statement: point 10, "Say what the text relies on."
5. Essay in a table cell: point 11, "Give separate points their own
   structure."

The copy editor's checklist (`.claude/agents/copy-editor.md`) still names the
five faults. That is left as it is: a reviewer looks for faults, and the
guidance above is about instructions to a writer.

The rule's other bad examples are a separate question for the owner,
recorded in `PL-Q89B` with a recommendation.
